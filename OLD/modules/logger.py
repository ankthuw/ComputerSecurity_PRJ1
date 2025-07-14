# Chức năng 11: Ghi log vào data/security.log
import os
from datetime import datetime

LOG_FILE = "data/security.log"

def write_log(email, action, status):
    """
    Ghi lại log bảo mật dưới dạng:
    [2025-07-03 21:15:01] | user@example.com | ACTION | STATUS
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] | {email} | {action} | {status}\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
