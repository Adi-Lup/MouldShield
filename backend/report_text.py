# report_text.py - T13: the text of the report
#
# - week_stats(): the numbers for the letter (average, time above 70 %, highest reading)
# - build_letter(): the letter to the landlord, always in English, filled in from the database.
#   It only describes the readings. It does not say there is damp or mould, because the
#   sensor measures humidity, not damp.
# - fixed_explanation(): a short explanation in English, Romanian or Polish, used when
#   the AI explanation is not available (no AWS, Bedrock down, or the daily limit reached)
# - explanation_prompt() and clean_answer(): for the AI explanation in report.py
#
# Plain Python only, so it can be tested without the server.

import re
from datetime import datetime, timedelta, timezone

from risk import HIGH_LIMIT, risk_level

try:
    from zoneinfo import ZoneInfo
    LONDON = ZoneInfo("Europe/London")
except Exception:
    # Windows needs the tzdata package for this (it is in requirements.txt).
    # Without it we show UTC, which is the same as UK time in winter.
    LONDON = timezone.utc

LANGUAGES = ("en", "ro", "pl")
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# The device sends a reading every 15 seconds. A reading counts for 15 seconds at most,
# so a gap in the data is never counted as time above 70 % (same as the dashboard).
READING_SECONDS = 15

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def parse_time(timestamp):
    return datetime.strptime(timestamp, TIME_FORMAT).replace(tzinfo=timezone.utc)


def day_text(moment):
    local = moment.astimezone(LONDON)
    return "%d %s" % (local.day, MONTHS[local.month - 1])


def date_text(moment):
    local = moment.astimezone(LONDON)
    return "%d %s %d" % (local.day, MONTHS[local.month - 1], local.year)


def clock_text(moment):
    return moment.astimezone(LONDON).strftime("%H:%M")


def week_stats(rows, end):
    # rows: (timestamp, humidity_pct) of one device in the 7 days before "end", any order
    readings = sorted({parse_time(ts): hum for ts, hum in rows}.items())
    if not readings:
        return None

    seconds_above = 0
    for i, (moment, humidity) in enumerate(readings):
        if humidity > HIGH_LIMIT:
            if i + 1 < len(readings):
                gap = (readings[i + 1][0] - moment).total_seconds()
                seconds_above += min(gap, READING_SECONDS)
            else:
                seconds_above += READING_SECONDS

    values = [hum for _, hum in readings]
    highest_at, highest = max(readings, key=lambda item: item[1])
    return {
        "first": readings[0][0],
        "average": sum(values) / len(values),
        "seconds_above": seconds_above,
        "highest": highest,
        "highest_at": highest_at,
        "count": len(readings),
        "full_week": readings[0][0] <= end - timedelta(days=6),
    }


def time_above_text(seconds):
    if seconds <= 0:
        return "none"
    if seconds < 3600:
        return "less than an hour"
    hours = round(seconds / 3600)
    return "about 1 hour" if hours == 1 else "about %d hours" % hours


def build_letter(latest, stats, check, today):
    # latest: the reading the report is about (timestamp, temperature_c, humidity_pct)
    # stats: from week_stats(); check: the answer of verify_chain(); today: a datetime
    taken = parse_time(latest["timestamp"])

    if stats["full_week"]:
        average_label = "average humidity over the last 7 days"
    else:
        average_label = "average humidity since " + day_text(stats["first"])

    # Only say the readings are high when they are
    high = (risk_level(latest["humidity_pct"]) != "LOW" or risk_level(stats["average"]) != "LOW"
            or stats["seconds_above"] > 0)
    if high:
        opening = ("I have been keeping track of the humidity in the [room] with a sensor, "
                   "and the readings have been higher than I expected.")
    else:
        opening = ("I have been keeping track of the humidity in the [room] with a sensor, "
                   "and I would like to share the readings with you.")

    lines = [
        "[Your name]",
        "[Your address]",
        "",
        date_text(today),
        "",
        "Dear [landlord's name],",
        "",
        "Humidity readings in the [room] at [your address]",
        "",
        opening + " [Add anything you have noticed, for example condensation on the "
        "window in the morning.]",
        "",
        "The sensor has recorded:",
        "- %s: %d%%" % (average_label, round(stats["average"])),
        "- time above 70%%: %s" % time_above_text(stats["seconds_above"]),
        "- highest reading: %d%% on %s" % (round(stats["highest"]), day_text(stats["highest_at"])),
        "- last reading: %d%% at %.1f \u00b0C on %s at %s" % (
            round(latest["humidity_pct"]), latest["temperature_c"],
            day_text(taken), clock_text(taken)),
        "",
    ]

    # Only say the readings are unchanged when the check really says so
    if check.get("status") == "OK" and check.get("checked", 0) > 0:
        checked = check["checked"]
        found = "all {:,} readings".format(checked) if checked > 1 else "the reading"
        lines += [
            "The readings are kept in a log that shows if any of them were changed later. "
            "The last check, on %s, found %s unchanged." % (day_text(today), found),
            "",
        ]

    lines += [
        "Could we arrange a time for you, or someone you choose, to have a look at the room? "
        "I would be grateful for a reply within 10 working days. "
        "I am happy to send you the full readings.",
        "",
        "Kind regards,",
        "[Your name]",
    ]
    return "\n".join(lines)


