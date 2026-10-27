# condensation.py - T17: will condensation form in the room in the next 48 hours?
#
# 1. Dew point: the temperature at which the air in the room would start to leave water
#    on a surface. We work it out from the last indoor reading (temperature and humidity)
#    with the Magnus formula.
# 2. Coldest surface: the inside of an outside wall or window gets colder when it is cold
#    outside. We estimate it with the temperature factor fRsi:
#        surface = outside + fRsi x (inside - outside)
#    fRsi = 0.75 is the lowest value UK guidance accepts for a wall to avoid mould
#    (BRE IP1/06, used by the Building Regulations). Windows and cold corners are often
#    colder than this, so we also warn when the surface is close to the dew point.
# 3. If the coldest surface is at or below the dew point, condensation is likely.
#
# We assume the room stays at the last indoor reading. This is a simple estimate for a
# warning, not a measurement. Plain Python only, so it can be tested without the server.

import math
from datetime import timedelta

MAGNUS_A = 17.62
MAGNUS_B = 243.12   # degrees C
F_RSI = 0.75
CLOSE_MARGIN = 2.0  # degrees C between the surface and the dew point
HORIZON_HOURS = 48
MORNING_HOUR = 9    # "tonight" lasts until 09:00 the next morning


def dew_point(temperature_c, humidity_pct):
    gamma = math.log(humidity_pct / 100.0) + MAGNUS_A * temperature_c / (MAGNUS_B + temperature_c)
    return MAGNUS_B * gamma / (MAGNUS_A - gamma)


def surface_temperature(inside_c, outside_c):
    return outside_c + F_RSI * (inside_c - outside_c)


def level_for(surface_c, dew_c):
    if surface_c <= dew_c:
        return "HIGH"
    if surface_c - dew_c <= CLOSE_MARGIN:
        return "MODERATE"
    return "LOW"


def tonight_end(now_local):
    # The end of "tonight": 09:00 tomorrow, or 09:00 today if it is still early morning
    end = now_local.replace(hour=MORNING_HOUR, minute=0, second=0, microsecond=0)
    if now_local >= end:
        end += timedelta(days=1)
    return end


WARNINGS = {
    ("HIGH", "tonight"): "High condensation risk tonight",
    ("HIGH", "later"): "High condensation risk in the next 48 hours",
    ("MODERATE", "tonight"): "Some condensation risk tonight on cold windows",
    ("MODERATE", "later"): "Some condensation risk on cold windows in the next 48 hours",
    ("LOW", "later"): "Low condensation risk in the next 48 hours",
}

ADVICE = {
    "HIGH": "Keep the room heated and open a window for a few minutes after cooking or a shower. "
            "Wipe off any water on windows in the morning.",
    "MODERATE": "Keep the room heated tonight and wipe off any water on windows in the morning.",
    "LOW": "No action needed. Keep using the extractor fan after cooking or a shower.",
}


def assess(inside_c, inside_humidity, hours, now_local):
    # hours: [(local datetime, outside temperature)], the hourly forecast
    # Returns the level, the warning text and the numbers behind it.
    dew = dew_point(inside_c, inside_humidity)
    end = now_local + timedelta(hours=HORIZON_HOURS)
    night_end = tonight_end(now_local)
    ahead = [(t, temp) for t, temp in hours if now_local - timedelta(hours=1) < t <= end]
    if not ahead:
        raise ValueError("no forecast hours for the next 48 hours")

    def worst(items):
        moment, outside = min(items, key=lambda item: item[1])
        surface = surface_temperature(inside_c, outside)
        return level_for(surface, dew), surface, moment

    tonight = [(t, temp) for t, temp in ahead if t <= night_end]
    order = {"LOW": 0, "MODERATE": 1, "HIGH": 2}
    level, surface, moment = worst(ahead)
    when = "later"
    if tonight:
        night_level, night_surface, night_moment = worst(tonight)
        if night_level != "LOW" and order[night_level] >= order[level]:
            level, surface, moment, when = night_level, night_surface, night_moment, "tonight"
    if level == "LOW":
        when = "later"

    return {
        "level": level,
        "warning": WARNINGS[(level, when)],
        "advice": ADVICE[level],
        "dew_point_c": round(dew, 1),
        "coldest_surface_c": round(surface, 1),
        "coldest_at": moment.isoformat(),
    }


def tonight_minimum(hours, now_local):
    night_end = tonight_end(now_local)
    tonight = [temp for t, temp in hours if now_local - timedelta(hours=1) < t <= night_end]
    return min(tonight) if tonight else None
