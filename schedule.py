from playwright.sync_api import sync_playwright

URL = "https://uspu.ru/education/eios/schedule/?group_name=БХ-2331"

def download_ics():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # ❗ ВАЖНО: НЕ networkidle
        page.goto(URL, wait_until="domcontentloaded")

        # даём JS догрузиться вручную
        page.wait_for_timeout(5000)

        # ищем ссылку на ICS
        link = page.locator("a[href*='calendar_filter']").first

        if link.count() == 0:
            raise Exception("ICS ссылка не найдена")

        with page.expect_download() as download_info:
            link.click()

        download = download_info.value
        download.save_as("calendar.ics")

        browser.close()

        print("OK")

if __name__ == "__main__":
    download_ics()

for i in range(3):
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        break
    except:
        page.wait_for_timeout(2000)