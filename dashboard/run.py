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
import socket
import ipaddress

ROOT = Path(__file__).resolve().parent
MAX_BODY = 1_000_000
BUILD_ID = '20261028-t20-t22'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, api_url, **kwargs):
        self.api_url = api_url.rstrip('/')
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_head(self):
        # Always send current static files, including after an in-place Windows update.
        for header in ('If-Modified-Since', 'If-None-Match'):
            if header in self.headers:
                del self.headers[header]
        return super().send_head()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('X-MouldShield-Build', BUILD_ID)
        super().end_headers()

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == '/preview-info':
            payload = json.dumps(self.server.phone_info).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path.startswith('/api/'):
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
            with opener.open(request, timeout=55 if self.command == 'POST' and path.path == '/api/report' else 10) as response:
                payload = response.read(20_000_001)
                if len(payload) > 20_000_000:
                    self.send_error(502, 'API response too large')
                    return
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
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


def discover_phone_urls(port):
    """Prefer the interface used by the default route, then hostname addresses."""
    addresses = []
    try:
        # UDP connect selects a local route; no application data is sent.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route:
            route.settimeout(.5)
            route.connect(('192.0.2.1', 1))
            addresses.append(route.getsockname()[0])
    except OSError:
        pass
    try:
        addresses.extend(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    urls = []
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if ip.version == 4 and ip.is_private and not ip.is_loopback and not ip.is_link_local:
            url = 'http://{}:{}/'.format(address, port)
            if url not in urls:
                urls.append(url)
    return urls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lan', action='store_true', help='Allow phones on the same private Wi-Fi')
    parser.add_argument('--port', type=port_number, default=8080)
    parser.add_argument('--api-url', default='https://d15ad8kcnyn7ke.cloudfront.net/api')
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
            server = ThreadingHTTPServer(('0.0.0.0' if args.lan else '127.0.0.1', candidate), handler)
            args.port = candidate
            break
        except OSError as exc:
            last_error = exc
    if server is None:
        parser.exit(1, 'Cannot start preview: {}\nClose the earlier preview or run: py run.py --port 8090\nYou can also open START_HERE.html without Python.\n'.format(last_error))
    phone_urls = discover_phone_urls(args.port) if args.lan else []
    server.phone_info = {'lan': args.lan, 'port': args.port, 'phone_urls': phone_urls, 'build_id': BUILD_ID}
    url = 'http://127.0.0.1:{}/'.format(args.port)
    print('Starting MouldShield local preview', flush=True)
    print('Open your dashboard: ' + url, flush=True)
    print('Release: ' + BUILD_ID, flush=True)
    print('Project folder: ' + str(ROOT), flush=True)
    print('API proxy: /api -> ' + args.api_url, flush=True)
    print('Starts with live sensor readings. See example data opens labelled samples. Ctrl+C stops the preview.', flush=True)
    if args.lan:
        print('Phone access is on. Use the same private Wi-Fi on laptop and phone.', flush=True)
        print('QR page: ' + url + 'MouldShield_QR.html', flush=True)
        for phone_url in phone_urls:
            print('Phone address (check your Wi-Fi adapter): ' + phone_url, flush=True)
    if not args.no_browser:
        timer = Timer(.3, webbrowser.open, args=(url + '?build=' + BUILD_ID,))
        timer.daemon = True
        timer.start()
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPreview stopped.')


if __name__ == '__main__':
    main()
