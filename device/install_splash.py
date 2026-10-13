# install_splash.py - one-time installer for the MouldShield boot splash screen.
# Run it once from UiFlow2 (Python tab, Custom Edit mode, then Run Once).
# 1. Writes /flash/splash.py on the device and tests it.
# 2. Only if the test works: saves a copy of /flash/boot.py as /flash/boot_backup.py
#    and adds a small hook at the top of /flash/boot.py.
# The hook is inside try/except, so if the splash ever fails the normal boot continues.
# Running it again is safe: if the hook is already there, boot.py is not changed.
# Note: flashing the firmware again with M5Burner removes the splash, so run this again after that.
import M5
from M5 import *
import time

SPLASH_LINES = [
    "# splash.py - MouldShield start screen, shown for a few seconds at every boot",
    "import M5",
    "from M5 import Widgets",
    "import time",
    "",
    "SPLASH_SECONDS = 3",
    "",
    "def show():",
    "    M5.begin()",
    "    Widgets.setRotation(0)",
    "    Widgets.fillScreen(0x000000)",
    "    Widgets.Label('MouldShield', 9, 90, 1.0, 0x2878D6, 0x000000, Widgets.FONTS.Montserrat18)",
    "    Widgets.Label('prototype v0.1', 19, 120, 1.0, 0x2878D6, 0x000000, Widgets.FONTS.Montserrat14)",
    "    Widgets.Label('by THE SHARKS', 10, 217, 1.0, 0x9AA0A6, 0x000000, Widgets.FONTS.Montserrat12)",
    "    time.sleep(SPLASH_SECONDS)",
]

HOOK_LINES = [
    "# MouldShield splash screen (added 13 Oct 2026).",
    "# If it fails for any reason, the normal boot continues.",
    "try:",
    "    import splash",
    "    splash.show()",
    "except Exception as e:",
    "    print('MouldShield splash error:', e)",
    "",
]


def message(text, colour):
    Widgets.fillScreen(0x000000)
    Widgets.Label(text, 5, 110, 1.0, colour, 0x000000, Widgets.FONTS.Montserrat12)


M5.begin()
Widgets.setRotation(0)
try:
    with open('/flash/splash.py', 'w') as f:
        f.write('\n'.join(SPLASH_LINES) + '\n')
    import splash
    splash.show()
    with open('/flash/boot.py', 'r') as f:
        boot = f.read()
    if 'import splash' in boot:
        result = 'Already installed'
    else:
        with open('/flash/boot_backup.py', 'w') as f:
            f.write(boot)
        with open('/flash/boot.py', 'w') as f:
            f.write('\n'.join(HOOK_LINES) + '\n' + boot)
        result = 'Splash installed'
    colour = 0x00C853
except Exception as e:
    result = 'Error: ' + str(e)
    colour = 0xFF0000

print(result)
message(result, colour)
