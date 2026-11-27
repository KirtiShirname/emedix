"""Logs in to the owner portal and reads whatever client list is shown (dynamic)."""
import logging
from dateutil import parser as dparser
from playwright.sync_api import sync_playwright
import config

log = logging.getLogger("scraper")


def _parse_date(text):
    try:
        return dparser.parse(text.strip(), dayfirst=config.DATE_DAYFIRST).date()
    except Exception:
        return None


def _col_index(spec, headers):
    """spec = a column number (0,1,2..) or part of the header text."""
    if not spec:
        return None
    if spec.isdigit():
        return int(spec)
    for i, h in enumerate(headers):
        if spec in h.lower():
            return i
    return None


def _login(page):
    page.goto(config.SITE_URL, wait_until="load", timeout=60000)
    if config.SITE_USERNAME:
        page.locator("input[type=text], input[type=email]").first.fill(config.SITE_USERNAME)
    page.locator("#loginPw").fill(config.SITE_PASSWORD)
    page.get_by_role("button", name="Unlock").click()
    page.wait_for_timeout(5000)


def _open_menu(page):
    for item in config.MENU_PATH:
        try:
            page.get_by_text(item, exact=False).locator("visible=true").first.click(timeout=5000)
            page.wait_for_timeout(2500)
        except Exception:
            log.warning("Menu item '%s' not found/clickable - continuing with current page", item)


def _best_table(page):
    """The client list = the visible table with the most rows."""
    page.wait_for_selector("table", timeout=20000)
    best, best_n = None, -1
    for t in page.locator("table").all():
        if not t.is_visible():
            continue
        n = t.locator("tbody tr, tr").count()
        if n > best_n:
            best, best_n = t, n
    if best is None:
        raise RuntimeError("No visible table found on the page")
    return best


def _read_table(table):
    headers = [h.strip() for h in table.locator("thead th, thead td").all_inner_texts()]
    rows = []
    for tr in table.locator("tbody tr").all():
        cells = [" ".join(c.split()) for c in tr.locator("td").all_inner_texts()]
        if cells:
            rows.append(cells)
    if not rows:  # table with no tbody
        for tr in table.locator("tr").all():
            cells = [" ".join(c.split()) for c in tr.locator("td").all_inner_texts()]
            if cells:
                rows.append(cells)
    return headers, rows


def discover():
    """Print the table with column NUMBERS so you can pick name / expiry columns."""
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(20000)
        _login(page)
        _open_menu(page)
        page.screenshot(path="discover.png", full_page=True)
        headers, rows = _read_table(_best_table(page))
        print("\n=== HEADERS (number: text) ===")
        for i, h in enumerate(headers):
            print(f"  {i}: {h!r}")
        print(f"\n=== FIRST ROWS (total {len(rows)}) ===")
        for r in rows[:4]:
            print("-" * 60)
            for i, c in enumerate(r):
                print(f"  {i}: {c[:70]!r}")
        b.close()


def fetch_clients(debug=False):
    clients = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(20000)
        try:
            _login(page)
            _open_menu(page)
            while True:
                headers, rows = _read_table(_best_table(page))
                i_name = _col_index(config.COL_NAME, headers)
                i_exp = _col_index(config.COL_EXPIRY, headers)
                i_ph = _col_index(config.COL_PHONE, headers)
                if i_name is None or i_exp is None:
                    raise RuntimeError(
                        f"Columns not found. Headers seen: {headers}. "
                        "Run 'python scraper.py' and set COL_NAME / COL_EXPIRY (name or number) in .env")
                for cells in rows:
                    if len(cells) <= max(i_name, i_exp):
                        continue
                    clients.append({
                        "name": cells[i_name],
                        "expiry": _parse_date(cells[i_exp]),
                        "phone": cells[i_ph] if i_ph is not None and i_ph < len(cells) else "",
                    })
                nxt = page.locator("a:has-text('Next'), button:has-text('Next')").first
                if nxt.count() and nxt.is_enabled() and "disabled" not in (nxt.get_attribute("class") or ""):
                    nxt.click(); page.wait_for_timeout(2000)
                else:
                    break
        except Exception:
            page.screenshot(path="failed.png", full_page=True)
            raise
        finally:
            browser.close()
    log.info("Fetched %d clients", len(clients))
    return clients


if __name__ == "__main__":
    discover()
