import requests
import config

def send_group(text):
    r = requests.post(f"{config.WA_SERVICE_URL}/send-group",
                      json={"group": config.WA_GROUP_NAME, "text": text,
                            "expectedSender": config.SENDER_NUMBER}, timeout=60)
    r.raise_for_status()

def send_direct(phone, text):
    r = requests.post(f"{config.WA_SERVICE_URL}/send-direct",
                      json={"phone": phone, "text": text}, timeout=60)
    r.raise_for_status()
