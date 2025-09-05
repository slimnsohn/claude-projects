#!/usr/bin/env python3
import os
from datetime import datetime

# ===== CONFIG =====
PROJECTS_DIR = "/home/sammy/development/git/claude-projects"
IGNORE_DIRS = {"project-tutor", ".git", "__pycache__", "node_modules", ".idea", ".vscode"}
FILE_EXTENSIONS = {".py", ".js", ".ts", ".html", ".css", ".md", ".json", ".yaml", ".yml"}
SNAPSHOT_DIR = os.path.expanduser("~/tutor_snapshots")
# ==================

def collect_project_files():
    file_data = {}
    for root, dirs, files in os.walk(PROJECTS_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if os.path.splitext(file)[1].lower() in FILE_EXTENSIONS:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_data[full_path] = f.read()
                except Exception as e:
                    print(f"Skipping {full_path}: {e}")
    return file_data

def in_claude_code():
    # Detect if running inside Claude Code by checking a special env var
    return "CLAUDE_SANDBOX" in os.environ

def run_in_claude_mode(files):
    print("\n--- Claude Tutor Mode ---\n")
    print("Paste this into the next Claude Code message:\n")
    for path, content in files.items():
        print(f"=== {path} ===\n{content}\n")

def run_in_local_mode(files):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(SNAPSHOT_DIR, f"project_snapshot_{ts}.md")
    with open(filename, "w", encoding="utf-8") as f:
        for path, content in files.items():
            f.write(f"## {path}\n\n```plaintext\n{content}\n```\n\n")
    print(f"Snapshot saved to: {filename}")

if __name__ == "__main__":
    files = collect_project_files()
    if not files:
        print("No files found to process.")
    elif in_claude_code():
        run_in_claude_mode(files)
    else:
        run_in_local_mode(files)

