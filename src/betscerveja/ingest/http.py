"""Cliente HTTP com retry."""

from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def get_bytes(url: str, timeout: float = 60.0) -> tuple[int, bytes, str]:
    headers = {"User-Agent": "betscerveja/0.1 (personal research pipeline)"}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.status_code, response.content, str(response.url)
