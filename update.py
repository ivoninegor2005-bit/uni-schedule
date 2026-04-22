import requests
from datetime import datetime

GROUP = "БХ-2331"

ICS_URL = "https://uspu.ru/....ics"  # если есть прямая ссылка

def download_ics():
    print("Downloading ICS...")
    r = requests.get(ICS_URL, timeout=30)
    r.raise_for_status()
    return r.text

def save_file(content):
    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.write(content)

def main():
    try:
        ics = download_ics()

        if "BEGIN:VEVENT" not in ics:
            raise Exception("Empty ICS")

        save_file(ics)
        print("OK → calendar.ics updated")

    except Exception as e:
        print("FAILED:", e)

        # fallback, чтобы iPhone НЕ пустой
        fallback = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Uni Schedule//RU
BEGIN:VEVENT
UID:fallback
DTSTART:20260422T120000
DTEND:20260422T133500
SUMMARY:Расписание временно недоступно
END:VEVENT
END:VCALENDAR"""

        save_file(fallback)
