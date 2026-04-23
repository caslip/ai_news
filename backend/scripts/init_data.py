"""
数据初始化脚本 - 添加默认信源
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.source import Source, SourceType
from app.models.user import User, UserRole
from passlib.context import CryptContext


# 默认 RSS 信源
DEFAULT_RSS_SOURCES = [
    {
        "name": "Hacker News",
        "type": SourceType.RSS,
        "config": {"feed_url": "https://hnrss.org/frontpage"},
        "description": "科技和创业热点"
    },
    {
        "name": "MIT Technology Review",
        "type": SourceType.RSS,
        "config": {"feed_url": "https://www.technologyreview.com/feed/"},
        "description": "MIT科技评论"
    },
    {
        "name": "TechCrunch",
        "type": SourceType.RSS,
        "config": {"feed_url": "https://techcrunch.com/feed/"},
        "description": "科技创业新闻"
    },
    {
        "name": "The Verge",
        "type": SourceType.RSS,
        "config": {"feed_url": "https://www.theverge.com/rss/index.xml"},
        "description": "科技和数字文化"
    },
    {
        "name": "ArXiv AI",
        "type": SourceType.RSS,
        "config": {"feed_url": "http://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending"},
        "description": "ArXiv 人工智能论文"
    },
]

# 默认 GitHub 信源
DEFAULT_GITHUB_SOURCES = [
    {
        "name": "LangChain",
        "type": SourceType.GITHUB,
        "config": {"org": "langchain-ai", "repo": "langchain"},
        "description": "LangChain 框架发布"
    },
    {
        "name": "vLLM",
        "type": SourceType.GITHUB,
        "config": {"org": "vllm-project", "repo": "vllm"},
        "description": "vLLM 高效推理引擎发布"
    },
    {
        "name": "Ollama",
        "type": SourceType.GITHUB,
        "config": {"org": "ollama", "repo": "ollama"},
        "description": "Ollama 本地LLM运行器发布"
    },
    {
        "name": "AutoGPT",
        "type": SourceType.GITHUB,
        "config": {"org": "Significant-Gravitas", "repo": "AutoGPT"},
        "description": "AutoGPT 发布动态"
    },
    {
        "name": "Next.js",
        "type": SourceType.GITHUB,
        "config": {"org": "vercel", "repo": "next.js"},
        "description": "Next.js 框架发布"
    },
    {
        "name": "Llama.cpp",
        "type": SourceType.GITHUB,
        "config": {"org": "ggerganov", "repo": "llama.cpp"},
        "description": "Llama.cpp 发布"
    },
]

# 默认 Twitter 监控账号（需要 Twitter API Token）
DEFAULT_TWITTER_SOURCES = [
    {
        "name": "Sam Altman",
        "type": SourceType.TWITTER,
        "config": {"account": "@sama"},
        "description": "OpenAI CEO"
    },
    {
        "name": "Yann LeCun",
        "type": SourceType.TWITTER,
        "config": {"account": "@ylecun"},
        "description": "Meta AI 首席科学家"
    },
    {
        "name": "Andrew Ng",
        "type": SourceType.TWITTER,
        "config": {"account": "@AndrewYNg"},
        "description": "AI 教育家"
    },
    {
        "name": "Jim Fan",
        "type": SourceType.TWITTER,
        "config": {"account": "@DrJimFan"},
        "description": "NVIDIA AI 科学家"
    },
]


def create_admin_user(db: SessionLocal) -> User:
    """创建管理员用户"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # 检查是否已存在
    admin = db.query(User).filter(User.email == "admin@ai-news.local").first()
    if admin:
        print("管理员用户已存在")
        return admin
    
    admin = User(
        email="admin@ai-news.local",
        nickname="Admin",
        password_hash=pwd_context.hash("admin123"),
        role=UserRole.ADMIN.value,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("管理员用户创建成功: admin@ai-news.local / admin123")
    return admin


def create_sources(db: SessionLocal, created_by: str):
    """创建默认信源"""
    sources_created = 0
    
    # RSS 信源
    for source_data in DEFAULT_RSS_SOURCES:
        existing = db.query(Source).filter(
            Source.name == source_data["name"],
            Source.type == source_data["type"]
        ).first()
        
        if existing:
            print(f"RSS 信源已存在: {source_data['name']}")
            continue
        
        source = Source(
            name=source_data["name"],
            type=source_data["type"],
            config=source_data["config"],
            is_active=True,
            created_by=created_by,
        )
        db.add(source)
        sources_created += 1
        print(f"添加 RSS 信源: {source_data['name']}")
    
    # GitHub 信源
    for source_data in DEFAULT_GITHUB_SOURCES:
        existing = db.query(Source).filter(
            Source.name == source_data["name"],
            Source.type == source_data["type"]
        ).first()
        
        if existing:
            print(f"GitHub 信源已存在: {source_data['name']}")
            continue
        
        source = Source(
            name=source_data["name"],
            type=source_data["type"],
            config=source_data["config"],
            is_active=True,
            created_by=created_by,
        )
        db.add(source)
        sources_created += 1
        print(f"添加 GitHub 信源: {source_data['name']}")
    
    # Twitter 信源（如果配置了 Token）
    twitter_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if twitter_token:
        for source_data in DEFAULT_TWITTER_SOURCES:
            existing = db.query(Source).filter(
                Source.name == source_data["name"],
                Source.type == source_data["type"]
            ).first()
            
            if existing:
                print(f"Twitter 信源已存在: {source_data['name']}")
                continue
            
            source = Source(
                name=source_data["name"],
                type=source_data["type"],
                config=source_data["config"],
                is_active=True,
                created_by=created_by,
            )
            db.add(source)
            sources_created += 1
            print(f"添加 Twitter 信源: {source_data['name']}")
    else:
        print("\n注意: 未配置 TWITTER_BEARER_TOKEN，跳过 Twitter 信源")
    
    db.commit()
    return sources_created


def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("AI News 数据初始化")
    print("=" * 50)
    
    # 创建表
    print("\n创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 创建管理员
        print("\n创建管理员用户...")
        admin = create_admin_user(db)
        
        # 创建默认信源
        print("\n创建默认信源...")
        sources_count = create_sources(db, admin.id)
        
        print("\n" + "=" * 50)
        print(f"初始化完成！")
        print(f"创建了 {sources_count} 个新信源")
        print("=" * 50)
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
