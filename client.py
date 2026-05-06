from __future__ import annotations
import json
import logging
import os
from typing import Any
import httpx

logger = logging.getLogger(__name__)

# Client singleton for connection pooling
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=_timeout(),
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
            ),
        )
    return _client


def _build_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["AuthenticationToken"] = os.getenv("WECLAPP_TOKEN", "")
    return headers


def _build_auth() -> None:
    # weclapp does not use HTTP Basic auth
    return None


def _build_base_url() -> str:
    tenant = os.getenv("WECLAPP_TENANT", "")
    return f"https://{tenant}.weclapp.com/webapp/api/v2"


def _url(path: str) -> str:
    base_url: str = _build_base_url()
    return base_url.rstrip("/") + path


def _timeout() -> int:
    return int(os.getenv("PARTY_API_TIMEOUT", "30"))


def _strip_nones(d: dict) -> dict:
    """Remove keys with None values (not sent to API)."""
    return {k: v for k, v in d.items() if v is not None}


async def api_get(path: str, params: dict | None = None) -> dict[str, Any]:
    clean = _strip_nones(params or {})
    async with httpx.AsyncClient(timeout=_timeout(), auth=_build_auth()) as client:
        r = await client.get(_url(path), params=clean, headers=_build_headers())
    return _handle(r)


async def api_post(path: str, body: dict | None = None, params: dict | None = None) -> dict[str, Any]:
    clean_params = _strip_nones(params or {})
    clean_body = _strip_nones(body or {})
    async with httpx.AsyncClient(timeout=_timeout(), auth=_build_auth()) as client:
        r = await client.post(_url(path), json=clean_body, params=clean_params, headers=_build_headers())
    return _handle(r)


async def api_put(path: str, body: dict | None = None, params: dict | None = None) -> dict[str, Any]:
    clean_params = _strip_nones(params or {})
    clean_body = _strip_nones(body or {})
    async with httpx.AsyncClient(timeout=_timeout(), auth=_build_auth()) as client:
        r = await client.put(_url(path), json=clean_body, params=clean_params, headers=_build_headers())
    return _handle(r)


async def api_delete(path: str, params: dict | None = None) -> dict[str, Any]:
    clean = _strip_nones(params or {})
    async with httpx.AsyncClient(timeout=_timeout(), auth=_build_auth()) as client:
        r = await client.delete(_url(path), params=clean, headers=_build_headers())
    return _handle(r)


async def api_post_multipart(path: str, file_bytes: bytes, filename: str, params: dict | None = None) -> dict[str, Any]:
    clean_params = _strip_nones(params or {})
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    h = _build_headers()
    h.pop("Content-Type", None)  # let httpx set multipart content-type
    async with httpx.AsyncClient(timeout=_timeout(), auth=_build_auth()) as client:
        r = await client.post(_url(path), files=files, params=clean_params, headers=h)
    return _handle(r)


def _handle(r: httpx.Response) -> dict[str, Any]:
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}

    if r.is_success:
        return {"success": True, "status": r.status_code, "data": body}

    logger.error(
        "HTTP error: %s %s - Status: %d, Error: %s",
        r.request.method,
        r.request.url,
        r.status_code,
        body,
    )
    return {
        "success": False,
        "status": r.status_code,
        "error": body,
        "hint": "Check status code and error body above for details.",
    }


def parse_json_param(value: str | None, param_name: str) -> Any:
    """Parse a JSON string parameter, returning helpful error on failure."""
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Parameter '{param_name}' must be valid JSON. Got: {value!r}. Error: {e}") from e
