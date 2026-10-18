import M5
from M5 import *
from hardware import I2C, Pin
from unit import ENVUnit
import time

env = None

BLACK = 0x000000
WHITE = 0xFFFFFF
GREEN = 0x008000
AMBER = 0xFFBF00
RED = 0xB00020

# Status bar colours (from the MouldShield logo).
BAR_BLUE = 0x1F67C2
TICK_GREEN = 0x13866B
X_RED = 0xC8001E
STATUS_BAR_HEIGHT = 16

READ_INTERVAL = 15000
FLASH_INTERVAL = 500

# Provisional humidity limits (% RH) from our T04 research
# (GOV.UK damp and mould guidance and HHSRS guidance).
# They will be checked again when we write the risk calculation (T10).
AMBER_LIMIT = 60
RED_LIMIT = 70
ERROR_RETRY = 5000

# True when the last reading reached AWS IoT Core. It stays False until
# the AWS publish is added to this program (Sprint 2); then the publish
# code sets it after every send.
cloud_sent = False

SMALL = None
HEADING = None
NUMBER_FONTS = []


def bold_text(value, x, y, font, colour):
    screen = M5.Display
    screen.setFont(font)
    screen.setTextSize(1)
    # Same colour for text and background: the display library then
    # does not paint a background box, so the text sits directly on
    # the coloured screen. Drawing it twice, 1 pixel apart, makes it bold.
    screen.setTextColor(colour, colour)
    screen.drawString(value, x, y)
    screen.drawString(value, x + 1, y)


