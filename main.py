import argparse, logging, re, traceback
from apscheduler.schedulers.blocking import BlockingScheduler
import config, scraper, logic, store, sender

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("agent")

def run_once(debug=False, dry=False):
    try:
        clients = scraper.fetch_clients(debug=debug)
    except Exception:
        log.error("Scrape failed:\n%s", traceback.format_exc())
        try: sender.send_group("⚠️ Reminder agent: could not read client list. Please check the portal login/layout.")
        except Exception: pass
        return
    for r in logic.build_reminders(clients):
        if store.was_sent(r["key"]):
            continue
        if dry:
            print("[DRY RUN]", r["text"]); continue
        try:
            sender.send_group(r["text"])
            phone = re.sub(r"\D", "", r["client"]["phone"])
            if config.SEND_TO_CLIENTS and phone:
                sender.send_direct(phone, r["text"])
            store.mark_sent(r["key"])
            log.info("Sent: %s", r["client"]["name"])
        except Exception:
            log.error("Send failed for %s:\n%s", r["client"]["name"], traceback.format_exc())

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--daemon", action="store_true", help="run daily at RUN_AT")
    ap.add_argument("--debug", action="store_true", help="visible browser + save debug.png/html")
    ap.add_argument("--dry-run", action="store_true", help="print messages, don't send")
    a = ap.parse_args()
    if a.daemon:
        h, m = config.RUN_AT.split(":")
        s = BlockingScheduler()
        s.add_job(run_once, "cron", hour=int(h), minute=int(m))
        log.info("Scheduled daily at %s", config.RUN_AT)
        s.start()
    else:
        run_once(debug=a.debug, dry=a.dry_run)
