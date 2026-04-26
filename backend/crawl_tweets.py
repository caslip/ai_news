"""
触发推文抓取脚本
用于将推文从 Nitter 抓取并保存到数据库
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.source import Source
from app.services.crawler import NitterCrawler, article_to_dict
from app.services.celery_tasks import save_article
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crawl_twitter_source(db, source):
    """抓取单个 Twitter 信源"""
    account = source.config.get("account", "").lstrip("@")
    if not account:
        logger.warning(f"Twitter source {source.name} has no account configured")
        return 0
    
    logger.info(f"Crawling Twitter source: {source.name} (@{account})")
    
    try:
        crawler = NitterCrawler()
        tweets = crawler.fetch_user_tweets_sync(account, max_results=20, source_type_override="twitter")
        
        saved_count = 0
        for article_data in tweets:
            if save_article(db, source.id, article_data):
                saved_count += 1
        
        source.last_fetched_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"  Fetched {len(tweets)} tweets, saved {saved_count} new articles")
        return saved_count
        
    except Exception as e:
        logger.error(f"  Failed to crawl {source.name}: {e}")
        db.rollback()
        return 0

def crawl_netter_source(db, source):
    """抓取单个 Nitter 信源"""
    username = source.config.get("username", "")
    if not username:
        logger.warning(f"Nitter source {source.name} has no username configured")
        return 0
    
    logger.info(f"Crawling Nitter source: {source.name} (@{username})")
    
    try:
        crawler = NitterCrawler()
        tweets = crawler.fetch_user_tweets_sync(username, max_results=20)
        
        saved_count = 0
        for article_data in tweets:
            if save_article(db, source.id, article_data):
                saved_count += 1
        
        source.last_fetched_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"  Fetched {len(tweets)} tweets, saved {saved_count} new articles")
        return saved_count
        
    except Exception as e:
        logger.error(f"  Failed to crawl {source.name}: {e}")
        db.rollback()
        return 0

def main():
    db = SessionLocal()
    
    try:
        # 获取所有活跃的信源
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        print("\n" + "="*60)
        print("TWEET CRAWLER - Starting crawl")
        print("="*60 + "\n")
        
        total_saved = 0
        
        for source in sources:
            if source.type == "twitter":
                saved = crawl_twitter_source(db, source)
                total_saved += saved
            elif source.type == "netter":
                saved = crawl_netter_source(db, source)
                total_saved += saved
        
        print("\n" + "="*60)
        print(f"CRAWL COMPLETE - Total new articles saved: {total_saved}")
        print("="*60 + "\n")
        
        # 显示抓取后的统计
        from app.models.article import Article
        from sqlalchemy import func
        
        twitter_count = db.query(func.count(Article.id)).join(Source).filter(Source.type == 'twitter').scalar()
        netter_count = db.query(func.count(Article.id)).join(Source).filter(Source.type == 'netter').scalar()
        total_count = db.query(func.count(Article.id)).scalar()
        
        print("Database Summary:")
        print(f"  Twitter articles: {twitter_count}")
        print(f"  Netter articles: {netter_count}")
        print(f"  Total articles: {total_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
