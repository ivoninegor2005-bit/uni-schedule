import requests
import time

ICS_URL = "https://uspu.ru/education/eios/schedule/calendar/calendar_filter/calendar_БХ-2331_22.04.2026%2012%3A00%3A00_13.05.2026%2012%3A00%3A00.ics"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/calendar,*/*",
}

def download_ics():
    print("Downloading ICS...")

    for i in range(5):
        try:
            r = requests.get(ICS_URL, headers=HEADERS, timeout=20)

            if r.status_code == 200 and "BEGIN:VCALENDAR" in r.text:
                print("ICS OK")
                return r.text

            print(f"bad response attempt {i}: {r.status_code}")

        except Exception as e:
            print(f"retry {i}: {e}")

        time.sleep(5)

    return None


def load_last_good():
    try:
        with open("calendar.ics", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return None


def save(data):
    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(data)


def fallback():
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Uni Schedule//RU
END:VCALENDAR
"""


def main():
    ics = download_ics()

    if ics:
        save(ics)
    else:
        print("Using last good or fallback")

        last = load_last_good()
        if last and "VEVENT" in last:
            save(last)
        else:
            save(fallback())


if __name__ == "__main__":
    main()
