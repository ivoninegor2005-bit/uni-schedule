import requests
from bs4 import BeautifulSoup
from datetime import datetime

GROUP = "БХ-2331"
URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"


def clean(text):
    return " ".join(text.split()).strip()


def parse_lessons(soup):
    lessons = []

    for card in soup.select("div.rasp-para"):
        try:
            # ⏰ время
            time = card.select_one(".para-time").get_text(strip=True)
            start, end = [t.strip() for t in time.split("-")]

            desc = card.select_one(".rasp-desc")

            # 📌 предмет (первая строка)
            title = desc.find("p").contents[0]
            title = clean(title)

            full = clean(desc.get_text(" ", strip=True))

            # 🏫 аудитория
            location = ""
            if "Учебная аудитория" in full:
                location = full.split("Учебная аудитория")[1].split("Преподаватель")[0]
                location = "Учебная аудитория " + location.strip()

            lessons.append({
                "title": title,
                "location": location,
                "start": start,
                "end": end
            })

        except:
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

        except:
            continue

    return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Uni Schedule//RU\n" + "\n".join(events) + "\nEND:VCALENDAR"


def main():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    lessons = parse_lessons(soup)

    print(f"Lessons: {len(lessons)}")

    ics = build_ics(lessons)

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)


if __name__ == "__main__":
    main()
