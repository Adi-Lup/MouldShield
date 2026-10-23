"""Tests only local fixtures, never the team's real database or AWS services."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import base64
import queue
import re
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


class FixtureAPI(BaseHTTPRequestHandler):
    received = None

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == '/verify':
            data = {'status': 'OK', 'checked': 131}
        elif self.path == '/readings/latest':
            data = {'id': 1, 'device_id': 'fixture', 'timestamp': '2026-10-23T12:00:00Z', 'temperature_c': 20.1, 'humidity_pct': 68.4}
        else:
            self.send_error(404)
            return
        self.reply(data)

    def do_POST(self):
        FixtureAPI.received = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.reply({'explanation': 'Fixture response', 'letter': 'Dear landlord'})

    def reply(self, data):
        payload = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = ThreadingHTTPServer(('127.0.0.1', 0), FixtureAPI)
        cls.worker = Thread(target=cls.upstream.serve_forever, daemon=True)
        cls.worker.start()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.process = subprocess.Popen([sys.executable, str(ROOT/'run.py'), '--no-browser', '--port', str(cls.port), '--api-url', 'http://127.0.0.1:'+str(cls.upstream.server_port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cls.base = 'http://127.0.0.1:'+str(cls.port)
        for _ in range(50):
            try:
                with urllib.request.urlopen(cls.base, timeout=1) as response:
                    response.read()
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('Preview server did not start')

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.communicate(timeout=5)
        cls.upstream.shutdown()
        cls.upstream.server_close()

    def get_json(self, path):
        with urllib.request.urlopen(self.base+path, timeout=2) as response:
            return json.load(response)

    def test_verify_proxy(self):
        self.assertEqual(self.get_json('/api/verify'), {'status': 'OK', 'checked': 131})

    def test_reading_precision(self):
        self.assertEqual(self.get_json('/api/readings/latest')['humidity_pct'], 68.4)

    def test_language_forwarding(self):
        body = {'humidity_pct': 68.4, 'language': 'ro'}
        request = urllib.request.Request(self.base+'/api/report', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(request, timeout=2) as response:
            self.assertEqual(json.load(response)['explanation'], 'Fixture response')
        self.assertEqual(FixtureAPI.received, body)

    def test_assets(self):
        for name in ['index.html', 'style.css', 'core.js', 'i18n.js', 'app.js', 'config.js', 'assets/logo-by-the-sharks.svg', 'boot.js', 'START_HERE.html', 'diagrams/T15_use_case.png', 'diagrams/T15_data_flow.png']:
            with self.subTest(name=name), urllib.request.urlopen(self.base+'/'+name, timeout=2) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.read())

    def test_unknown_upstream_route_stays_an_error(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get_json('/api/not-an-endpoint')
        self.assertEqual(caught.exception.code, 404)

    def test_front_end_cannot_post_rounded_readings(self):
        request = urllib.request.Request(self.base+'/api/readings', data=b'{}', method='POST')
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=2)
        self.assertEqual(caught.exception.code, 405)

    def test_busy_port_fallback_and_fixed_port_error(self):
        occupied = self.upstream.server_port
        command = [sys.executable, str(ROOT/'run.py'), '--no-browser', '--port', str(occupied)]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = queue.Queue()
        def collect():
            for line in process.stdout:
                output.put(line)
        worker = Thread(target=collect, daemon=True)
        worker.start()
        try:
            self.assertIn('Starting MouldShield', output.get(timeout=5))
            address = output.get(timeout=5).strip().split(': ', 1)[1]
            self.assertNotEqual(address, 'http://127.0.0.1:{}/'.format(occupied))
            with urllib.request.urlopen(address, timeout=2) as response:
                self.assertIn(b'MouldShield', response.read())
        finally:
            process.terminate()
            process.wait(timeout=5)
            worker.join(timeout=2)
            process.stdout.close()
            process.stderr.close()
        fixed = subprocess.run(command + ['--fixed-port'], capture_output=True, text=True, timeout=5)
        self.assertEqual(fixed.returncode, 1)
        self.assertIn('Cannot start preview', fixed.stderr)
        self.assertIn('START_HERE.html', fixed.stderr)

    def test_standalone_is_self_contained_and_diagrams_stay_separate(self):
        page = (ROOT/'START_HERE.html').read_text(encoding='utf-8')
        self.assertNotRegex(page, r'<script[^>]+src=')
        self.assertNotRegex(page, r'<link[^>]+href=')
        self.assertNotIn('id="download-svg"', page)
        self.assertIn('window.MOULDSHIELD_STANDALONE=true', page)
        self.assertIn('src="data:image/svg+xml;base64,', page)
        self.assertNotIn('data:image/png;base64,', page)
        self.assertNotIn('data-view="diagrams"', page)
        self.assertNotIn('id="diagrams-view"', page)
        self.assertNotIn('data-mode-label', page)
        self.assertIn('id="ui-language"', page)
        self.assertIn('MouldShieldI18n', page)
        for name in ['T15_use_case.png', 'T15_data_flow.png']:
            self.assertTrue((ROOT/'diagrams'/name).is_file())



if __name__ == '__main__':
    unittest.main()
