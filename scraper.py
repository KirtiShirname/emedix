"""Logs in to the owner portal and reads the client table dynamically."""
import logging
from dateutil import parser as dparser
from playwright.sync_api import sync_playwright
import config

log = logging.getLogger("scraper")

def _parse_date(text):
    try:
        return dparser.parse(text.strip(), dayfirst=True).date()
    except Exception:
        return None

def _find_col(headers, wanted):
    for i, h in enumerate(headers):
        if wanted in h.lower():
            return i
    return None

def fetch_clients(debug=False):
    clients = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not debug)
        page = browser.new_page()
        page.goto(config.SITE_URL, wait_until="networkidle")

        # --- login ---
        if config.SITE_USERNAME:
            page.locator("input[type=text], input[type=email]").first.fill(config.SITE_USERNAME)
        page.locator("input[type=password]").first.fill(config.SITE_PASSWORD)
        page.locator("button[type=submit], input[type=submit], button:has-text('Login'), button:has-text('Sign')").first.click()
        page.wait_for_load_state("networkidle")

        # --- navigate menu: Project > Clinical Assistant ---
        for item in config.MENU_PATH:
            page.get_by_text(item, exact=False).first.click()
            page.wait_for_load_state("networkidle")

        page.wait_for_selector("table", timeout=20000)
        if debug:
            page.screenshot(path="debug.png", full_page=True)
            open("debug.html", "w", encoding="utf-8").write(page.content())

        # --- read table (handles pagination via 'Next' button if present) ---
        while True:
            table = page.locator("table").first
            headers = [h.strip() for h in table.locator("thead th, tr:first-child th").all_inner_texts()]
            i_name = _find_col(headers, config.COL_NAME)
            i_exp = _find_col(headers, config.COL_EXPIRY)
            i_ph = _find_col(headers, config.COL_PHONE)
            if i_name is None or i_exp is None:
                raise RuntimeError(f"Columns not found. Headers seen: {headers}. Fix COL_NAME/COL_EXPIRY in .env")

            for row in table.locator("tbody tr").all():
                cells = [c.strip() for c in row.locator("td").all_inner_texts()]
                if len(cells) <= max(i_name, i_exp):
                    continue
                clients.append({
                    "name": cells[i_name],
                    "expiry": _parse_date(cells[i_exp]),
                    "phone": cells[i_ph] if i_ph is not None and i_ph < len(cells) else "",
                })

            nxt = page.locator("a:has-text('Next'), button:has-text('Next')").first
            if nxt.count() and nxt.is_enabled() and "disabled" not in (nxt.get_attribute("class") or ""):
                nxt.click(); page.wait_for_load_state("networkidle")
            else:
                break
        browser.close()

    log.info("Fetched %d clients", len(clients))
    return clients
