import time
from threading import Lock
from typing import Dict

# jti -> expiry timestamp
_blocklist: Dict[str, float] = {}
_lock = Lock()

def block_token(jti: str, exp: float):
    """
    Adds a token's JTI to the blocklist until its natural expiry.
    :param jti: The unique identifier for the token.
    :param exp: Unix timestamp when the token would have expired.
    """
    with _lock:
        _blocklist[jti] = exp

def is_blocked(jti: str) -> bool:
    """
    Checks if a JTI is in the blocklist.
    Also performs periodic eviction of expired entries.
    """
    with _lock:
        _evict()
        return jti in _blocklist

def _evict():
    """Removes entries that have passed their expiry time."""
    now = time.time()
    expired = [k for k, v in _blocklist.items() if v < now]
    for k in expired:
        del _blocklist[k]
