"""
Encryption Service - Handles symmetric encryption for API keys using Fernet
"""
import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Find .env in project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

# Environment variable name for the encryption key
API_KEY_ENCRYPTION_KEY_NAME = "API_KEY_ENCRYPTION_KEY"


def _get_or_create_encryption_key() -> bytes:
    """
    Get the encryption key from environment variable.
    If not found, generate a new one and save it to .env file.
    This only happens once during first use.
    """
    key = os.getenv(API_KEY_ENCRYPTION_KEY_NAME)
    
    if key:
        return key.encode()
    
    # Generate a new Fernet key
    new_key = Fernet.generate_key()
    
    # Save to .env file
    _save_key_to_env(new_key.decode())
    
    logger.info(f"Generated new API key encryption key and saved to .env")
    return new_key


def _save_key_to_env(key: str) -> None:
    """Save encryption key to .env file"""
    env_path = _env_path
    
    # Read existing .env content
    existing_content = ""
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
    
    # Check if the key already exists
    if API_KEY_ENCRYPTION_KEY_NAME in existing_content:
        return
    
    # Append the new key
    with open(env_path, "a", encoding="utf-8") as f:
        if existing_content and not existing_content.endswith("\n"):
            f.write("\n")
        f.write(f"{API_KEY_ENCRYPTION_KEY_NAME}={key}\n")
    
    logger.info(f"Saved API key encryption key to {env_path}")


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    _instance = None
    _fernet = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the Fernet cipher with the encryption key"""
        key = _get_or_create_encryption_key()
        self._fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""
        encrypted = self._fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            ciphertext: The encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
        decrypted = self._fernet.decrypt(ciphertext.encode())
        return decrypted.decode()


# Singleton instance
encryption_service = EncryptionService()


def get_encryption_service() -> EncryptionService:
    """Get the encryption service singleton instance"""
    return encryption_service
