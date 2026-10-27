# risk.py - T10: the risk level of a reading (LOW, MODERATE or HIGH)
#
# Same limits as the device and the dashboard (agreed at the Sprint 1 review):
#   HIGH      above 70 %
#   MODERATE  above 60 %, up to 70 %
#   LOW       60 % or less
#
# We use the exact humidity saved in the database, not the rounded number on the
# screen, the same as the dashboard (statusFor in dashboard/core.js).
# So 70.4 % is HIGH here, even though the screen shows 70 %.

MODERATE_LIMIT = 60
HIGH_LIMIT = 70

LEVELS = ("LOW", "MODERATE", "HIGH")


def risk_level(humidity_pct):
    if humidity_pct > HIGH_LIMIT:
        return "HIGH"
    if humidity_pct > MODERATE_LIMIT:
        return "MODERATE"
    return "LOW"
