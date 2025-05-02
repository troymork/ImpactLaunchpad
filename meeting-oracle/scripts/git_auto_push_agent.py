import subprocess
import time
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
POLL_INTERVAL = 10  # seconds

def run_git_commands():
    try:
        subprocess.run(["git", "add", "."], cwd=OUTPUT_DIR.parent, check=True)
        subprocess.run(["git", "commit", "-m", "🤖 Auto-commit: Oracle outputs updated"], cwd=OUTPUT_DIR.parent, check=True)
        subprocess.run(["git", "push"], cwd=OUTPUT_DIR.parent, check=True)
        print("✅ Git auto-push completed.")
    except subprocess.CalledProcessError as e:
        print("⚠️ Git push failed:", e)

def watch_outputs():
    print(f"📤 Git Auto Push Agent watching: {OUTPUT_DIR}")
    last_mtime = None
    while True:
        latest = max((f.stat().st_mtime for f in OUTPUT_DIR.glob("*.md")), default=None)
        if latest and latest != last_mtime:
            last_mtime = latest
            run_git_commands()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    watch_outputs()
