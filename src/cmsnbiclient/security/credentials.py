import base64
import os
from typing import Optional

import keyring
import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = structlog.get_logger()


class SecureCredentialManager:
    """Secure credential storage using system keyring"""

    SERVICE_NAME = "cms-nbi-client"

    def __init__(self, profile: str = "default"):
        self.profile = profile
        self._fernet: Optional[Fernet] = None

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_name = f"{self.SERVICE_NAME}-key-{self.profile}"

        # Try to get existing key
        stored_key = keyring.get_password(self.SERVICE_NAME, key_name)
        if stored_key:
            return base64.b64decode(stored_key)

        # Generate new key
        key = Fernet.generate_key()
        keyring.set_password(self.SERVICE_NAME, key_name, base64.b64encode(key).decode())
        return key

    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption"""
        if not self._fernet:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet

    def store_credential(self, name: str, value: str) -> None:
        """Store encrypted credential"""
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(value.encode())

        keyring.set_password(
            self.SERVICE_NAME, f"{self.profile}-{name}", base64.b64encode(encrypted).decode()
        )
        logger.info(f"Stored credential: {name}")

    def get_credential(self, name: str) -> Optional[str]:
        """Retrieve and decrypt credential"""
        stored = keyring.get_password(self.SERVICE_NAME, f"{self.profile}-{name}")

        if not stored:
            return None

        try:
            fernet = self._get_fernet()
            encrypted = base64.b64decode(stored)
            decrypted = fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt credential {name}: {e}")
            return None

    def delete_credential(self, name: str) -> None:
        """Delete stored credential"""
        try:
            keyring.delete_password(self.SERVICE_NAME, f"{self.profile}-{name}")
            logger.info(f"Deleted credential: {name}")
        except keyring.errors.PasswordDeleteError:
            pass
