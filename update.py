import requests
import re
import subprocess
from datetime import datetime

# --- НАСТРОЙ ---
GROUP = "БХ-2331"

SCHEDULE_PAGE_URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"
BASE_ICS_URL = "https://uspu.ru/education/eios/schedule/calendar/calendar_filter"

OUTPUT_FILE = "calendar.ics"


def get_dates_from_html():
    print("Downloading HTML...")

    html = requests.get(SCHEDULE_PAGE_URL, timeout=30).text

    # Ищем: "Расписание c 22 апреля по 13 мая"
    match = re.search(r'Расписание c (\d{1,2}) (\w+) по (\d{1,2}) (\w+)', html)

    if not match:
        raise Exception("Не удалось найти даты в HTML")

    day1, month1, day2, month2 = match.groups()

    months = {
        "января": 1, "февраля": 2, "марта": 3,
        "апреля": 4, "мая": 5, "июня": 6,
        "июля": 7, "августа": 8, "сентября": 9,
        "октября": 10, "ноября": 11, "декабря": 12
    }

    now = datetime.now()
    year = now.year

    date_from = datetime(year, months[month1], int(day1), 12, 0, 0)
    date_to = datetime(year, months[month2], int(day2), 12, 0, 0)

    print(f"Dates parsed: {date_from} → {date_to}")

    return date_from, date_to


def build_ics_url(date_from, date_to):
    def format_dt(dt):
        return dt.strftime("%d.%m.%Y %H:%M:%S")

    url = (
        f"{BASE_ICS_URL}/calendar_{GROUP}_"
        f"{format_dt(date_from)}_{format_dt(date_to)}.ics"
    )

    print("ICS URL:", url)
    return url


def download_ics(url):
    print("Downloading ICS...")

    r = requests.get(url, timeout=30)

    if r.status_code != 200 or "BEGIN:VCALENDAR" not in r.text:
        raise Exception("Не удалось скачать ICS")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(r.text)

    print("calendar.ics saved")


def push_to_github():
    print("Pushing to GitHub...")

    subprocess.run(["git", "add", "calendar.ics"])
    subprocess.run(["git", "commit", "-m", "update schedule"])
    subprocess.run(["git", "push"])

    print("Done")


# --- MAIN ---
try:
    date_from, date_to = get_dates_from_html()
    url = build_ics_url(date_from, date_to)
    download_ics(url)
    push_to_github()

except Exception as e:
    print("ERROR:", e)
