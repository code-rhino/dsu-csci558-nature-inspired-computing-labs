"""Start the 3D viewer.

    python3 -m viewer          # from the repo root; opens http://localhost:8765/viewer/
    python3 -m viewer 9000     # another port

Leave it running. Every time a lab saves a trace, the open viewer replays it.
Ctrl+C to stop.
"""
import functools
import http.server
import sys
import threading
import webbrowser
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
ROOT = Path(__file__).resolve().parent.parent   # serve the repo root


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def main():
    handler = functools.partial(Handler, directory=str(ROOT))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    except OSError:
        sys.exit(f"Port {PORT} is busy (is the viewer already running?). Try: python3 -m viewer {PORT + 1}")
    url = f"http://localhost:{PORT}/viewer/"
    print(f"viewer at {url}   (Ctrl+C to stop)")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
