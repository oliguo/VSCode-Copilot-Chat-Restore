#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path
from urllib.parse import unquote, urlparse


def normalize_project_path(value: str) -> str:
    text = value.strip()
    if text.startswith("file://"):
        parsed = urlparse(text)
        if parsed.path:
            text = parsed.path
    return unquote(text)


def extract_project_path(payload: dict) -> str:
    folder = payload.get("folder")
    if isinstance(folder, str) and folder.strip():
        return normalize_project_path(folder)

    workspace = payload.get("workspace")
    if isinstance(workspace, str) and workspace.strip():
        return normalize_project_path(workspace)

    if isinstance(workspace, dict):
        for key in ("folder", "path", "configPath", "id"):
            candidate = workspace.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return normalize_project_path(candidate)

    return "<missing>"


def collect_rows(workspace_storage: Path, only_transcripts: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for folder in sorted(workspace_storage.iterdir(), key=lambda p: p.name):
        if not folder.is_dir():
            continue

        workspace_json = folder / "workspace.json"
        if not workspace_json.is_file():
            continue

        project_path = "<missing>"
        try:
            payload = json.loads(workspace_json.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                project_path = extract_project_path(payload)
            else:
                project_path = "<invalid-json>"
        except Exception:
            project_path = "<invalid-json>"

        has_transcripts = (folder / "GitHub.copilot-chat" / "transcripts").is_dir()
        has_text = "Yes" if has_transcripts else "No"

        if only_transcripts != "all" and has_text.lower() != only_transcripts:
            continue

        rows.append([folder.name, project_path, has_text])

    return rows

def prompt_workspace_storage() -> Path:
    while True:
        raw = input("Enter workspaceStorage path: ").strip()
        if not raw:
            print("Path is required.")
            continue
        path = Path(raw).expanduser().resolve()
        if not path.is_dir():
            print(f"Directory not found: {path}")
            continue
        return path


def prompt_output_file() -> Path:
    while True:
        raw = input("Enter output CSV path: ").strip()
        if not raw:
            print("Path is required.")
            continue
        return Path(raw).expanduser().resolve()


def prompt_filter_mode() -> str:
    while True:
        raw = input("Filter rows by transcripts (all/yes/no) [all]: ").strip().lower()
        if not raw:
            return "all"
        if raw in {"all", "yes", "no"}:
            return raw
        print("Please enter all, yes, or no.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan VS Code workspaceStorage hash folders and export project path + "
            "GitHub Copilot transcript directory status to CSV."
        )
    )
    parser.add_argument(
        "--workspace-storage",
        default=None,
        help="Path to workspaceStorage directory",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path",
    )
    parser.add_argument(
        "--only-transcripts",
        choices=("all", "yes", "no"),
        default=None,
        help="Filter rows by transcript directory status",
    )
    args = parser.parse_args()
    if args.workspace_storage:
        workspace_storage = Path(args.workspace_storage).expanduser().resolve()
        if not workspace_storage.is_dir():
            raise SystemExit(f"workspaceStorage folder not found: {workspace_storage}")
    else:
        workspace_storage = prompt_workspace_storage()

    output_file = (
        Path(args.output).expanduser().resolve()
        if args.output
        else prompt_output_file()
    )

    only_transcripts = args.only_transcripts or prompt_filter_mode()

    rows = collect_rows(workspace_storage, only_transcripts)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["hash_folder", "real_project_path", "has_transcripts"])
        writer.writerows(rows)

    yes_count = sum(1 for row in rows if row[2] == "Yes")
    no_count = sum(1 for row in rows if row[2] == "No")
    print(f"CSV created: {output_file}")
    print(f"Rows: {len(rows)} (Yes: {yes_count}, No: {no_count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
