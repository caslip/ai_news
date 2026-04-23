"""
快速测试 RSS 抓取
"""
import sys
import os

# 设置工作目录
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")
sys.path.insert(0, os.getcwd())

from app.services.crawler import RSSCrawler

def test_rss_crawl():
    crawler = RSSCrawler()

    # 测试抓取 Hacker News
    print("抓取 Hacker News...")
    try:
        articles = crawler.fetch_sync("https://hnrss.org/frontpage")
        print(f"获取 {len(articles)} 篇文章")
        for i, a in enumerate(articles[:3]):
            print(f"  {i+1}. {a.title[:60]}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试抓取 ArXiv AI
    print("\n抓取 ArXiv AI...")
    try:
        articles = crawler.fetch_sync("http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending")
        print(f"获取 {len(articles)} 篇文章")
        for i, a in enumerate(articles[:3]):
            print(f"  {i+1}. {a.title[:60]}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_rss_crawl()
