"""Local MouldShield preview and same-origin proxy to the team's FastAPI app."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
import json
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
MAX_BODY = 1_000_000


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, api_url, **kwargs):
        self.api_url = api_url.rstrip('/')
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/report':
            self.proxy()
        else:
            self.send_error(405, 'Only POST /api/report is supported by this preview')

    def proxy(self):
        path = urllib.parse.urlsplit(self.path)
        if not path.path.startswith('/api/') or '..' in path.path:
            self.send_error(400, 'Invalid API path')
            return
        route = path.path[4:] + ('?' + path.query if path.query else '')
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length < 0 or length > MAX_BODY:
                self.send_error(413, 'Request too large')
                return
            body = self.rfile.read(length) if self.command == 'POST' else None
            request = urllib.request.Request(
                self.api_url + route, data=body, method=self.command,
                headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
            )
            opener = urllib.request.build_opener(NoRedirect)
            with opener.open(request, timeout=10) as response:
                payload = response.read(20_000_001)
                if len(payload) > 20_000_000:
                    self.send_error(502, 'API response too large')
                    return
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read(MAX_BODY)
            self.send_response(exc.code)
            self.send_header('Content-Type', exc.headers.get('Content-Type', 'application/json'))
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (OSError, ValueError) as exc:
            payload = json.dumps({'error': 'Back-end unavailable. Start FastAPI or check --api-url.', 'detail': str(exc)}).encode()
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)


def port_number(value):
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError('Port must be between 1 and 65535')
    return port


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=port_number, default=8080)
    parser.add_argument('--api-url', default='http://127.0.0.1:8000')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--auto-port', dest='auto_port', action='store_true', default=True, help='Try the next free preview port if needed (default)')
    parser.add_argument('--fixed-port', dest='auto_port', action='store_false', help='Use only the requested port (used by VS Code debugging)')
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.api_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password:
        parser.error('--api-url must be an HTTP(S) base URL without credentials')
    if args.port == parsed.port and parsed.hostname in ('localhost', '127.0.0.1'):
        parser.error('Preview and API need different ports; use 8080 for preview and 8000 for FastAPI')
    handler = partial(PreviewHandler, api_url=args.api_url)
    server = None
    last_error = None
    requested_port = args.port
    candidates = range(requested_port, min(requested_port + 11, 65536)) if args.auto_port else [requested_port]
    for candidate in candidates:
        if candidate == parsed.port and parsed.hostname in ('localhost', '127.0.0.1'):
            continue
        try:
            server = ThreadingHTTPServer(('127.0.0.1', candidate), handler)
            args.port = candidate
            break
        except OSError as exc:
            last_error = exc
    if server is None:
        parser.exit(1, 'Cannot start preview: {}\nClose the earlier preview or run: py run.py --port 8090\nYou can also open START_HERE.html without Python.\n'.format(last_error))
    url = 'http://127.0.0.1:{}/'.format(args.port)
    print('Starting MouldShield local preview', flush=True)
    print('Open your dashboard: ' + url, flush=True)
    print('API proxy: /api -> ' + args.api_url, flush=True)
    print('Starts in demo mode. Click Connect to API for real readings. Ctrl+C stops the preview.', flush=True)
    if not args.no_browser:
        timer = Timer(.3, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPreview stopped.')


if __name__ == '__main__':
    main()
