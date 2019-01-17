from pathlib import Path
from watchdog.events import FileSystemEventHandler
import traceback
import time
import signal
from watchdog.observers import Observer

from p10s.generator import Generator


class PyterranetesEventHandler(FileSystemEventHandler):
    def __init__(self, ignore_dotfiles):
        super().__init__()
        self.ignore_dotfiles = ignore_dotfiles

    def _maybe_generate(self, filename, *message):
        path = Path(filename)
        if self.ignore_dotfiles and path.name.startswith("."):
            return False
        if path.name.endswith(".p10s"):
            print(*message)
            try:
                Generator().generate(filename)
            except Exception:
                traceback.print_exc()
                return

    def dispatch(self, event):
        if event.is_directory:
            return
        else:
            super().dispatch(event)

    def on_created(self, event):
        self._maybe_generate(event.src_path,
                             "%s created. building." % event.src_path)

    def on_modified(self, event):
        self._maybe_generate(event.src_path,
                             "%s modified, rebuilding" % event.src_path)

    def on_moved(self, event):
        self._maybe_generate(event.dest_path,
                             "%s moved, rebuilding at %s" % (event.src_path, event.dest_path))


class Watcher():
    def __init__(self, directory, ignore_dotfiles):
        self.directory = directory
        self.ignore_dotfiles = ignore_dotfiles
        self.run = True
        self.observer = Observer()

    def watch(self):
        dirname = str(Path(self.directory).resolve())
        self.observer.schedule(PyterranetesEventHandler(ignore_dotfiles=self.ignore_dotfiles),
                               dirname,
                               recursive=True)
        self.observer.start()
        while self.run:
            time.sleep(1)
        self.observer.join()

    def install_signal_handlers(self):
        def handler(sig, frame):
            self.run = False
            self.observer.stop()

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
