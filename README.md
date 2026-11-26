# Emedix Subscription Reminder Agent

## Setup
1. `cp .env.example .env` and fill in values (set WA_GROUP_NAME exactly as in WhatsApp).
2. Python: `pip install -r requirements.txt && playwright install chromium`
3. WhatsApp service: `cd whatsapp-service && npm install && node server.js`
   Scan the QR with the business number (9665328953). Session is saved in ./session.
   The number must already be a member of the group.
4. First test: `python main.py --debug --dry-run`
   (opens a visible browser, saves debug.png / debug.html, prints messages without sending)
5. Real run: `python main.py` | Daily scheduler: `python main.py --daemon`

## Changing things (no code edits)
- New sender number: change SENDER_NUMBER, delete ./session, re-scan QR.
- New group: change WA_GROUP_NAME.
- Reminder days: REMIND_DAYS=7,3,1,0
- Clients are read live from the portal each run, so new/changed clients are picked up automatically.

## Notes
- If the table columns have different names, fix COL_NAME / COL_EXPIRY / COL_PHONE.
- whatsapp-web.js is unofficial; use only this dedicated business number, avoid bulk/spammy sending.
