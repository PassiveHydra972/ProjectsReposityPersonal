"""
online_handler.py
Handles online AI provider API calls: OpenAI, Grok (xAI), Anthropic.
All calls are stateless — no conversation history, no memory.
"""

import base64
import json
from pathlib import Path

import requests

# OpenAI-compatible providers share the same endpoint structure
OPENAI_COMPATIBLE = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "grok":   "https://api.x.ai/v1/chat/completions",
}

ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"

MIME_MAP = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "png": "image/png", "gif": "image/gif", "webp": "image/webp",
}


class OnlineProviderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def generate_text(
    provider: str,
    api_key: str,
    model: str,
    prompt: str,
    system: str = "",
    temperature: float = 0.7,
    chunk_callback=None,
) -> str:
    _require_key(api_key, provider)
    if provider == "anthropic":
        return _anthropic_text(api_key, model, prompt, system, temperature, chunk_callback)
    return _openai_text(provider, api_key, model, prompt, system, temperature, chunk_callback)


def generate_with_image(
    provider: str,
    api_key: str,
    model: str,
    prompt: str,
    image_path,
    system: str = "",
    temperature: float = 0.4,
    chunk_callback=None,
) -> str:
    _require_key(api_key, provider)
    image_path = Path(image_path)
    if not image_path.exists():
        raise OnlineProviderError(f"Image file not found: {image_path}")
    if provider == "anthropic":
        return _anthropic_vision(api_key, model, prompt, image_path, system, temperature, chunk_callback)
    return _openai_vision(provider, api_key, model, prompt, image_path, system, temperature, chunk_callback)


# ---------------------------------------------------------------------------
# OpenAI-compatible (OpenAI + Grok)
# ---------------------------------------------------------------------------

def _openai_text(provider, api_key, model, prompt, system, temperature, chunk_callback):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return _openai_stream(provider, api_key, model, messages, temperature, chunk_callback)


def _openai_vision(provider, api_key, model, prompt, image_path, system, temperature, chunk_callback):
    mime = MIME_MAP.get(image_path.suffix.lower().lstrip("."), "image/jpeg")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ]
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": content})
    return _openai_stream(provider, api_key, model, messages, temperature, chunk_callback)


def _openai_stream(provider, api_key, model, messages, temperature, chunk_callback):
    endpoint = OPENAI_COMPATIBLE[provider]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    try:
        with requests.post(
            endpoint, json=payload, headers=headers,
            stream=True, timeout=(30, None),
        ) as resp:
            _check_response(resp, provider)
            accumulated = []
            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
                if not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        accumulated.append(delta)
                        if chunk_callback:
                            chunk_callback(delta)
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
            return "".join(accumulated).strip()
    except OnlineProviderError:
        raise
    except requests.exceptions.ConnectionError as exc:
        raise OnlineProviderError(f"Cannot connect to {provider} API.") from exc
    except Exception as exc:  # noqa: BLE001
        raise OnlineProviderError(f"{provider} request failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------

def _anthropic_text(api_key, model, prompt, system, temperature, chunk_callback):
    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "stream": True,
    }
    if system:
        payload["system"] = system
    return _anthropic_stream(api_key, payload, chunk_callback)


def _anthropic_vision(api_key, model, prompt, image_path, system, temperature, chunk_callback):
    mime = MIME_MAP.get(image_path.suffix.lower().lstrip("."), "image/jpeg")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                {"type": "text", "text": prompt},
            ],
        }],
        "temperature": temperature,
        "stream": True,
    }
    if system:
        payload["system"] = system
    return _anthropic_stream(api_key, payload, chunk_callback)


def _anthropic_stream(api_key, payload, chunk_callback):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type": "application/json",
    }
    try:
        with requests.post(
            ANTHROPIC_ENDPOINT, json=payload, headers=headers,
            stream=True, timeout=(30, None),
        ) as resp:
            _check_response(resp, "anthropic")
            accumulated = []
            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
                if not line.startswith("data: "):
                    continue
                try:
                    chunk = json.loads(line[6:])
                    if chunk.get("type") == "content_block_delta":
                        delta = chunk.get("delta", {}).get("text", "")
                        if delta:
                            accumulated.append(delta)
                            if chunk_callback:
                                chunk_callback(delta)
                except (json.JSONDecodeError, KeyError):
                    continue
            return "".join(accumulated).strip()
    except OnlineProviderError:
        raise
    except requests.exceptions.ConnectionError as exc:
        raise OnlineProviderError("Cannot connect to Anthropic API.") from exc
    except Exception as exc:  # noqa: BLE001
        raise OnlineProviderError(f"Anthropic request failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_key(api_key: str, provider: str) -> None:
    if not api_key or not api_key.strip():
        raise OnlineProviderError(
            f"No API key set for {provider}.\n"
            "Click 'API Keys…' in the sidebar to add one."
        )


def _check_response(resp: requests.Response, provider: str) -> None:
    if resp.status_code < 400:
        return
    try:
        detail = resp.json()
        msg = (
            detail.get("error", {}).get("message")
            or detail.get("error", str(detail))
        )
    except Exception:  # noqa: BLE001
        msg = resp.text[:300]
    raise OnlineProviderError(f"{provider} API error {resp.status_code}: {msg}")
