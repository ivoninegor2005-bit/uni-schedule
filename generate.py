import requests
from bs4 import BeautifulSoup
from datetime import datetime

GROUP = "БХ-2331"
URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"


def clean(t):
    return " ".join(t.split()).strip()


def fetch_html():
    print("Fetching schedule...")

    try:
        r = requests.get(
            URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        r.raise_for_status()
        print("HTML loaded")
        return r.text

    except Exception as e:
        print("Fetch error:", e)
        return None


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.rasp-para")

    print("Cards:", len(cards))

    lessons = []

    for c in cards:
        try:
            time = c.select_one(".para-time").get_text(strip=True)
            start, end = [x.strip() for x in time.split("-")]

            desc = c.select_one(".rasp-desc")

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
            print("skip:", e)

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

            events.append(f"""BEGIN:VEVENT
UID:{GROUP}-{i}
SUMMARY:{l['title']}
LOCATION:{l['location']}
DTSTART:{start.strftime("%Y%m%dT%H%M%S")}
DTEND:{end.strftime("%Y%m%dT%H%M%S")}
END:VEVENT""")

        except Exception as e:
            print("event skip:", e)

    return (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//Uni Schedule//RU\n"
        + "\n".join(events) +
        "\nEND:VCALENDAR"
    )


def main():
    html = fetch_html()

    # 🔥 ВАЖНО: файл ВСЕГДА создаётся
    if html:
        lessons = parse(html)
        print("Lessons:", len(lessons))
        ics = build_ics(lessons)
    else:
        print("Fallback calendar")
        ics = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print("calendar.ics written")


if __name__ == "__main__":
    main()
