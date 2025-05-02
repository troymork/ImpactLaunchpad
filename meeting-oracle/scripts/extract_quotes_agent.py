# scripts/extract_quotes_agent.py

import json, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import openai

BASE_DIR = Path(__file__).resolve().parent.parent
COMPLETED_DIR = BASE_DIR / "completed_tasks"
OUTPUT_DIR = BASE_DIR / "outputs"

def extract_quotes(transcript):
    prompt = f"""
You are the Quote Extractor Agent. Your task is to extract all notable or insightful quotes from the following transcript. A quote is considered notable if it is emotionally impactful, expresses a clear or powerful idea, or would be valuable to remember or share. Return the quotes in plain text as a list. Do not summarize.

Transcript:
{transcript}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract notable quotes from transcripts."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

class CompletedTaskHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".completed.json"):
            return

        time.sleep(0.5)
        with open(event.src_path, "r") as f:
            task = json.load(f)

        output_path = BASE_DIR / task["output_path"]
        if not output_path.exists():
            print(f"⛔ Output file missing: {output_path}")
            return

        with open(output_path, "r") as f:
            transcript_md = f.read()

        quotes = extract_quotes(transcript_md)
        quote_file = output_path.with_name(output_path.stem + ".quotes.md")
        with open(quote_file, "w") as f:
            f.write("## 💬 Notable Quotes\n\n" + quotes)

        print(f"💬 Quotes extracted to: {quote_file}")

if __name__ == "__main__":
    print(f"💬 Quote Agent watching: {COMPLETED_DIR}")
    observer = Observer()
    observer.schedule(CompletedTaskHandler(), str(COMPLETED_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
