from datetime import date
import config

def build_reminders(clients):
    out = []
    today = date.today()
    for c in clients:
        if not c["expiry"]:
            continue
        d = (c["expiry"] - today).days
        if d in config.REMIND_DAYS:
            if d == 0:
                when = "expires today"
            else:
                when = f"is expiring in {d} day{'s' if d != 1 else ''}"
            msg = (f"Reminder: The premium plan of *{c['name']}* {when} "
                   f"(expiry: {c['expiry']:%d-%b-%Y}). Please make the payment to continue using the service.")
        elif d < 0 and config.NOTIFY_EXPIRED:
            msg = (f"Alert: The premium plan of *{c['name']}* expired {abs(d)} day(s) ago "
                   f"({c['expiry']:%d-%b-%Y}). Please make the payment to continue using the service.")
        else:
            continue
        out.append({"client": c, "days_left": d, "text": msg,
                    "key": f"{c['name']}|{c['expiry']}|{d}|{today}"})
    return out
