# VS Code Copilot Chat Recovery & Mapping Tool

A lightweight utility to decode VS Code's hidden `workspaceStorage` directory, map randomized folder hashes to real project names, and safely restore your GitHub Copilot chat history (e.g., when moving to a new MacBook).

## 🛑 The Problem
VS Code saves your local Copilot chat histories inside folders named with randomized, cryptic alphanumeric hashes (e.g., `3a8f9c2d1b...`). When you migrate data manually or restore a project from a backup like Time Machine, VS Code breaks the link to your chat histories because it generates a brand-new hash for your workspaces. Finding which chat belongs to which project manually is nearly impossible.

## 💡 The Solution
This tool scans your backed-up `workspaceStorage` directory, reads the internal metadata (`workspace.json`), and exports a clean mapping report. It tells you exactly which hash corresponds to which project, and whether that folder contains Copilot chat transcripts.

---

## 📂 Repository Contents
- `read_old_copilot_chat_sessions.py` — The core Python scanner and CSV exporter script.
- `workspace_transcripts.csv` — An example generated output file showing the mapping structure.

---

## 🚀 Step-by-Step Usage Guide

### 1. Run the Exporter
Execute the Python script in your terminal:
```bash
python3 read_old_copilot_chat_sessions.py
```

### 2. Respond to the Interactive Prompts
The script will ask you for three inputs:
- `Enter workspaceStorage path:` (e.g., `~/Downloads/Code/User/workspaceStorage/`)
- `Enter output CSV path:` (e.g., `./my_mapped_workspaces.csv`)
- `Filter rows by transcripts (all/yes/no) [all]:` (Type `yes` to only show projects that actually contain chats)

### 3. Review Your Map
Open the generated CSV file using your terminal or an app like Excel/Numbers to find your target project name and its corresponding old hash value:
```bash
open ./my_mapped_workspaces.csv
```

---

## ⚙️ Command Line Arguments (Skip Prompts)
For automated workflows or non-interactive runs, you can pass arguments directly to the script:

*   **Specify Input Path:**
    ```bash
    python3 read_old_copilot_chat_sessions.py --workspace-storage /path/to/backup/workspaceStorage
    ```
*   **Specify Output Path:**
    ```bash
    python3 read_old_copilot_chat_sessions.py --output /path/to/output.csv
    ```
*   **Filter Projects With Chats Only:**
    ```bash
    python3 read_old_copilot_chat_sessions.py --only-transcripts yes
    ```
*   **Full Non-Interactive One-Liner:**
    ```bash
    python3 read_old_copilot_chat_sessions.py \
      --workspace-storage ~/Downloads/Code/User/workspaceStorage \
      --output ./output.csv \
      --only-transcripts yes
    ```

---

## 🛠️ How to Restore Chats to Your New Mac (Best Practices)

Once your CSV map has identified the old hash folder holding your desired chat history, use these steps to link it back to your live VS Code installation.

### Step A: Identify the New Workspace Hash
1. Open your project folder in your new VS Code installation.
2. Open Copilot Chat, send a single **dummy test message**, and then **completely quit VS Code (`Cmd + Q`)**. *Crucial: If VS Code is open during restoration, it will overwrite your files.*
3. Find your new live hash folder by running this command to sort folders by recent activity:
   ```bash
   ls -lt ~/Library/"Application Support"/Code/User/workspaceStorage/ | head -n 5
   ```
   The folder at the very top of the list is your **New Hash Folder**.

### Step B: Copy the Copilot Transcripts
Using the **Old Hash** (found via your CSV map) and your **New Hash** (found in Step A), copy the old transcript files over to your live system:
```bash
cp -R /path/to/backup/workspaceStorage/<OLD_HASH>/GitHub.copilot-chat/transcripts/* \
  ~/Library/"Application Support"/Code/User/workspaceStorage/<NEW_HASH>/GitHub.copilot-chat/transcripts/
```

### Step C: Clear the Index Cache Database
VS Code caches history tracking in a local file named `state.vscdb`. You must remove it so VS Code is forced to scan and index your newly added transcripts:
```bash
rm ~/Library/"Application Support"/Code/User/workspaceStorage/<NEW_HASH>/state.vscdb
```

### Step D: Launch and Verify
Open VS Code. Your complete Copilot chat timeline will be beautifully restored and seamlessly bound to your active project workspace!
