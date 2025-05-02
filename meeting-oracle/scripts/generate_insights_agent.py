# scripts/generate_insights_agent.py

import json, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import openai

BASE_DIR = Path(__file__).resolve().parent.parent
COMPLETED_DIR = BASE_DIR / "completed_tasks"
OUTPUT_DIR = BASE_DIR / "outputs"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

def generate_insights(transcript, task_id):
    prompt = f"""Act as an AI strategist. From this transcript, generate:
- Key themes that emerged
- Opportunities for improvement or innovation
- Any hidden patterns or strategic suggestions

Transcript:
{transcript}"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    output_path = OUTPUT_DIR / f"{task_id}__insights.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(response.choices[0].message.content)
    print(f"✅ Insights written to: {output_path}")

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
            generate_insights(transcript, task_id)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), str(COMPLETED_DIR), recursive=False)
    observer.start()
    print(f"🔮 Insight Agent watching: {COMPLETED_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
