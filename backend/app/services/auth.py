from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import uuid
import httpx
from app.models.user import User, UserRole, OAuthProvider
from app.schemas.user import UserCreate, UserRegisterRequest, UserResponse, TokenData
from app.config import settings
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_oauth(self, provider: OAuthProvider, oauth_id: str) -> Optional[User]:
        return self.db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id
        ).first()

    def create_user(self, user_data: UserRegisterRequest) -> User:
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            nickname=user_data.nickname,
            password_hash=hashed_password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def create_oauth_user(
        self,
        email: str,
        nickname: str,
        avatar_url: Optional[str],
        provider: OAuthProvider,
        oauth_id: str,
    ) -> User:
        db_user = User(
            email=email,
            nickname=nickname,
            avatar_url=avatar_url,
            oauth_provider=provider,
            oauth_id=oauth_id,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not user.password_hash:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
        })
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role", "user")
            if user_id is None:
                return None
            return TokenData(
                user_id=user_id,
                email=email,
                role=UserRole(role)
            )
        except ExpiredSignatureError:
            return None
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        return self.get_user_by_id(token_data.user_id)


class GitHubOAuthService:
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "scope": "read:user user:email",
        }
        if state:
            params["state"] = state
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.GITHUB_AUTH_URL}?{query}"

    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
            )
            if response.status_code != 200:
                return None
            data = response.json()
            return data.get("access_token")

    async def get_user_info(self, access_token: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.GITHUB_API_URL}/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            if response.status_code != 200:
                return None
            return response.json()

    async def get_user_emails(self, access_token: str) -> Optional[list]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.GITHUB_API_URL}/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            if response.status_code != 200:
                return None
            return response.json()


def get_github_oauth_service() -> Optional[GitHubOAuthService]:
    import os
    client_id = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_OAUTH_CLIENT_SECRET")
    if client_id and client_secret:
        return GitHubOAuthService(client_id, client_secret)
    return None


# 依赖注入函数
def get_current_user_dependency(db: Session, token: str) -> User:
    """获取当前用户依赖"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return user


def require_admin_dependency(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """要求管理员权限"""
    user = get_current_user_dependency(db, token)
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user
