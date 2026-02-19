import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- tiny web server for Render (keeps web service alive) ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

def run_web():
    port = int(os.getenv("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

def run_bot():
    import autoservice_bot  # your existing bot file
    autoservice_bot.main()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
