import os
import subprocess
from datetime import datetime

OUTPUT_DIR = "project-tutor/explanations"


def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        stdout=subprocess.PIPE,
        text=True,
    )
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def save_files_for_review(files):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"changes_{timestamp}.md")

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"# Code Changes – {timestamp}\n\n")
        for file in files:
            if not os.path.isfile(file):
                continue
            out.write(f"## {file}\n\n")
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            out.write("```python\n" if file.endswith(".py") else "```\n")
            out.write(content)
            out.write("\n```\n\n")

    print(f"Saved changes for review: {output_path}")


if __name__ == "__main__":
    files = get_changed_files()
    if files:
        save_files_for_review(files)
    else:
        print("No file changes detected.")
