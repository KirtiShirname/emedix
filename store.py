import sqlite3
_db = sqlite3.connect("sent.db")
_db.execute("CREATE TABLE IF NOT EXISTS sent (k TEXT PRIMARY KEY)")

def was_sent(k): return _db.execute("SELECT 1 FROM sent WHERE k=?", (k,)).fetchone() is not None
def mark_sent(k):
    _db.execute("INSERT OR IGNORE INTO sent VALUES (?)", (k,)); _db.commit()
