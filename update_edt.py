import datetime
import requests
from icalendar import Calendar, Event

URL = "https://edt.uvsq.fr/Home/GetCalendarData"

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

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}

resp = requests.post(URL, data=payload, headers=headers, timeout=30)
resp.raise_for_status()
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
