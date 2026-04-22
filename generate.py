import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://uspu.ru/education/eios/schedule/?group_name=%D0%91%D0%A5-2331"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def parse_datetime(date_str, time_str):
    # date: 2026-04-22, time: 12:00 - 13:35
    start, end = time_str.split(" - ")
    start_dt = datetime.strptime(f"{date_str} {start}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date_str} {end}", "%Y-%m-%d %H:%M")
    return start_dt, end_dt


def download_html():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for block in soup.select(".rasp-para"):
        try:
            time = block.select_one(".para-time").get_text(strip=True)
            desc = block.select_one(".rasp-desc").get_text(" ", strip=True)

            # грубый парсинг даты (сайт обычно внутри расписания уже по дням)
            # здесь упрощённо — ты потом можешь улучшить
            today = datetime.now().strftime("%Y-%m-%d")

            start, end = parse_datetime(today, time)

            title = desc.split("(")[0].strip()

            location = ""
            if "Учебная аудитория" in desc:
                location = desc.split("Учебная аудитория")[-1].split("Преподаватель")[0].strip()

            events.append({
                "title": title,
                "start": start,
                "end": end,
                "location": location,
                "description": desc
            })

        except Exception:
            continue

    return events


def build_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Uni Schedule//RU",
        "CALSCALE:GREGORIAN"
    ]

    for i, e in enumerate(events):
        lines += [
            "BEGIN:VEVENT",
            f"UID:{i}-{e['start'].timestamp()}@uni",
            f"DTSTART:{e['start'].strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{e['end'].strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{e['title']}",
            f"LOCATION:{e['location']}",
            f"DESCRIPTION:{e['description']}",
            "END:VEVENT"
        ]

    lines.append("END:VCALENDAR")

    return "\n".join(lines)


def main():
    print("Downloading HTML...")
    try:
        html = download_html()
    except Exception as e:
        print("HTML download failed:", e)
        html = ""

    if html:
        events = parse_schedule(html)
    else:
        events = []

    if not events:
        print("No events → fallback empty calendar")

    ics = build_ics(events)

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print("calendar.ics written")


if __name__ == "__main__":
    main()
