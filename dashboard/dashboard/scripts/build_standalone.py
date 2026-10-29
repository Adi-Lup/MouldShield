"""Build a single-file demo: no Python server, external assets or downloads required."""
from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parents[1]


def data_uri(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def build():
    page = (ROOT / 'index.html').read_text(encoding='utf-8')
    page = page.replace('<title>MouldShield · Your home, in view</title>', '<title>MouldShield - standalone preview</title>')
    page = re.sub(r'<link rel="stylesheet" href="style\.css(?:\?[^"]*)?">', lambda match: '<style>\n' + (ROOT/'style.css').read_text(encoding='utf-8') + '\n</style>', page)
    logo = data_uri(ROOT/'assets/logo-by-the-sharks.svg', 'image/svg+xml')
    page = page.replace('src="assets/logo-by-the-sharks.svg"', 'src="'+logo+'"')
    for name in ['boot.js', 'config.js', 'core.js', 'i18n.js', 'vendor/jspdf.umd.min.js', 'pdf-fonts.js', 'pdf-report.js', 'app.js']:
        code = (ROOT/name).read_text(encoding='utf-8').replace('</script', '<\\/script')
        if name == 'config.js':
            code += '\nwindow.MOULDSHIELD_CONFIG.mode="demo";\nwindow.MOULDSHIELD_STANDALONE=true;'
        page = re.sub(r'<script src="'+re.escape(name)+r'(?:\?[^"]*)?"></script>', lambda match: '<script>\n'+code+'\n</script>', page)
    if re.search(r'<script[^>]+src=', page):
        raise RuntimeError('External script remained in the standalone preview')
    target = ROOT/'START_HERE.html'
    target.write_text(page, encoding='utf-8')
    print(target)


if __name__ == '__main__':
    build()
