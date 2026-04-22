import requests
import os

URL = "https://uspu.ru/education/eios/schedule/calendar/calendar_filter/calendar_БХ-2331_22.04.2026%2012%3A00%3A00_13.05.2026%2012%3A00%3A00.ics"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def download():
    try:
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("Download failed:", e)
        return None

def is_valid(ics):
    return ics and "BEGIN:VEVENT" in ics

def load_old():
    if os.path.exists("calendar.ics"):
        return open("calendar.ics", "r", encoding="utf-8").read()
    return None

def save(data):
    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(data)

def main():
    print("Downloading ICS...")

    new_ics = download()

    if is_valid(new_ics):
        print("Valid ICS → saving")
        save(new_ics)
        return

    print("Invalid ICS → fallback")

    old = load_old()

    if is_valid(old):
        print("Using previous version")
        save(old)
    else:
        print("Empty calendar fallback")
        save("BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR\n")

main()
