import requests

LEAGUE_ID = "4500"
SEASON = "2026"

def fetch_matches():
url = (
f"https://www.thesportsdb.com/api/v1/json/3/"
f"eventsseason.php?id={LEAGUE_ID}&s={SEASON}"
)

r = requests.get(url, timeout=30)
r.raise_for_status()

data = r.json()

events = []

for e in data.get("events", []):

    events.append({
        "id": str(e["idEvent"]),
        "home": e["strHomeTeam"],
        "away": e["strAwayTeam"],
        "home_score": e.get("intHomeScore"),
        "away_score": e.get("intAwayScore"),
        "date": e["dateEvent"],
        "time": e.get("strTime") or "00:00:00",
        "venue": e.get("strVenue") or "",
    })

return events
