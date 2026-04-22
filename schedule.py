from playwright.sync_api import sync_playwright

URL = "https://uspu.ru/education/eios/schedule/?group_name=БХ-2331"

OUTPUT_FILE = "calendar.ics"


def download_ics():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(URL, wait_until="networkidle")

        # ждём, чтобы страница точно дорендерилась
        page.wait_for_timeout(3000)

        # ищем ссылку на ICS (как в браузере)
        download_link = page.locator("a[href*='calendar_filter']").first

        if download_link.count() == 0:
            raise Exception("ICS ссылка не найдена")

        with page.expect_download() as download_info:
            download_link.click()

        download = download_info.value
        download.save_as(OUTPUT_FILE)

        browser.close()

        print("OK: ICS скачан")


if __name__ == "__main__":
    download_ics()