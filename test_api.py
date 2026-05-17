import httpx
import json
import time
import sqlite3

BASE = "http://localhost:8001"

# Check tables in database
conn = sqlite3.connect("D:/.Job/ai_news/backend/ai_news.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])
conn.close()

# Register a new unique user

reg_resp = httpx.post(f"{BASE}/api/auth/register", json={
    "email": f"1@1.com",
    "password": "testpass123",
    "nickname": "User1"
}, timeout=10)
print(f"Register: {reg_resp.status_code}")
if reg_resp.status_code != 200:
    print(f"Register failed: {reg_resp.text[:200]}")
    exit(1)
token = reg_resp.json()["access_token"]
print(f"Got token: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}

# 2. Test generate endpoint with verbose error capture
gen_data = {
    "source_content": "这是一段测试内容，关于AI大模型的发展。",
    "topic": "AI大模型",
    "style": "technical",
    "tone": "professional",
    "length": "short"
}
try:
    gen_resp = httpx.post(f"{BASE}/api/writer/generate", json=gen_data, headers=headers, timeout=60)
    print(f"Generate status: {gen_resp.status_code}")
    print(f"Response: {gen_resp.text[:2000]}")
    time.sleep(2)  # Wait for logs to flush
except Exception as e:
    print(f"Generate exception: {e}")
    time.sleep(2)
