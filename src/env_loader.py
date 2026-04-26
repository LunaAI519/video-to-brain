"""
Shared environment variable loader.

Reads .env files without requiring python-dotenv.
Used by bot.py and other modules that need env config.
"""

import os


def load_env(env_path: str = ".env") -> None:
    """Load environment variables from a .env file.

    Only sets variables that are not already in the environment.
    Tries the given path first, then falls back to ~/.hermes/.env.

    Args:
        env_path: Path to the .env file.
    """
    if not os.path.exists(env_path):
        env_path = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(env_path):
        return

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val
