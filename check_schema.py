import sqlite3
conn = sqlite3.connect('d:\\.Job\\ai_news\\backend\\ai_news.db')
cur = conn.cursor()
cur.execute('PRAGMA table_info(sources)')
for col in cur.fetchall():
    print(col[1], col[2])
print('---monitor_configs---')
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='monitor_configs'")
print('Exists:', cur.fetchone() is not None)
print('---sample monitor sources---')
cur.execute("SELECT id, name, type, monitor_type, config FROM sources WHERE monitor_type IN ('keyword', 'account') LIMIT 5")
for row in cur.fetchall():
    print(row)
conn.close()
