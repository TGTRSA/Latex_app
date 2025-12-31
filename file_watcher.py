import time
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#TODO: Make sure the watchdog watches the text of out input in the gui

WATCH_FILE = '/home/tash/pythonProds/watchdog/watched.py'
WATCH_DIR = os.path.dirname(WATCH_FILE)

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(WATCH_FILE):
            print(f"File {event.src_path} has been modified")

observer = Observer()
observer.schedule(MyHandler(), path=WATCH_DIR, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

