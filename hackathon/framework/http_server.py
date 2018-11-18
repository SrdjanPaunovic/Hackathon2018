"""This module contains only simple dummy HTTP server aimed to serve
results to vizualizing web page.

"""
__author__ = "Novak Boskov"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from os.path import exists, join
from os import makedirs, path
import sys
import json
from hackathon.utils.utils import CFG, TYPHOON_DIR, read_results


def prepare_dot_dir():
    """Prepare .typhoon directory used to store server specific data."""
    if not exists(TYPHOON_DIR):
        makedirs(TYPHOON_DIR)


class ResultsRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler"""
    def do_GET(self) -> None:
        dir_to_serve = path.join('hackathon', 'viz')

        self.send_response(200)

        url = urlparse(self.path)
        if url.path == '/results':
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            data = json.dumps(read_results())

            self.wfile.write(bytes(data, "utf8"))
        else:
            try:
                with open(dir_to_serve + url.path, 'r') as f:
                    html = f.read()

                self.send_header("Content-Length", str(len(html)))
                self.end_headers()

                self.wfile.write(bytes(html, "utf8"))
            except FileNotFoundError:
                self.send_error(404, 'File not found.')


def run() -> None:
    prepare_dot_dir()

    # Redirect stderr to log file
    sys.stderr = open(join(TYPHOON_DIR, 'simple_server.log'), 'w+')

    server_address = ('127.0.0.1', CFG.results_http_server_port)
    httpd = HTTPServer(server_address, ResultsRequestHandler)
    print('Running simple HTTP server on http://localhost:{} ...'
          .format(CFG.results_http_server_port))
    httpd.serve_forever()
