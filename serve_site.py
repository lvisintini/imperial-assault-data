"""Serve the data explorer locally, laid out the way pages.yml deploys it: site/ at the root, plus data/, images/
and docs/ next to it.

Usage: uv run python serve_site.py [port]
"""
import http.server
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
SITE = os.path.join(ROOT, 'site')
MOUNTED = {'data', 'images', 'docs'}


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        top = path.lstrip('/').split('/', 1)[0]
        self.directory = ROOT if top in MOUNTED else SITE
        return super().translate_path(path)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler) as server:
        print(f'Serving the data explorer on http://localhost:{port}/')
        server.serve_forever()
