"""Tests for the link preview (what Teams, WhatsApp or LinkedIn show for our link)."""
import io
import os
import tempfile
import unittest

from PIL import Image


class LinkPreviewTests(unittest.TestCase):
    def setUp(self):
        self.old_dir = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)  # mouldshield.db is created here, not in the real folder
        import server
        from fastapi.testclient import TestClient
        self.server = server
        self.client = TestClient(server.app)

    def tearDown(self):
        os.chdir(self.old_dir)
        self.tmp.cleanup()

    def test_page_has_the_preview_tags(self):
        html = self.client.get("/").text
        self.assertIn('<meta property="og:image" content="https://d15ad8kcnyn7ke.cloudfront.net/og-image.png">', html)
        self.assertIn('<meta property="og:title"', html)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
        # the tags are in the head, not in the body
        self.assertLess(html.index('property="og:image"'), html.index("</head>"))

    def test_description_no_longer_says_sample_data(self):
        html = self.client.get("/").text
        self.assertNotIn("using sample data", html)
        self.assertEqual(html.count('<meta name="description"'), 1)

    def test_preview_image_is_a_1200_by_630_png(self):
        r = self.client.get("/og-image.png")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["content-type"], "image/png")
        self.assertEqual(Image.open(io.BytesIO(r.content)).size, (1200, 630))

    def test_image_can_be_read_from_outside_but_not_changed(self):
        self.assertEqual(self.client.head("/og-image.png").status_code, 200)
        self.assertEqual(self.client.post("/og-image.png").status_code, 403)


if __name__ == "__main__":
    unittest.main()
