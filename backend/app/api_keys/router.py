"""
API Key Router - CRUD endpoints for managing user API keys
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.models.api_key import ApiKey
from app.services.encryption import get_encryption_service
from app.api_keys.schemas import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeyListResponse,
    ProviderInfo,
    ApiKeyTestRequest,
    ApiKeyTestResponse,
)
from app.api_keys.providers import PROVIDERS, get_provider, get_all_providers, is_valid_provider
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()


def mask_api_key(key: str) -> str:
    """Mask an API key to show only first 4 and last 4 characters"""
    if not key or len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


def api_key_to_response(api_key: ApiKey, encryption_service) -> ApiKeyResponse:
    """Convert ApiKey model to response schema with masked key"""
    decrypted_key = encryption_service.decrypt(api_key.encrypted_key)
    return ApiKeyResponse(
        id=api_key.id,
        user_id=api_key.user_id,
        provider=api_key.provider,
        label=api_key.label,
        masked_key=mask_api_key(decrypted_key),
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
    )


@router.get("/providers", response_model=list[ProviderInfo])
async def get_providers():
    """Get all supported AI providers"""
    providers = get_all_providers()
    return [
        ProviderInfo(
            id=p["id"],
            name=p["name"],
            base_url=p["base_url"],
            models=p["models"],
            supports_function_calling=p["supports_function_calling"],
            supports_vision=p["supports_vision"],
            website=p["website"],
            description=p["description"],
        )
        for p in providers
    ]


@router.get("", response_model=ApiKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all API keys for the current user"""
    encryption_service = get_encryption_service()
    
    api_keys = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id
    ).order_by(ApiKey.created_at.desc()).all()
    
    return ApiKeyListResponse(
        items=[api_key_to_response(k, encryption_service) for k in api_keys],
        total=len(api_keys),
    )


@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_api_key(
    data: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create or update an API key for a provider"""
    # Validate provider
    if not is_valid_provider(data.provider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {data.provider}. Valid providers: {list(PROVIDERS.keys())}",
        )
    
    encryption_service = get_encryption_service()
    
    # Check if API key already exists for this user and provider
    existing = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == data.provider,
    ).first()
    
    if existing:
        # Update existing key
        existing.encrypted_key = encryption_service.encrypt(data.api_key)
        existing.label = data.label
        existing.is_active = True
        existing.updated_at = existing.updated_at  # Will auto-update via onupdate
        db.commit()
        db.refresh(existing)
        logger.info(f"Updated API key for user {current_user.id}, provider {data.provider}")
        return api_key_to_response(existing, encryption_service)
    
    # Create new API key
    encrypted_key = encryption_service.encrypt(data.api_key)
    api_key = ApiKey(
        user_id=current_user.id,
        provider=data.provider,
        encrypted_key=encrypted_key,
        label=data.label,
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    logger.info(f"Created API key for user {current_user.id}, provider {data.provider}")
    return api_key_to_response(api_key, encryption_service)


@router.patch("/{provider}", response_model=ApiKeyResponse)
async def update_api_key(
    provider: str,
    data: ApiKeyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update an API key (change label or active status)"""
    encryption_service = get_encryption_service()
    
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == provider,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for provider '{provider}' not found",
        )
    
    if data.api_key is not None:
        api_key.encrypted_key = encryption_service.encrypt(data.api_key)
    if data.label is not None:
        api_key.label = data.label
    if data.is_active is not None:
        api_key.is_active = data.is_active
    
    db.commit()
    db.refresh(api_key)
    
    logger.info(f"Updated API key for user {current_user.id}, provider {provider}")
    return api_key_to_response(api_key, encryption_service)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete an API key for a provider"""
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == provider,
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for provider '{provider}' not found",
        )
    
    db.delete(api_key)
    db.commit()
    
    logger.info(f"Deleted API key for user {current_user.id}, provider {provider}")
    return None


@router.post("/test", response_model=ApiKeyTestResponse)
async def test_api_key(
    data: ApiKeyTestRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Test if an API key is valid by making a simple request"""
    if not is_valid_provider(data.provider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {data.provider}",
        )
    
    # Get or use the API key
    if data.api_key:
        # Test the provided new key (before saving)
        api_key_to_test = data.api_key
    else:
        # Test the stored key for this provider
        encryption_service = get_encryption_service()
        api_key_record = db.query(ApiKey).filter(
            ApiKey.user_id == current_user.id,
            ApiKey.provider == data.provider,
            ApiKey.is_active == True
        ).first()
        
        if not api_key_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active API key found for provider '{data.provider}'",
            )
        
        api_key_to_test = encryption_service.decrypt(api_key_record.encrypted_key)
    
    provider_config = get_provider(data.provider)
    
    try:
        # Make a simple test request
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {api_key_to_test}"}
            
            # Prepare request based on provider
            if data.provider == "anthropic":
                # Anthropic requires specific headers
                headers["x-api-key"] = api_key_to_test
                headers["anthropic-version"] = "2023-06-01"
                response = await client.post(
                    f"{provider_config['base_url']}/messages",
                    headers=headers,
                    json={
                        "model": provider_config["models"][0],
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hi"}],
                    },
                )
            elif data.provider == "gemini":
                # Gemini uses a different endpoint format
                response = await client.post(
                    f"{provider_config['base_url']}/models/{provider_config['models'][0]}:generateContent",
                    headers={"Authorization": f"Bearer {api_key_to_test}"},
                    params={"key": api_key_to_test},
                    json={"contents": [{"parts": [{"text": "Hi"}]}]},
                )
            else:
                # Standard OpenAI-compatible API
                response = await client.post(
                    f"{provider_config['base_url']}/chat/completions",
                    headers=headers,
                    json={
                        "model": provider_config["models"][0],
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 10,
                    },
                )
            
            if response.status_code == 200:
                result = response.json()
                model = result.get("model") or result.get("candidates", [{}])[0].get("model", provider_config["models"][0])
                return ApiKeyTestResponse(
                    success=True,
                    message="API key is valid",
                    model=model,
                )
            else:
                error_detail = response.text
                return ApiKeyTestResponse(
                    success=False,
                    message=f"API key validation failed: {response.status_code} - {error_detail[:200]}",
                )
    
    except httpx.TimeoutException:
        return ApiKeyTestResponse(
            success=False,
            message="Request timed out",
        )
    except Exception as e:
        logger.error(f"API key test failed: {str(e)}")
        return ApiKeyTestResponse(
            success=False,
            message=f"Request failed: {str(e)[:200]}",
        )
