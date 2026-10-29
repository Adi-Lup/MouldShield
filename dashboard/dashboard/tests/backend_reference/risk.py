# T22 read-only excerpt from Adi-Lup/MouldShield/backend/risk.py
# Reference blob: e20c1c63d8bf53ec36ed456f3991aae22ed229a3 (28 October 2026)
MODERATE_LIMIT = 60
HIGH_LIMIT = 70

def risk_level(humidity_pct):
    if humidity_pct > HIGH_LIMIT:
        return 'HIGH'
    if humidity_pct > MODERATE_LIMIT:
        return 'MODERATE'
    return 'LOW'
