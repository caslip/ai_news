"""
种子数据 - 论文信源初始化

运行方式：python -m backend.seed_paper_sources
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.source import Source

# 确保表已创建
Base.metadata.create_all(bind=engine)


def seed_paper_sources():
    db = SessionLocal()
    try:
        sources = [
            # Arxiv RSS 信源
            {
                "name": "Arxiv cs.AI",
                "type": "arxiv",
                "config": {"feed_url": "http://export.arxiv.org/rss/cs.AI"},
            },
            {
                "name": "Arxiv cs.LG",
                "type": "arxiv",
                "config": {"feed_url": "http://export.arxiv.org/rss/cs.LG"},
            },
            {
                "name": "Arxiv cs.CL",
                "type": "arxiv",
                "config": {"feed_url": "http://export.arxiv.org/rss/cs.CL"},
            },
            {
                "name": "Arxiv cs.CV",
                "type": "arxiv",
                "config": {"feed_url": "http://export.arxiv.org/rss/cs.CV"},
            },
            {
                "name": "Arxiv cs.RO",
                "type": "arxiv",
                "config": {"feed_url": "http://export.arxiv.org/rss/cs.RO"},
            },
            # HuggingFace Paper 信源
            {
                "name": "HuggingFace Papers",
                "type": "hf_paper",
                "config": {"sort": "hfulike", "limit": 50},
            },
        ]

        created = 0
        skipped = 0
        for s in sources:
            existing = db.query(Source).filter(
                Source.name == s["name"],
                Source.type == s["type"],
            ).first()
            if existing:
                print(f"  跳过（已存在）: {s['name']}")
                skipped += 1
                continue
            source = Source(**s)
            db.add(source)
            print(f"  创建: {s['name']} ({s['type']})")
            created += 1

        db.commit()
        print(f"\n完成：新建 {created} 个信源，跳过 {skipped} 个（已存在）")

    finally:
        db.close()


if __name__ == "__main__":
    print("开始创建论文信源...")
    seed_paper_sources()
