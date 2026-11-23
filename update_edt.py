import datetime
import requests
from icalendar import Calendar, Event

BASE_URL = "https://edt.uvsq.fr"
DATA_URL = f"{BASE_URL}/Home/GetCalendarData"

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/cal?vt=agendaWeek&et=group&fid0=S5%20MIASHS",
    "X-Requested-With": "XMLHttpRequest",
}

# 1. Récupération automatique du cookie de session Celcat
session.get(f"{BASE_URL}/cal?vt=agendaWeek&et=group&fid0=S5%20MIASHS", headers=headers, timeout=30)

today = datetime.date.today()
start_date = (today - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
end_date = (today + datetime.timedelta(days=120)).strftime("%Y-%m-%d")

payload = {
    "start": start_date,
    "end": end_date,
    "resType": "103",
    "calView": "agendaWeek",
    "federationIds[]": "S5 MIASHS",
    "colourScheme": "3",
}

resp = session.post(DATA_URL, data=payload, headers=headers, timeout=30)
print("Status:", resp.status_code, "Length:", len(resp.text))
if not resp.text.strip():
    raise RuntimeError(f"Réponse vide du serveur (HTTP {resp.status_code}).")

events_data = resp.json()

cal = Calendar()
cal.add("prodid", "-//UVSQ EDT L3 MIASHS//FR")
cal.add("version", "2.0")

for item in events_data:
    if not item.get("start") or not item.get("end"):
        continue
    ev = Event()
    desc = item.get("description", "").replace("<br />", "\n").replace("<br/>", "\n")
    lines = [l.strip() for l in desc.split("\n") if l.strip()]
    summary = lines[1] if len(lines) > 1 else (lines[0] if lines else "Cours UVSQ")
    ev.add("summary", summary)
    ev.add("description", "\n".join(lines))
    ev.add("dtstart", datetime.datetime.fromisoformat(item["start"]))
    ev.add("dtend", datetime.datetime.fromisoformat(item["end"]))
    ev.add("uid", f"{item.get('id', hash(desc))}@edt.uvsq.fr")
    cal.add_component(ev)

with open("edt.ics", "wb") as f:
    f.write(cal.to_ical())
