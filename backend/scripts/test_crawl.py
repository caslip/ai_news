"""
手动抓取测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.crawler import RSSCrawler, GitHubCrawler, NitterCrawler
from app.services.celery_tasks import save_article
from app.models.source import Source

def crawl_all_sources():
    db = SessionLocal()
    crawler = RSSCrawler()
    
    try:
        # 获取所有活跃 RSS 信源
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        total_fetched = 0
        for source in sources:
            print(f"\n抓取: {source.name}")
            
            source_type = source.type.value if hasattr(source.type, 'value') else source.type
            
            if source_type == "rss":
                feed_url = source.config.get("feed_url")
                if not feed_url:
                    print(f"  跳过: 无 feed_url")
                    continue
                
                try:
                    articles = crawler.fetch_sync(feed_url)
                    print(f"  获取 {len(articles)} 篇文章")
                    
                    for article in articles:
                        if save_article(db, source.id, article):
                            total_fetched += 1
                    
                    print(f"  新增 {total_fetched} 篇")
                except Exception as e:
                    print(f"  错误: {e}")
            
            elif source_type == "github":
                org = source.config.get("org")
                repo = source.config.get("repo")
                if not org or not repo:
                    print(f"  跳过: 无 org/repo")
                    continue
                
                try:
                    gh_crawler = GitHubCrawler()
                    releases = gh_crawler.fetch_releases_sync(org, repo)
                    print(f"  获取 {len(releases)} 个 releases")
                    
                    for article in releases:
                        if save_article(db, source.id, article):
                            total_fetched += 1
                except Exception as e:
                    print(f"  错误: {e}")
            
            elif source_type == "netter":
                username = source.config.get("username")
                if not username:
                    print(f"  跳过: 无 username")
                    continue
                
                try:
                    nitter = NitterCrawler()
                    tweets = nitter.fetch_user_tweets_sync(username, max_results=20)
                    print(f"  获取 {len(tweets)} 条推文")
                    
                    for article in tweets:
                        if save_article(db, source.id, article):
                            total_fetched += 1
                except Exception as e:
                    print(f"  错误: {e}")
        
        print(f"\n总计新增文章: {total_fetched}")
        
    finally:
        db.close()

if __name__ == "__main__":
    crawl_all_sources()
