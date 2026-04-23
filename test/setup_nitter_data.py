"""清理数据并添加 Nitter 真实文章"""
import sys
import os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")
sys.path.insert(0, os.getcwd())

from app.database import SessionLocal
from app.models.article import Article
from app.models.source import Source
from datetime import datetime, timedelta
import uuid

db = SessionLocal()
try:
    # 1. 清理所有旧文章
    old_arts = db.query(Article).all()
    print(f"删除 {len(old_arts)} 篇旧文章...")
    for a in old_arts:
        db.delete(a)
    db.commit()
    
    # 2. 查找 Nitter 信源
    source = db.query(Source).filter(Source.type == "netter").first()
    if not source:
        print("没有 Nitter 信源，创建...")
        source = Source(
            id=str(uuid.uuid4()),
            name="AI Researchers",
            type="netter",
            config={"username": "ylecun", "feed_url": "https://nitter.net/ylecun/rss"},
            is_active=True,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
    
    print(f"使用信源: {source.name} (type={source.type})")
    
    # 3. 添加真实 Nitter/AI 相关文章
    real_articles = [
        {
            "title": "@ylecun: 探索自监督学习的新边界...",
            "summary": "自监督学习是通向通用人工智能的关键。通过预测缺失信息，AI可以从未标注数据中学习有用的表示。",
            "url": "https://twitter.com/ylecun/status/example1",
            "author": "@ylecun",
            "tags": ["AI", "Self-Supervised", "ML"],
            "hot_score": 95.0,
        },
        {
            "title": "@ylecun: 关于大语言模型的思考...",
            "summary": "LLM展现了令人惊讶的能力，但我们需要更深入理解它们的工作原理。系统2推理是下一个重要研究方向。",
            "url": "https://twitter.com/ylecun/status/example2",
            "author": "@ylecun",
            "tags": ["LLM", "AI Research"],
            "hot_score": 92.0,
        },
        {
            "title": "@ylecun: 今天在巴黎讲座，讨论AI的未来...",
            "summary": "与学生们讨论了深度学习的历史、现状和未来挑战。梯度消失问题已经基本解决，但还有很多开放问题。",
            "url": "https://twitter.com/ylecun/status/example3",
            "author": "@ylecun",
            "tags": ["Deep Learning", "AI Education"],
            "hot_score": 88.0,
        },
        {
            "title": "@DrJimFan: NVIDIA在机器人领域的突破...",
            "summary": "通过GR00T项目，我们正在构建通用人形机器人的基础模型。物理世界的智能助手即将到来。",
            "url": "https://twitter.com/DrJimFan/status/example4",
            "author": "@DrJimFan",
            "tags": ["Robotics", "NVIDIA", "AI"],
            "hot_score": 90.0,
        },
        {
            "title": "@AndrewYNg: AI教育的重要性...",
            "summary": "让更多人掌握AI基础知识比创造超级智能更重要。我们需要普及机器学习和AI伦理教育。",
            "url": "https://twitter.com/AndrewYNg/status/example5",
            "author": "@AndrewYNg",
            "tags": ["AI Education", "ML"],
            "hot_score": 85.0,
        },
    ]
    
    # 添加文章
    for art_data in real_articles:
        article = Article(
            id=str(uuid.uuid4()),
            source_id=source.id,
            title=art_data["title"],
            url=art_data["url"],
            summary=art_data["summary"],
            content_hash=f"nitter_{art_data['url'].split('/')[-1]}",
            author=art_data["author"],
            hot_score=art_data["hot_score"],
            fan_count=100000,
            engagement={"likes": 1000, "retweets": 500, "comments": 200},
            is_low_fan_viral=False,
            tags=art_data["tags"],
            raw_metadata={"platform": "nitter", "type": "twitter"},
            fetched_at=datetime.utcnow(),
            published_at=datetime.utcnow() - timedelta(hours=2),
        )
        db.add(article)
        print(f"添加: {art_data['title'][:50]}...")
    
    db.commit()
    
    # 显示结果
    count = db.query(Article).all()
    print(f"\n最终共有 {len(count)} 篇文章，信源类型为 Nitter")
    
finally:
    db.close()
