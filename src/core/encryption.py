"""
Encryption module for securing sensitive data (credentials, passwords, API keys).
Uses Fernet symmetric encryption from the cryptography library.
The master key is derived from a user-supplied passphrase via PBKDF2.
"""
import os
import base64
import json
import logging
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

_SALT_FILE = os.path.join(Path.home(), ".mynexus", "data", ".salt")
_KEY_CHECK_FILE = os.path.join(Path.home(), ".mynexus", "data", ".keycheck")


def _get_or_create_salt() -> bytes:
    """Get existing salt or create a new one."""
    os.makedirs(os.path.dirname(_SALT_FILE), exist_ok=True)
    if os.path.exists(_SALT_FILE):
        with open(_SALT_FILE, "rb") as f:
            return f.read()
    salt = os.urandom(16)
    with open(_SALT_FILE, "wb") as f:
        f.write(salt)
    return salt


def derive_key(passphrase: str) -> bytes:
    """Derive a Fernet key from a passphrase using PBKDF2."""
    salt = _get_or_create_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def save_key_check(passphrase: str) -> None:
    """Save a verification token so we can validate the passphrase later."""
    key = derive_key(passphrase)
    fernet = Fernet(key)
    token = fernet.encrypt(b"MYNEXUS_KEY_CHECK")
    os.makedirs(os.path.dirname(_KEY_CHECK_FILE), exist_ok=True)
    with open(_KEY_CHECK_FILE, "wb") as f:
        f.write(token)


def verify_passphrase(passphrase: str) -> bool:
    """Verify a passphrase against the stored key check."""
    if not os.path.exists(_KEY_CHECK_FILE):
        return True  # No passphrase set yet
    try:
        key = derive_key(passphrase)
        fernet = Fernet(key)
        with open(_KEY_CHECK_FILE, "rb") as f:
            token = f.read()
        result = fernet.decrypt(token)
        return result == b"MYNEXUS_KEY_CHECK"
    except (InvalidToken, Exception):
        return False


def is_passphrase_set() -> bool:
    """Check whether a master passphrase has been configured."""
    return os.path.exists(_KEY_CHECK_FILE)


class EncryptionManager:
    """Encrypt/decrypt strings using a derived Fernet key."""

    def __init__(self, passphrase: str):
        self._key = derive_key(passphrase)
        self._fernet = Fernet(self._key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string, return base64-encoded ciphertext."""
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string. Returns empty string on failure."""
        if not ciphertext:
            return ""
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except (InvalidToken, Exception):
            # If decryption fails, the data may be unencrypted (legacy).
            # Return the original value so the UI can still display it.
            logger.warning("Decryption failed; returning raw value (possible legacy data)")
            return ciphertext


# Global instance – initialized after user enters master passphrase
_instance: EncryptionManager | None = None


def init_encryption(passphrase: str) -> EncryptionManager:
    """Initialize the global encryption manager."""
    global _instance
    _instance = EncryptionManager(passphrase)
    return _instance


def get_encryption_manager() -> EncryptionManager | None:
    """Get the global encryption manager (None if not yet initialized)."""
    return _instance
