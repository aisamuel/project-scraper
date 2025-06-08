import random
from typing import List, Optional

from fake_useragent import UserAgent  # type: ignore

PROXY_LIST: List[str] = []


def get_headers() -> dict:
    ua = UserAgent()
    return {"User-Agent": ua.random, "Accept-Language": "en-US,en;q=0.5"}


def get_proxies() -> Optional[dict]:
    if PROXY_LIST:
        proxy = random.choice(PROXY_LIST)
        return {"http": proxy, "https": proxy}
    return None
