"""
清空数据库中所有文章
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "ai_news.db")


def clear_articles():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 先删除 article_tags 关联表（如果有）
    try:
        cur.execute("DELETE FROM article_tags")
        print("Deleted article_tags")
    except sqlite3.OperationalError:
        pass  # 表不存在

    # 删除 articles 表
    cur.execute("DELETE FROM articles")
    print("Deleted all articles")

    conn.commit()
    conn.close()
    print("Done! All articles cleared.")


if __name__ == "__main__":
    clear_articles()

