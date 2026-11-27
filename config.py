import os
from dotenv import load_dotenv
load_dotenv()

def _b(k, d="false"): return os.getenv(k, d).strip().lower() in ("1", "true", "yes")

SITE_URL = os.getenv("SITE_URL", "https://owner.emedix.co.in")
SITE_USERNAME = os.getenv("SITE_USERNAME", "")
SITE_PASSWORD = os.getenv("SITE_PASSWORD", "")
MENU_PATH = [p.strip() for p in os.getenv("MENU_PATH", "").split(">") if p.strip()]
DATE_DAYFIRST = _b("DATE_DAYFIRST", "false")
COL_NAME = os.getenv("COL_NAME", "").strip().lower()
COL_EXPIRY = os.getenv("COL_EXPIRY", "").strip().lower()
COL_PHONE = os.getenv("COL_PHONE", "").strip().lower()

SENDER_NUMBER = os.getenv("SENDER_NUMBER", "")
WA_GROUP_NAME = os.getenv("WA_GROUP_NAME", "")
WA_SERVICE_URL = os.getenv("WA_SERVICE_URL", "http://localhost:3000")
SEND_TO_CLIENTS = _b("SEND_TO_CLIENTS")

REMIND_DAYS = [int(x) for x in os.getenv("REMIND_DAYS", "7,3,1,0").split(",") if x.strip()]
NOTIFY_EXPIRED = _b("NOTIFY_EXPIRED", "true")
RUN_AT = os.getenv("RUN_AT", "09:00")
