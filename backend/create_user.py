"""
Quick script to create a new user in the database.
Run from the backend directory: python create_user.py
"""
import sys
import uuid
from datetime import datetime

# Add the backend dir to path so we can import app modules
sys.path.insert(0, ".")

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User

# Use the same database as the app
DATABASE_URL = "sqlite:///./ai_news.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "1@1.com").first()
        if existing:
            print(f"User with email 1@1.com already exists (id={existing.id})")
            return

        # Hash password
        password_hash = pwd_context.hash("123")
        print(f"Password hash: {password_hash}")

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email="1@1.com",
            nickname="User1",
            password_hash=password_hash,
            role="user",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"User created successfully!")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Nickname: {user.nickname}")
        print(f"  Role: {user.role}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
