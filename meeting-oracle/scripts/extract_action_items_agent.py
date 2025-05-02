# scripts/extract_action_items_agent.py

import json, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import openai

BASE_DIR = Path(__file__).resolve().parent.parent
COMPLETED_DIR = BASE_DIR / "completed_tasks"
OUTPUT_DIR = BASE_DIR / "outputs"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

openai.api_key = "your-api-key"  # Optional if handled elsewhere

def extract_action_items(transcript, task_id):
    prompt = f"""You are an executive meeting assistant. Extract all action items from this transcript, listing:
- Responsible person
- Specific task
- Deadline (if mentioned)

Transcript:
{transcript}"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    output_path = OUTPUT_DIR / f"{task_id}__actions.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(response.choices[0].message.content)
    print(f"✅ Actions written to: {output_path}")

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        time.sleep(0.5)
        task = json.load(open(event.src_path))
        task_id = task["task_id"]
        transcript_path = BASE_DIR / task["input_path"]
        if transcript_path.exists():
            transcript = transcript_path.read_text()
            extract_action_items(transcript, task_id)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), str(COMPLETED_DIR), recursive=False)
    observer.start()
    print(f"📋 Action Item Agent watching: {COMPLETED_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
