import sqlite3
import json

conn = sqlite3.connect('ai_news.db')
cur = conn.cursor()

# Check articles from twitter/nitter sources
cur.execute('''
    SELECT a.id, a.title, a.url, a.author, a.published_at, a.engagement, s.type
    FROM articles a
    LEFT JOIN sources s ON a.source_id = s.id
    WHERE s.type IN ('twitter', 'netter')
    ORDER BY a.published_at DESC
    LIMIT 30
''')
rows = cur.fetchall()
print(f'Articles from Twitter/Nitter sources: {len(rows)}')
for row in rows[:10]:
    engagement = json.loads(row[5]) if row[5] else {}
    print(f'  [{row[6]}] {row[1][:60]}... | {row[4]} | likes={engagement.get("likes", 0)}')

# Check sources
cur.execute('SELECT id, name, type, config FROM sources WHERE type IN ("twitter", "netter")')
sources = cur.fetchall()
print(f'\nSources (twitter/netter): {len(sources)}')
for s in sources:
    print(f'  {s[1]} | type={s[2]} | config={s[3]}')

conn.close()
