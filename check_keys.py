import sqlite3
import os

db_path = r"d:\.Job\ai_news\backend\ai_news.db"
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", [t[0] for t in tables])

if ("api_keys",) in tables:
    cur.execute("SELECT id, user_id, provider, label, is_active FROM api_keys")
    rows = cur.fetchall()
    print(f"API Keys: {len(rows)} found")
    for r in rows:
        print(f"  - id={r[0]}, user_id={r[1]}, provider={r[2]}, label={r[3]}, is_active={r[4]}")
else:
    print("No api_keys table found")

conn.close()
