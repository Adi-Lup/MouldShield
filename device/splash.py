# splash.py - MouldShield start screen, shown for a few seconds at every boot.
# This file lives on the device at /flash/splash.py.
# It is called from /flash/boot.py (see install_splash.py), before the UiFlow2 startup menu.
import M5
from M5 import Widgets
import time

SPLASH_SECONDS = 3


def show():
    M5.begin()
    Widgets.setRotation(0)
    Widgets.fillScreen(0x000000)
    Widgets.Label('MouldShield', 9, 90, 1.0, 0x2878D6, 0x000000, Widgets.FONTS.Montserrat18)
    Widgets.Label('prototype v0.1', 19, 120, 1.0, 0x2878D6, 0x000000, Widgets.FONTS.Montserrat14)
    Widgets.Label('by THE SHARKS', 10, 217, 1.0, 0x9AA0A6, 0x000000, Widgets.FONTS.Montserrat12)
    time.sleep(SPLASH_SECONDS)
