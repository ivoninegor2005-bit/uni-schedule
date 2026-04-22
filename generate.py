import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

GROUP = "БХ-2331"

URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"


def parse_lessons(html):
    soup = BeautifulSoup(html, "html.parser")

    lessons = []

    # 🔥 ВАЖНО: здесь почти наверняка надо подстроить селектор
    rows = soup.select("tr")  # <-- возможно заменить

    for r in rows:
        text = r.get_text(" ", strip=True)

        # грубый пример парсинга (потом улучшим)
        # ищем что-то типа: "08:30 - 10:00 Математика ауд. 101"
        m = re.search(r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2}).+?([А-Яа-яA-Za-z0-9 .,-]+)", text)
        if not m:
            continue

        start_t, end_t, title = m.groups()

        lessons.append({
            "title": title.strip(),
            "start": start_t,
            "end": end_t,
        })

    return lessons


def to_ics(lessons):
    today = datetime.today()

    events = []

    for i, l in enumerate(lessons):
        start_dt = today.replace(hour=int(l["start"][:2]), minute=int(l["start"][3:]))
        end_dt = today.replace(hour=int(l["end"][:2]), minute=int(l["end"][3:]))

        event = f"""BEGIN:VEVENT
UID:{i}-{GROUP}
SUMMARY:{l['title']}
DTSTART:{start_dt.strftime("%Y%m%dT%H%M%S")}
DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}
END:VEVENT"""

        events.append(event)

    return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Uni Schedule//RU\n" + "\n".join(events) + "\nEND:VCALENDAR"


def main():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    lessons = parse_lessons(r.text)

    ics = to_ics(lessons)

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print(f"Generated {len(lessons)} events")


if __name__ == "__main__":
    main()