def draw_value(value, unit, top, area_height, colour):
    screen = M5.Display
    width = screen.width()

    screen.setTextSize(1)
    screen.setFont(SMALL)
    unit_width = screen.textWidth(unit)
    unit_height = screen.fontHeight()

    # Choose the largest font that fits with small side margins.
    chosen_font = NUMBER_FONTS[-1]

    for font in NUMBER_FONTS:
        screen.setFont(font)
        number_width = screen.textWidth(value)
        number_height = screen.fontHeight()

        if (
            number_width + unit_width + 6 <= width - 8
            and number_height <= area_height
        ):
            chosen_font = font
            break

    screen.setFont(chosen_font)
    number_width = screen.textWidth(value)
    number_height = screen.fontHeight()

    total_width = number_width + unit_width + 6
    x = max(4, (width - total_width) // 2)
    y = top + max(0, (area_height - number_height) // 2)

    bold_text(value, x, y, chosen_font, colour)

    unit_y = y + max(0, number_height - unit_height - 4)
    bold_text(
        unit,
        x + number_width + 5,
        unit_y,
        SMALL,
        colour
    )


def draw_cloud(cx, cy):
    # White cloud made of four circles and a rectangle under them.
    screen = M5.Display
    for dx, dy, r in ((-6, 2, 3), (-2, -1, 4), (3, -2, 4), (7, 2, 3)):
        screen.fillCircle(cx + dx, cy + dy, r, WHITE)
    screen.fillRect(cx - 6, cy + 1, 14, 5, WHITE)


def draw_status_bar(sent):
    # Blue bar at the top: cloud with a green tick and "SYNCED" when the
    # last reading reached AWS, cloud with a red X and "OFFLINE" when not.
    screen = M5.Display
    width = screen.width()
    screen.fillRect(0, 0, width, STATUS_BAR_HEIGHT, BAR_BLUE)

    label = "SYNCED" if sent else "OFFLINE"
    screen.setTextSize(1)
    screen.setFont(SMALL)
    text_width = screen.textWidth(label)

    # The cloud is 20 pixels wide; the cloud, a 4 pixel gap and the word
    # are centred together.
    left = (width - (20 + 4 + text_width)) // 2
    cx = left + 9
    cy = 8
    draw_cloud(cx, cy)

    for offset in (0, 1):
        if sent:
            screen.drawLine(cx - 3 + offset, cy + 1, cx - 1 + offset, cy + 3, TICK_GREEN)
            screen.drawLine(cx - 1 + offset, cy + 3, cx + 3 + offset, cy - 1, TICK_GREEN)
        else:
            screen.drawLine(cx - 2 + offset, cy - 1, cx + 2 + offset, cy + 3, X_RED)
            screen.drawLine(cx - 2 + offset, cy + 3, cx + 2 + offset, cy - 1, X_RED)

    text_y = (STATUS_BAR_HEIGHT - screen.fontHeight()) // 2
    bold_text(label, left + 24, text_y, SMALL, WHITE)


def draw_screen(level, temperature, humidity, flash_on=True):
    screen = M5.Display
    width = screen.width()
    height = screen.height()

    colours = [GREEN, AMBER, RED]
    headings = ["LOW RISK", "MODERATE RISK", "HIGH RISK"]

    background = colours[level]

    if level == 2 and not flash_on:
        background = BLACK

    foreground = BLACK if level == 1 else WHITE

    # Full screen background matches the current status.
    screen.fillScreen(background)
    screen.setTextSize(1)

    # Cloud status bar at the top.
    draw_status_bar(cloud_sent)

    # Centred risk heading.
    heading = headings[level]
    font = HEADING
    screen.setFont(font)

    if screen.textWidth(heading) > width - 10:
        font = SMALL
        screen.setFont(font)

    heading_width = screen.textWidth(heading)

    bold_text(
        heading,
        (width - heading_width - 1) // 2,
        STATUS_BAR_HEIGHT + 3,
        font,
        foreground
    )

    # Large centred values with small units.
    draw_value(
        "%.1f" % temperature,
        "C",
        41,
        70,
        foreground
    )

    # Thin separator between temperature and humidity.
    screen.drawLine(5, 117, width - 6, 117, foreground)

    draw_value(
        "%d" % humidity,
        "%",
        123,
        76,
        foreground
    )

    # Three equal colour blocks with small borders.
    margin = 5
    gap = 4
    block_width = (width - 2 * margin - 2 * gap) // 3
    bar_y = height - 27
    bar_height = 21

    for index in range(3):
        x = margin + index * (block_width + gap)

        screen.fillRect(
            x,
            bar_y,
            block_width,
            bar_height,
            colours[index]
        )

        # Black borders distinguish blocks from the background.
        screen.drawRect(
            x,
            bar_y,
            block_width,
            bar_height,
            BLACK
        )

        screen.drawRect(
            x + 1,
            bar_y + 1,
            block_width - 2,
            bar_height - 2,
            BLACK
        )

        # White outline and an arrow show the current category.
        if index == level:
            screen.drawRect(
                x - 1,
                bar_y - 1,
                block_width + 2,
                bar_height + 2,
                WHITE
            )

            middle = x + block_width // 2
            screen.fillRect(middle - 1, bar_y - 13, 3, 6, foreground)
            screen.fillTriangle(
                middle - 5, bar_y - 8,
                middle + 5, bar_y - 8,
                middle, bar_y - 3,
                foreground
            )


def draw_error():
    screen = M5.Display
    screen.fillScreen(BLACK)
    screen.setTextSize(1)
    screen.setFont(SMALL)
    message = "SENSOR ERROR"
    x = (screen.width() - screen.textWidth(message)) // 2
    bold_text(message, x, screen.height() // 2 - 6, SMALL, WHITE)


def beep(count):
    for index in range(count):
        Speaker.tone(2000, 180)
        time.sleep_ms(280)
        M5.update()


def setup():
    global env, SMALL, HEADING, NUMBER_FONTS

    M5.begin()
    M5.Display.setRotation(0)
    M5.Display.fillScreen(BLACK)

    SMALL = M5.Lcd.FONTS.DejaVu12
    HEADING = M5.Lcd.FONTS.DejaVu18

    NUMBER_FONTS = [
        M5.Lcd.FONTS.DejaVu56,
        M5.Lcd.FONTS.DejaVu40,
        M5.Lcd.FONTS.DejaVu24
    ]

    Power.setExtOutput(True)
    time.sleep_ms(200)

    i2c0 = I2C(
        0,
        scl=Pin(10),
        sda=Pin(9),
        freq=100000
    )

    # If the sensor is not plugged in at start-up, show an error and
    # keep trying, instead of stopping the program.
    while env is None:
        try:
            env = ENVUnit(i2c=i2c0, type=3)
        except Exception as error:
            print("Sensor not found:", error)
            draw_error()
            time.sleep_ms(ERROR_RETRY)

    Speaker.begin()
    Speaker.setVolumePercentage(100)


def run():
    previous_level = 0

    while True:
        cycle_start = time.ticks_ms()

        # If the sensor cable is loose, the read fails. We show an error
        # and try again, instead of letting the whole program stop.
        try:
            temperature = env.read_temperature()
            humidity = env.read_humidity()
        except Exception as error:
            print("Sensor read failed:", error)
            draw_error()
            time.sleep_ms(ERROR_RETRY)
            continue

        # The sensor is accurate to about 2 % RH, so a decimal would
        # suggest more precision than it has. We round humidity to a whole
        # number and use the same rounded value for the risk level, so the
        # screen never shows "60 %" on an amber background.
        # The exact value (humidity) is kept for sending to the cloud.
        humidity_shown = round(humidity)

        if humidity_shown > RED_LIMIT:
            level = 2
        elif humidity_shown > AMBER_LIMIT:
            level = 1
        else:
            level = 0

        draw_screen(level, temperature, humidity_shown)

        # Beep only when the risk goes up (1 beep for amber, 2 for red),
        # not at every reading, so the device is not annoying at night.
        if level > previous_level:
            beep(level)
        previous_level = level

        print(
            "Temperature:", temperature,
            "C | Humidity:", humidity, "%"
        )

        last_flash = True

        while time.ticks_diff(
            time.ticks_ms(), cycle_start
        ) < READ_INTERVAL:

            elapsed = time.ticks_diff(
                time.ticks_ms(), cycle_start
            )

            if level == 2:
                flash_on = (
                    elapsed // FLASH_INTERVAL
                ) % 2 == 0

                if flash_on != last_flash:
                    draw_screen(
                        level,
                        temperature,
                        humidity_shown,
                        flash_on
                    )
                    last_flash = flash_on

            M5.update()
            time.sleep_ms(30)


if __name__ == "__main__":
    setup()
    run()
