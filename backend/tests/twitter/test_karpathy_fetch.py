"""
test_karpathy_fetch.py - Test script for fetching tweets from @karpathy using Nitter RSS

This script:
1. Fetches tweets from @karpathy using Nitter RSS
2. Filters tweets from today (2026-04-23)
3. Saves results to a markdown file
"""

import sys
import os
from datetime import datetime, date
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.crawler import NitterCrawler, ParsedArticle


def format_engagement(engagement: dict) -> str:
    """Format engagement stats for display."""
    likes = engagement.get("likes", 0)
    retweets = engagement.get("retweets", 0)
    comments = engagement.get("comments", 0)
    return f"❤️ {likes:,} | 🔁 {retweets:,} | 💬 {comments:,}"


def format_timestamp(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def tweet_to_markdown(article: ParsedArticle, index: int) -> str:
    """Convert a ParsedArticle to markdown format."""
    lines = [
        f"### Tweet {index}: @{article.author[1:]}",
        "",
        f"**Published:** {format_timestamp(article.published_at)}",
        "",
        f"**Engagement:** {format_engagement(article.engagement)}",
        "",
        f"**Tweet URL:** {article.url}",
        "",
        "**Content:**",
        "",
        article.content if article.content else article.title,
        "",
        "---",
    ]
    return "\n".join(lines)


def main():
    # Configuration
    USERNAME = "karpathy"
    TARGET_DATE = date(2026, 4, 23)  # Today's date
    MAX_RESULTS = 30  # Fetch up to 30 tweets
    OUTPUT_DIR = Path(__file__).parent
    OUTPUT_FILE = OUTPUT_DIR / f"karpathy_tweets_{TARGET_DATE.isoformat()}.md"
    
    print(f"=" * 60)
    print(f"Twitter Crawling Test - @karpathy via Nitter RSS")
    print(f"=" * 60)
    print(f"Target Date: {TARGET_DATE}")
    print(f"Fetching up to {MAX_RESULTS} tweets...")
    print()
    
    # Initialize crawler
    crawler = NitterCrawler(timeout=30)
    
    # Fetch tweets synchronously
    print("Fetching tweets from Nitter RSS...")
    try:
        articles = crawler.fetch_user_tweets_sync(
            username=USERNAME,
            max_results=MAX_RESULTS,
            source_type_override="twitter"
        )
        print(f"Fetched {len(articles)} total tweets")
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return
    
    # Filter tweets from today
    today_tweets = [
        article for article in articles
        if article.published_at.date() == TARGET_DATE
    ]
    
    print(f"Tweets from today ({TARGET_DATE}): {len(today_tweets)}")
    print()
    
    # Generate markdown content
    md_lines = [
        f"# @{USERNAME} Tweets - {TARGET_DATE}",
        "",
        "## Summary",
        "",
        f"- **Account:** @{USERNAME}",
        f"- **Date:** {TARGET_DATE}",
        f"- **Total Tweets Fetched:** {len(articles)}",
        f"- **Tweets from Today:** {len(today_tweets)}",
        f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
    ]
    
    # Add today's tweets section
    if today_tweets:
        md_lines.extend([
            "## Today's Tweets",
            "",
        ])
        
        for i, article in enumerate(today_tweets, 1):
            md_lines.append(tweet_to_markdown(article, i))
    else:
        md_lines.extend([
            "## Today's Tweets",
            "",
            "*No tweets found from today.*",
            "",
        ])
    
    # Add engagement summary
    if today_tweets:
        total_likes = sum(t.engagement.get("likes", 0) for t in today_tweets)
        total_retweets = sum(t.engagement.get("retweets", 0) for t in today_tweets)
        total_comments = sum(t.engagement.get("comments", 0) for t in today_tweets)
        
        md_lines.extend([
            "## Today's Engagement Summary",
            "",
            f"- **Total Likes:** {total_likes:,}",
            f"- **Total Retweets:** {total_retweets:,}",
            f"- **Total Comments:** {total_comments:,}",
            f"- **Avg Likes per Tweet:** {total_likes / len(today_tweets):.1f}",
            f"- **Avg Retweets per Tweet:** {total_retweets / len(today_tweets):.1f}",
            "",
        ])
    
    # Add all fetched tweets for reference (with date filter note)
    md_lines.extend([
        "## All Fetched Tweets (for reference)",
        "",
        f"*Note: Showing all {len(articles)} tweets fetched from RSS. Today's tweets are filtered above.*",
        "",
    ])
    
    for i, article in enumerate(articles, 1):
        tweet_date = article.published_at.strftime("%Y-%m-%d")
        date_marker = " **[TODAY]**" if article.published_at.date() == TARGET_DATE else ""
        md_lines.append(f"- [{tweet_date}] {article.content[:80]}...{date_marker}" if len(article.content) > 80 else f"- [{tweet_date}] {article.content}{date_marker}")
    
    # Write to file
    md_content = "\n".join(md_lines)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"=" * 60)
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"=" * 60)
    print()
    print(f"Summary:")
    print(f"  - Total tweets fetched: {len(articles)}")
    print(f"  - Tweets from {TARGET_DATE}: {len(today_tweets)}")
    print()
    
    # Print today's tweets to console as well
    if today_tweets:
        print("Today's Tweets:")
        print("-" * 60)
        for i, article in enumerate(today_tweets, 1):
            print(f"\n[{i}] {format_timestamp(article.published_at)}")
            print(f"    {article.content}")
            print(f"    {format_engagement(article.engagement)}")
    else:
        print("No tweets from today found.")
    
    return len(articles), len(today_tweets)


if __name__ == "__main__":
    total, today_count = main()
    sys.exit(0)
