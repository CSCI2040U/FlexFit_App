from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import subprocess

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(self.command, shell=True)

    def on_modified(self, event):
        if event.src_path.endswith(".py") or event.src_path.endswith(".kv"):
            print(f"File changed: {event.src_path}, restarting...")
            self.start_process()

def watch():
    path = os.getcwd()
    event_handler = ReloadHandler("python main.py")  # Change main.py to your entry script
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch()