FIXED = {
    "en": {
        "LOW": "Humidity is {h}%, which is LOW risk. At this level mould is unlikely to grow. "
               "Keep using the extractor fan and open a window after cooking or a shower.",
        "MODERATE": "Humidity is {h}%, which is MODERATE risk. Above 60%, condensation can form "
                    "on cold windows and walls. Open a window for a few minutes after cooking or "
                    "a shower and wipe off any water you see.",
        "HIGH": "Humidity is {h}%, which is HIGH risk. If it stays above 70% for long, mould can "
                "start to grow on cold surfaces. Air the room every day, keep it heated, and tell "
                "your landlord if it stays this high.",
    },
    "ro": {
        "LOW": "Umiditatea este {h}%, adică risc SCĂZUT. La acest nivel, mucegaiul nu are condiții "
               "să apară. Folosiți în continuare ventilatorul și aerisiți după gătit sau duș.",
        "MODERATE": "Umiditatea este {h}%, adică risc MODERAT. Peste 60%, se poate forma condens "
                    "pe ferestrele și pereții reci. Aerisiți câteva minute după gătit sau duș și "
                    "ștergeți apa care apare.",
        "HIGH": "Umiditatea este {h}%, adică risc RIDICAT. Dacă rămâne mult timp peste 70%, pe "
                "suprafețele reci poate apărea mucegai. Aerisiți camera în fiecare zi, păstrați-o "
                "încălzită și anunțați proprietarul dacă umiditatea rămâne la fel de mare.",
    },
    "pl": {
        "LOW": "Wilgotność wynosi {h}%, czyli ryzyko NISKIE. Przy takim poziomie pleśń raczej się "
               "nie pojawi. Nadal używaj wentylatora i wietrz po gotowaniu lub prysznicu.",
        "MODERATE": "Wilgotność wynosi {h}%, czyli ryzyko UMIARKOWANE. Powyżej 60% na zimnych "
                    "oknach i ścianach może skraplać się para. Wietrz pokój przez kilka minut po "
                    "gotowaniu lub prysznicu i wycieraj wodę, którą zauważysz.",
        "HIGH": "Wilgotność wynosi {h}%, czyli ryzyko WYSOKIE. Jeśli długo utrzymuje się powyżej "
                "70%, na zimnych powierzchniach może pojawić się pleśń. Wietrz pokój codziennie, "
                "ogrzewaj go i powiadom właściciela, jeśli wilgotność nadal będzie tak wysoka.",
    },
}


def fixed_explanation(humidity_pct, language):
    return FIXED[language][risk_level(humidity_pct)].format(h=round(humidity_pct))


LANGUAGE_NAMES = {"en": "British English", "ro": "Romanian", "pl": "Polish"}
LEVEL_NAMES = {
    "en": {"LOW": "LOW", "MODERATE": "MODERATE", "HIGH": "HIGH"},
    "ro": {"LOW": "SCĂZUT", "MODERATE": "MODERAT", "HIGH": "RIDICAT"},
    "pl": {"LOW": "NISKIE", "MODERATE": "UMIARKOWANE", "HIGH": "WYSOKIE"},
}


def explanation_prompt(latest, stats, language):
    level = risk_level(latest["humidity_pct"])
    return (
        "Write a short explanation of a damp risk reading for a tenant, in %s.\n"
        "Reading: humidity %d%%, temperature %.1f C, risk level %s (written as %s).\n"
        "Last 7 days: average humidity %d%%, time above 70%%: %s.\n"
        "Our limits: LOW is 60%% or less, MODERATE is above 60%%, HIGH is above 70%%.\n"
        "Rules:\n"
        "- 2 or 3 short sentences, about 50 words in total.\n"
        "- Simple everyday words. Say what the level means for this room and one or two "
        "practical things the tenant can do.\n"
        "- Use the numbers above. Do not add other numbers.\n"
        "- No greeting, no sign-off, no questions, no exclamation marks, no lists, no "
        "headings, no markdown, no emoji, no dashes between clauses.\n"
        "- Do not write about yourself and do not say the text was generated.\n"
        "- No diagnosis and nothing about health. Do not say there is mould.\n"
        "Answer with the explanation only."
    ) % (
        LANGUAGE_NAMES[language], round(latest["humidity_pct"]), latest["temperature_c"],
        level, LEVEL_NAMES[language][level], round(stats["average"]),
        time_above_text(stats["seconds_above"]),
    )


def clean_answer(text):
    # Keeps the AI answer plain. Returns None if it does not look like a short explanation,
    # so report.py uses the fixed text instead.
    if not isinstance(text, str):
        return None
    text = re.sub(r"[*#`_]", "", text)
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = " ".join(text.split())
    text = text.strip("\"' ")
    if len(text) < 40 or len(text) > 700 or "!" in text:
        return None
    return text
