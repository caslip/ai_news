from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import uuid
import json

from app.database import get_db
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    UserUpdate,
    TokenResponse,
)
from app.services.auth import AuthService, get_github_oauth_service, OAuthProvider
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[UserResponse]:
    if token is None:
        return None
    user = auth_service.get_current_user(token)
    if user is None:
        return None
    return UserResponse.model_validate(user)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return UserResponse.model_validate(user)


async def require_admin(
    token: Optional[str] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Require admin role"""
    user = await get_current_user(token, auth_service)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


@router.post("/register", response_model=TokenResponse)
def register(
    user_data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    existing_user = auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = auth_service.create_user(user_data)
    access_token = auth_service.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
def logout(
    response: Response,
    token: Optional[str] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    # logout 不强制要求有效 token，因为用户可能已经过期
    # 只清理 cookie
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(user, key, value)

    auth_service.db.commit()
    auth_service.db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/oauth/github")
def github_oauth_init():
    oauth_service = get_github_oauth_service()
    if not oauth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )
    state = str(uuid.uuid4())
    url = oauth_service.get_authorization_url(state)
    return {"authorization_url": url, "state": state}


@router.get("/oauth/github/callback", response_model=TokenResponse)
async def github_oauth_callback(
    code: str,
    state: Optional[str] = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    oauth_service = get_github_oauth_service()
    if not oauth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )

    access_token = await oauth_service.exchange_code_for_token(code)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token",
        )

    github_user = await oauth_service.get_user_info(access_token)
    if not github_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from GitHub",
        )

    github_id = str(github_user.get("id"))
    email = github_user.get("email")

    if not email:
        emails = await oauth_service.get_user_emails(access_token)
        if emails:
            primary_email = next(
                (e for e in emails if e.get("primary") and e.get("verified")),
                emails[0] if emails else None
            )
            email = primary_email.get("email") if primary_email else None

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get email from GitHub",
        )

    user = auth_service.get_user_by_oauth(OAuthProvider.GITHUB, github_id)
    if not user:
        user = auth_service.get_user_by_email(email)
        if user:
            user.oauth_provider = OAuthProvider.GITHUB
            user.oauth_id = github_id
            auth_service.db.commit()
            auth_service.db.refresh(user)
        else:
            nickname = github_user.get("login", f"user_{github_id[:8]}")
            avatar_url = github_user.get("avatar_url")
            user = auth_service.create_oauth_user(
                email=email,
                nickname=nickname,
                avatar_url=avatar_url,
                provider=OAuthProvider.GITHUB,
                oauth_id=github_id,
            )

    token = auth_service.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_token = auth_service.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
