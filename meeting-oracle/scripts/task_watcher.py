import json, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ✅ Absolute project path resolution
BASE_DIR = Path(__file__).resolve().parent.parent
TASK_DIR = BASE_DIR / "tasks"
DONE_DIR = BASE_DIR / "completed_tasks"

def run_task(task):
    task_type = task["type"]
    input_path = BASE_DIR / Path(task["input_path"])
    output_path = BASE_DIR / Path(task["output_path"])

    if task_type == "summarize_transcript":
        if not input_path.exists():
            print(f"❌ Input not found: {input_path}")
            return

        with open(input_path, "r") as f:
            transcript = f.read()

        result = f"""## 🧠 Oracle Summary for {task['task_id']}

(Replace this with your real Oracle output.)

---

📜 **Transcript**:

{transcript}
"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(result)

        print(f"✅ Summary written to: {output_path}")

    else:
        print(f"❌ Unknown task type: {task_type}")

    # Mark as complete
    completed_path = DONE_DIR / f"{task['task_id']}.completed.json"
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    with open(completed_path, "w") as f:
        json.dump(task, f, indent=2)

    # Clean up original task file

    git_commit_task(task["task_id"])
    task_file = TASK_DIR / f"{task['task_id']}.task.json"
    if task_file.exists():
        task_file.unlink()

class TaskHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return

        time.sleep(0.5)  # Prevent read-before-write issues
        with open(event.src_path, "r") as f:
            task = json.load(f)

        run_task(task)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(TaskHandler(), str(TASK_DIR), recursive=False)
    observer.start()
    print(f"👁️ Oracle is watching for new tasks in: {TASK_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

import subprocess

def git_commit_task(task_id):
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"🧠 Oracle run: {task_id}"], cwd=BASE_DIR, check=True)
        print(f"✅ Git commit created for task {task_id}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git commit failed: {e}")

