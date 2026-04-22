import requests
from bs4 import BeautifulSoup
from datetime import datetime

GROUP = "БХ-2331"
URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"


def clean(text):
    return " ".join(text.split()).strip()


def fetch_html():
    print("Fetching schedule...")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    try:
        r = requests.get(URL, headers=headers, timeout=20)
        r.raise_for_status()
        print("Response received")
        return r.text

    except Exception as e:
        print("ERROR fetching page:", e)
        return None


def parse_lessons(html):
    soup = BeautifulSoup(html, "html.parser")
    lessons = []

    cards = soup.select("div.rasp-para")

    print(f"Found cards: {len(cards)}")

    for card in cards:
        try:
            time_el = card.select_one(".para-time")
            desc = card.select_one(".rasp-desc")

            if not time_el or not desc:
                continue

            time_text = clean(time_el.get_text())
            start, end = [t.strip() for t in time_text.split("-")]

            title = desc.find("p").contents[0]
            title = clean(title)

            full = clean(desc.get_text(" ", strip=True))

            location = ""
            if "Учебная аудитория" in full:
                location = full.split("Учебная аудитория")[1].split("Преподаватель")[0]
                location = "Учебная аудитория " + location.strip()

            lessons.append({
                "title": title,
                "start": start,
                "end": end,
                "location": location
            })

        except Exception as e:
            print("Skip card:", e)
            continue

    return lessons


def build_ics(lessons):
    base = datetime.today()
    events = []

    for i, l in enumerate(lessons):
        try:
            sh, sm = map(int, l["start"].split(":"))
            eh, em = map(int, l["end"].split(":"))

            start = base.replace(hour=sh, minute=sm, second=0)
            end = base.replace(hour=eh, minute=em, second=0)

            event = f"""BEGIN:VEVENT
UID:{GROUP}-{i}
SUMMARY:{l['title']}
LOCATION:{l['location']}
DTSTART:{start.strftime("%Y%m%dT%H%M%S")}
DTEND:{end.strftime("%Y%m%dT%H%M%S")}
END:VEVENT"""

            events.append(event)

        except Exception as e:
            print("Skip lesson:", e)
            continue

    return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Uni Schedule//RU\n" + "\n".join(events) + "\nEND:VCALENDAR"


def main():
    html = fetch_html()

    if not html:
        print("No HTML, exiting")
        return

    lessons = parse_lessons(html)

    print(f"Total lessons: {len(lessons)}")

    ics = build_ics(lessons)

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print("calendar.ics generated")


if __name__ == "__main__":
    main()
