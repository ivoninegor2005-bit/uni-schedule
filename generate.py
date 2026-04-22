import requests
from datetime import datetime

ICS_URL = "https://uspu.ru/education/eios/schedule/calendar/calendar_filter/calendar_БХ-2331_22.04.2026%2012%3A00%3A00_13.05.2026%2012%3A00%3A00.ics"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/calendar,text/plain,*/*",
}

def download_ics():
    print("Downloading ICS...")

    r = requests.get(ICS_URL, headers=HEADERS, timeout=30)

    if r.status_code != 200:
        print("Download failed:", r.status_code)
        return None

    return r.text


def save_calendar(content: str):
    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(content)
    print("calendar.ics written")


def validate(content: str):
    if not content:
        return False
    return "BEGIN:VCALENDAR" in content and "VEVENT" in content


def fallback_calendar():
    print("Invalid ICS → fallback empty calendar")

    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Uni Schedule//RU
CALSCALE:GREGORIAN
END:VCALENDAR
"""


def main():
    ics = download_ics()

    if validate(ics):
        print("ICS OK")
        save_calendar(ics)
    else:
        save_calendar(fallback_calendar())


if __name__ == "__main__":
    main()
