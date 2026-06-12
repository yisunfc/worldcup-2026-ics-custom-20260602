import json
from pathlib import Path
from datetime import datetime, timezone

from icalendar import Calendar
from icalendar import Event

from fetch_matches import fetch_matches

CACHE_FILE = Path("cache.json")
OUTPUT_FILE = "worldcup_2026_final.ics"

def load_cache():
if CACHE_FILE.exists():
return json.loads(CACHE_FILE.read_text())
return {}

def save_cache(data):
CACHE_FILE.write_text(
json.dumps(data, indent=2, ensure_ascii=False)
)

def get_sequence(cache, uid, summary):

if uid not in cache:
    cache[uid] = {
        "summary": summary,
        "sequence": 1
    }
    return 1

old_summary = cache[uid]["summary"]

if old_summary != summary:
    cache[uid]["sequence"] += 1
    cache[uid]["summary"] = summary

return cache[uid]["sequence"]

def build_calendar():

matches = fetch_matches()

cache = load_cache()

cal = Calendar()

cal.add("prodid", "-//World Cup 2026//EN")
cal.add("version", "2.0")

now = datetime.now(timezone.utc)

for match in matches:

    uid = f"wc2026-{match['id']}"

    home = match["home"]
    away = match["away"]

    hs = match["home_score"]
    aw = match["away_score"]

    if hs is not None and aw is not None:

        summary = (
            f"{home} {hs}-{aw} {away}"
        )

        status = "Finished"

    else:

        summary = (
            f"{home} vs {away}"
        )

        status = "Scheduled"

    sequence = get_sequence(
        cache,
        uid,
        summary
    )

    dt = datetime.fromisoformat(
        f"{match['date']}T{match['time'].replace('Z','')}"
    )

    event = Event()

    event.add("uid", uid)

    event.add("summary", summary)

    event.add(
        "description",
        (
            f"Status: {status}\n"
            f"Venue: {match['venue']}\n"
            f"Last Update: {now.isoformat()}"
        )
    )

    event.add("dtstart", dt)

    event.add("dtstamp", now)

    event.add("last-modified", now)

    event.add("sequence", sequence)

    cal.add_component(event)

with open(
    OUTPUT_FILE,
    "wb"
) as f:
    f.write(cal.to_ical())

save_cache(cache)

if name == "main":
build_calendar()
