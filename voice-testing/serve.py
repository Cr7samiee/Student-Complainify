"""Local server for voice-testing: serves the folder AND proxies the Vosk
model downloads so the browser never talks to alphacephei.com directly
(which sends no CORS headers, so plain http.server always fails).

Usage:  python serve.py [port]      (default 8000)
Models are downloaded once into models_cache/ and served from disk after
that, so the page works fully offline after the first run.
"""
import os
import shutil
import sys
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'models_cache')

MODELS = {
    'vosk-model-small-en-us-0.15.zip':
        'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
    'vosk-model-small-en-in-0.4.zip':
        'https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip',
}


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path.startswith('/model/'):
            return self.serve_model(path[len('/model/'):])
        return super().do_GET()

    def serve_model(self, name):
        if name not in MODELS:
            self.send_error(404, 'unknown model: %s' % name)
            return
        os.makedirs(CACHE_DIR, exist_ok=True)
        dest = os.path.join(CACHE_DIR, name)
        if not os.path.exists(dest):
            part = dest + '.part'
            self.log_message('downloading %s', MODELS[name])
            req = urllib.request.Request(
                MODELS[name], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as src, open(part, 'wb') as out:
                shutil.copyfileobj(src, out)
            os.replace(part, dest)
        size = os.path.getsize(dest)
        self.send_response(200)
        self.send_header('Content-Type', 'application/zip')
        self.send_header('Content-Length', str(size))
        self.send_header('Cache-Control', 'max-age=31536000')
        self.end_headers()
        with open(dest, 'rb') as f:
            shutil.copyfileobj(f, self.wfile)

    def log_message(self, fmt, *args):
        sys.stderr.write('[serve] %s %s\n' % (self.address_string(), fmt % args))


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(BASE_DIR)
    print('Serving voice-testing on http://localhost:%d  (models proxy at /model/)' % port)
    ThreadingHTTPServer(('', port), Handler).serve_forever()
