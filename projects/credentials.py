"""Secure credential management using system keyring."""

import os
import json
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
import keyring

SERVICE_NAME = "project-cli"
KEY_FILE = Path.home() / ".config" / "project-cli" / ".key"
ENCRYPTED_TOKENS_FILE = Path.home() / ".config" / "project-cli" / ".tokens"


def _get_encryption_key() -> bytes:
    """Get or create encryption key for config file encryption."""
    if not KEY_FILE.exists():
        key = Fernet.generate_key()
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_bytes(key)
        KEY_FILE.chmod(0o600)  # Secure permissions (owner read/write only)
    return KEY_FILE.read_bytes()


def _load_encrypted_tokens() -> dict:
    """Load encrypted tokens from config file."""
    if not ENCRYPTED_TOKENS_FILE.exists():
        return {}

    try:
        key = _get_encryption_key()
        fernet = Fernet(key)

        encrypted_data = ENCRYPTED_TOKENS_FILE.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception:
        return {}


def _save_encrypted_tokens(tokens: dict) -> bool:
    """Save encrypted tokens to config file."""
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)

        json_data = json.dumps(tokens).encode()
        encrypted_data = fernet.encrypt(json_data)

        ENCRYPTED_TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ENCRYPTED_TOKENS_FILE.write_bytes(encrypted_data)
        ENCRYPTED_TOKENS_FILE.chmod(0o600)  # Secure permissions
        return True
    except Exception:
        return False


def store_token(platform: str, token: str, method: str = 'keyring') -> bool:
    """
    Store API token securely.

    Args:
        platform: Platform name ('github' or 'gitlab')
        token: API token to store
        method: Storage method ('keyring', 'encrypted_file', or 'both')

    Returns:
        True if stored successfully, False otherwise
    """
    success = False

    if method in ('keyring', 'both'):
        try:
            keyring.set_password(SERVICE_NAME, platform, token)
            success = True
        except Exception:
            # Keyring might not be available on all systems
            pass

    if method in ('encrypted_file', 'both'):
        tokens = _load_encrypted_tokens()
        tokens[platform] = token
        if _save_encrypted_tokens(tokens):
            success = True

    return success


def get_token(platform: str) -> Optional[str]:
    """
    Retrieve API token with fallback chain.

    Tries in order:
    1. System keyring
    2. Encrypted config file
    3. Environment variable

    Args:
        platform: Platform name ('github' or 'gitlab')

    Returns:
        Token string if found, None otherwise
    """
    # 1. Try keyring first
    try:
        token = keyring.get_password(SERVICE_NAME, platform)
        if token:
            return token
    except Exception:
        pass

    # 2. Try encrypted config file
    tokens = _load_encrypted_tokens()
    if platform in tokens:
        return tokens[platform]

    # 3. Try environment variable
    env_var = f"{platform.upper()}_TOKEN"
    token = os.getenv(env_var)
    if token:
        return token

    return None


def delete_token(platform: str) -> bool:
    """
    Delete API token from all storage locations.

    Args:
        platform: Platform name ('github' or 'gitlab')

    Returns:
        True if any token was deleted, False otherwise
    """
    deleted = False

    # Delete from keyring
    try:
        keyring.delete_password(SERVICE_NAME, platform)
        deleted = True
    except Exception:
        pass

    # Delete from encrypted config file
    tokens = _load_encrypted_tokens()
    if platform in tokens:
        del tokens[platform]
        _save_encrypted_tokens(tokens)
        deleted = True

    return deleted


def list_stored_platforms() -> list[str]:
    """
    List platforms that have stored tokens.

    Returns:
        List of platform names
    """
    platforms = set()

    # Check keyring
    try:
        # Note: keyring doesn't have a list method, so we check known platforms
        for platform in ['github', 'gitlab']:
            if keyring.get_password(SERVICE_NAME, platform):
                platforms.add(platform)
    except Exception:
        pass

    # Check encrypted file
    tokens = _load_encrypted_tokens()
    platforms.update(tokens.keys())

    return sorted(platforms)


def test_token(platform: str, token: Optional[str] = None) -> bool:
    """
    Test if a token is valid by making an API call.

    Args:
        platform: Platform name ('github' or 'gitlab')
        token: Token to test (if None, will retrieve from storage)

    Returns:
        True if token is valid, False otherwise
    """
    if token is None:
        token = get_token(platform)

    if not token:
        return False

    try:
        if platform == 'github':
            from github import Github
            g = Github(token)
            # Test by getting authenticated user
            g.get_user().login
            return True
        elif platform == 'gitlab':
            from gitlab import Gitlab
            gl = Gitlab('https://gitlab.com', private_token=token)
            # Test by getting authenticated user
            gl.auth()
            return True
    except Exception:
        return False

    return False
