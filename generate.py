import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ics import Calendar, Event

URL = "https://uspu.ru/education/eios/schedule/?group_name=БХ-2331"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def parse_time(text):
    start, end = text.split("-")
    return start.strip(), end.strip()

def build_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def download_html():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".rasp-para")

    events = []

    current_date = None

    for item in items:
        time_block = item.select_one(".para-time").text.strip()
        desc = item.select_one(".rasp-desc p").text.strip()

        # грубый парс даты из контекста страницы
        # (если вуз не даёт — берём из логики или расширяем позже)
        if not current_date:
            current_date = datetime.now().strftime("%Y-%m-%d")

        start_t, end_t = parse_time(time_block)

        events.append({
            "start": build_datetime(current_date, start_t),
            "end": build_datetime(current_date, end_t),
            "title": desc.split("\n")[0],
            "location": desc
        })

    return events

def build_ics(events):
    cal = Calendar()

    for i, e in enumerate(events):
        event = Event()
        event.name = e["title"]
        event.begin = e["start"]
        event.end = e["end"]
        event.location = e["location"]
        event.uid = str(i)

        cal.events.add(event)

    return cal

def save_calendar(cal):
    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.writelines(cal)

def main():
    print("Downloading HTML...")

    html = download_html()

    print("Parsing schedule...")
    events = parse_schedule(html)

    if not events:
        raise Exception("No events parsed — check HTML structure")

    print(f"Found {len(events)} events")

    cal = build_ics(events)

    save_calendar(cal)

    print("calendar.ics written successfully")

if __name__ == "__main__":
    main()
