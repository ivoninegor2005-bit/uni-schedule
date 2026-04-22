import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

GROUP = "БХ-2331"
URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"


def extract_date_range(soup):
    el = soup.select_one(".rasp-zag.rasp-zag-group")
    if not el:
        return None, None

    text = el.get_text(strip=True)

    # "Расписание c 22 апреля по 13 мая"
    m = re.search(r"c\s+(\d{1,2}\s+\w+)\s+по\s+(\d{1,2}\s+\w+)", text)
    if not m:
        return None, None

    return m.group(1), m.group(2)


def parse_lessons(soup):
    lessons = []

    # 🔥 ВАЖНО: универсальный поиск блоков
    # сайт у тебя, скорее всего, использует карточки или строки таблицы
    blocks = soup.find_all(["tr", "div"])

    for b in blocks:
        text = b.get_text(" ", strip=True)

        # пропускаем мусор
        if len(text) < 10:
            continue

        # ищем типичный формат пары:
        # "08:30 - 10:00 Математика ауд. 101"
        m = re.search(
            r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2}).+?([А-Яа-яA-Za-z0-9 .,\-]+)",
            text
        )

        if not m:
            continue

        start, end, title = m.groups()

        lessons.append({
            "title": title.strip(),
            "start": start,
            "end": end
        })

    return lessons


def build_ics(lessons):
    events = []

    for i, l in enumerate(lessons):
        try:
            today = datetime.today()

            sh, sm = map(int, l["start"].split(":"))
            eh, em = map(int, l["end"].split(":"))

            start = today.replace(hour=sh, minute=sm, second=0)
            end = today.replace(hour=eh, minute=em, second=0)

            event = f"""BEGIN:VEVENT
UID:{GROUP}-{i}
SUMMARY:{l['title']}
DTSTART:{start.strftime("%Y%m%dT%H%M%S")}
DTEND:{end.strftime("%Y%m%dT%H%M%S")}
END:VEVENT"""

            events.append(event)
        except:
            continue

    return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Uni Schedule//RU\n" + "\n".join(events) + "\nEND:VCALENDAR"


def main():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    start, end = extract_date_range(soup)
    lessons = parse_lessons(soup)

    ics = build_ics(lessons)

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print(f"Done: {len(lessons)} lessons")


if __name__ == "__main__":
    main()
