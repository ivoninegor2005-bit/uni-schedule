import requests

ICS_URL = "https://uspu.ru/education/eios/schedule/calendar/calendar_filter/calendar_БХ-2331_22.04.2026%2012%3A00%3A00_13.05.2026%2012%3A00%3A00.ics"


def fetch_ics():
    print("Downloading ICS...")

    try:
        r = requests.get(
            ICS_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
            allow_redirects=True
        )
        r.raise_for_status()

        print("Status:", r.status_code)
        print("Length:", len(r.text))

        return r.text

    except Exception as e:
        print("Download failed:", e)
        return None


def validate_ics(text):
    if not text:
        return False

    return "BEGIN:VCALENDAR" in text and "END:VCALENDAR" in text


def main():
    ics = fetch_ics()

    if not validate_ics(ics):
        print("Invalid ICS → fallback empty calendar")
        ics = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"

    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(ics)

    print("calendar.ics written")


if __name__ == "__main__":
    main()
