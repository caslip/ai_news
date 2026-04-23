"""查看并清理测试数据"""
import sys
import os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")
sys.path.insert(0, os.getcwd())

from app.database import SessionLocal
from app.models.article import Article

db = SessionLocal()
try:
    arts = db.query(Article).all()
    print(f"数据库中共有 {len(arts)} 篇文章:\n")
    for a in arts:
        print(f"标题: {a.title}")
        print(f"URL: {a.url}")
        print(f"信源: {a.source_id}")
        print("-" * 50)
finally:
    db.close()
