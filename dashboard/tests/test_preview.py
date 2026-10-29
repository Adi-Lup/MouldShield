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
from unittest.mock import patch, MagicMock
import importlib.util
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

    def test_static_files_do_not_reuse_an_old_conditional_cache(self):
        request = urllib.request.Request(self.base+'/app.js?v=20261029-t20-t22-fixes', headers={'If-Modified-Since': 'Wed, 01 Jan 2031 00:00:00 GMT', 'If-None-Match': 'old-build'})
        with urllib.request.urlopen(request, timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertIn('no-store', response.headers.get('Cache-Control', ''))
            self.assertEqual(response.headers.get('X-MouldShield-Build'), '20261029-t20-t22-fixes')
            self.assertIn(b'connect-live', response.read())

    def test_report_proxy_allows_time_for_the_explanation_service(self):
        import io
        spec=importlib.util.spec_from_file_location('preview_timeout', ROOT/'run.py')
        preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
        handler=object.__new__(preview.PreviewHandler)
        handler.path='/api/report';handler.command='POST';handler.api_url='http://fixture.test'
        handler.headers={'Content-Length':'2'};handler.rfile=io.BytesIO(b'{}');handler.wfile=io.BytesIO()
        handler.send_response=MagicMock();handler.send_header=MagicMock();handler.end_headers=MagicMock()
        response=MagicMock();response.__enter__.return_value=response;response.status=200;response.read.return_value=b'{}';response.headers={'Content-Type':'application/json'}
        opener=MagicMock();opener.open.return_value=response
        with patch.object(preview.urllib.request,'build_opener',return_value=opener):
            handler.proxy()
        self.assertEqual(opener.open.call_args.kwargs['timeout'],55)

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
        for name in ['index.html', 'style.css', 'core.js', 'i18n.js', 'app.js', 'config.js', 'assets/logo-by-the-sharks.svg', 'boot.js', 'START_HERE.html', 'mobile.html', 'qr.html', 'phone.css', 'mobile.js', 'phone-core.js', 'MouldShield_QR.html', 'MouldShield_QR.png', 'diagrams/T15_use_case.png', 'diagrams/T15_data_flow.png']:
            with self.subTest(name=name), urllib.request.urlopen(self.base+'/'+name, timeout=2) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.read())

    def test_phone_configuration_is_local_only_by_default(self):
        data = self.get_json('/preview-info')
        self.assertIs(data['lan'], False)
        self.assertEqual(data['phone_urls'], [])
        self.assertEqual(data['port'], self.port)

    def test_lan_flag_starts_phone_access_and_still_proxies_readings(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        command = [sys.executable, str(ROOT/'run.py'), '--no-browser', '--lan', '--fixed-port', '--port', str(port), '--api-url', 'http://127.0.0.1:'+str(self.upstream.server_port)]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        base = 'http://127.0.0.1:'+str(port)
        try:
            for attempt in range(40):
                try:
                    with urllib.request.urlopen(base+'/preview-info', timeout=1) as response:
                        info = json.load(response)
                    break
                except OSError:
                    time.sleep(.05)
            else:
                self.fail('LAN preview did not start')
            self.assertIs(info['lan'], True)
            self.assertEqual(info['port'], port)
            with urllib.request.urlopen(base+'/api/readings/latest', timeout=2) as response:
                self.assertEqual(json.load(response)['humidity_pct'], 68.4)
            with urllib.request.urlopen(base+'/mobile.html?mode=live', timeout=2) as response:
                self.assertIn(b'phone-temperature', response.read())
        finally:
            process.terminate()
            process.communicate(timeout=5)

    def test_network_detection_uses_route_when_hostname_only_returns_loopback(self):
        spec = importlib.util.spec_from_file_location('mouldshield_preview', ROOT/'run.py')
        preview = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preview)
        route = MagicMock()
        route.__enter__.return_value = route
        route.getsockname.return_value = ('192.168.1.24', 50000)
        with patch.object(preview.socket, 'socket', return_value=route), patch.object(preview.socket, 'gethostbyname_ex', return_value=('laptop', [], ['127.0.0.1', '192.168.1.24', '192.168.56.1'])):
            self.assertEqual(preview.discover_phone_urls(8080), ['http://192.168.1.24:8080/', 'http://192.168.56.1:8080/'])
        route.send.assert_not_called()
        route.sendto.assert_not_called()

    def test_mobile_source_files_are_present_and_live_by_default(self):
        page = (ROOT/'mobile.html').read_text(encoding='utf-8')
        self.assertIn('src="mobile.js?v=', page)
        self.assertIn("let mode='live'", (ROOT/'mobile.js').read_text(encoding='utf-8'))
        self.assertNotIn('data-view="diagrams"', page)

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
        # The standalone page embeds one PNG for the PDF header logo.
        # Permit that expected image while keeping the rest of the app self-contained.
        self.assertEqual(page.count('data:image/png;base64,'), 1)
        self.assertRegex(page, r"window\.MouldShieldPdfLogo=['\"]data:image/png;base64,")
        self.assertIn('Make sure the sensor is switched on and connected to Wi-Fi, then refresh the page.', page)
        self.assertNotIn('Keep the sensor and the project API running, then refresh the dashboard.', page)
        self.assertNotIn('T15_data_flow.png', page)
        self.assertNotIn('data-view="diagrams"', page)
        self.assertNotIn('id="diagrams-view"', page)
        self.assertNotIn('data-mode-label', page)
        self.assertIn('id="ui-language"', page)
        self.assertIn('MouldShieldI18n', page)
        for name in ['T15_use_case.png', 'T15_data_flow.png']:
            self.assertTrue((ROOT/'diagrams'/name).is_file())



if __name__ == '__main__':
    unittest.main()
