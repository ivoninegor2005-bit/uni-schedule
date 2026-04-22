import requests
from bs4 import BeautifulSoup
import base64
import os

GROUP = "БХ-2331"
HTML_URL = f"https://uspu.ru/education/eios/schedule/?group_name={GROUP}"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "USERNAME/REPO_NAME"
FILE_PATH = "calendar.ics"

def get_dates():
    r = requests.get(HTML_URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    tag = soup.find("p", class_="rasp-zag rasp-zag-group")

    if not tag:
        raise Exception("No schedule header found")

    text = tag.text
    # "Расписание c 22 апреля по 13 мая"
    parts = text.split("c")[1].strip().split("по")

    start = parts[0].strip()
    end = parts[1].strip()

    return start, end

def download_ics(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text

def push_to_github(content):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    encoded = base64.b64encode(content.encode()).decode()

    r = requests.get(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })

    sha = None
    if r.status_code == 200:
        sha = r.json()["sha"]

    data = {
        "message": "update schedule",
        "content": encoded,
    }

    if sha:
        data["sha"] = sha

    r = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })

    r.raise_for_status()

def main():
    print("Getting dates...")
    start, end = get_dates()

    print("Building ICS URL...")
    ics_url = f"https://uspu.ru/education/eios/schedule/calendar/calendar_filter/calendar_{GROUP}_{start}_12:00:00_{end}_12:00:00.ics"

    print("Downloading ICS...")
    try:
        ics = download_ics(ics_url)
    except Exception as e:
        print("FAILED ICS, using fallback")
        ics = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"

    print("Uploading to GitHub...")
    push_to_github(ics)

    print("DONE")

if __name__ == "__main__":
    main()
