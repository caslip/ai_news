"""
手动测试脚本 - 模拟添加测试数据并验证页面显示
"""
import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")
sys.path.insert(0, os.getcwd())

from app.database import SessionLocal
from app.models.article import Article
from app.models.source import Source
from datetime import datetime, timedelta
import uuid


def add_test_articles():
    """添加测试文章数据"""
    db = SessionLocal()
    
    try:
        # 打印所有信源
        sources = db.query(Source).all()
        print(f"数据库中共有 {len(sources)} 个信源:")
        for s in sources:
            print(f"  - {s.name} (type={s.type}, is_active={s.is_active})")
        
        # 获取一个信源
        source = db.query(Source).first()
        if not source:
            print("没有找到任何信源")
            return
        
        print(f"\n使用信源: {source.name} (type={source.type})")
        
        # 添加测试文章
        test_articles = [
            {
                "title": "OpenAI 发布 GPT-5，带来革命性突破",
                "summary": "OpenAI 今日发布了 GPT-5 模型，在推理能力和多模态理解方面实现了质的飞跃。",
                "url": "https://example.com/gpt5-release",
                "source_name": source.name,
            },
            {
                "title": "Anthropic 推出 Claude 4，性能超越 GPT-4",
                "summary": "Anthropic 发布了 Claude 4，在长文本理解和代码生成方面表现优异。",
                "url": "https://example.com/claude4-release",
                "source_name": source.name,
            },
            {
                "title": "Meta 开源 Llama 3，性能匹敌 GPT-4",
                "summary": "Meta 发布了 Llama 3 开源大模型，性能可以与闭源模型相媲美。",
                "url": "https://example.com/llama3-release",
                "source_name": source.name,
            },
            {
                "title": "Google 发布 Gemini 2.0，性能大幅提升",
                "summary": "Google DeepMind 发布了 Gemini 2.0，在多个基准测试中刷新纪录。",
                "url": "https://example.com/gemini2-release",
                "source_name": source.name,
            },
            {
                "title": "特斯拉发布自动驾驶新突破",
                "summary": "特斯拉在自动驾驶领域取得重大突破，展示了完全无人驾驶技术。",
                "url": "https://example.com/tesla-fsd",
                "source_name": source.name,
            },
        ]
        
        added_count = 0
        for article_data in test_articles:
            # 检查是否已存在
            existing = db.query(Article).filter(Article.url == article_data["url"]).first()
            if existing:
                print(f"文章已存在: {article_data['title']}")
                continue
            
            article = Article(
                id=str(uuid.uuid4()),
                source_id=source.id,
                title=article_data["title"],
                url=article_data["url"],
                summary=article_data["summary"],
                content_hash=f"hash_{article_data['url']}",
                author="Test Author",
                hot_score=85.5,
                fan_count=1000,
                engagement={"likes": 100, "retweets": 50, "comments": 20},
                is_low_fan_viral=False,
                tags=["AI", "LLM", "OpenAI"],
                raw_metadata={"source": "test"},
                fetched_at=datetime.utcnow(),
                published_at=datetime.utcnow() - timedelta(hours=2),
            )
            db.add(article)
            added_count += 1
            print(f"添加文章: {article_data['title']}")
        
        db.commit()
        print(f"\n成功添加 {added_count} 篇测试文章")
        
        # 验证数据
        count = db.query(Article).count()
        print(f"数据库中共有 {count} 篇文章")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_test_articles()
