"""
llm_handler.py
Stateless interface to Ollama.
Every call is a fresh, isolated request — no history, no memory.
"""

import base64
import json
from pathlib import Path

import requests

OLLAMA_BASE_URL = "http://127.0.0.1:11434"


class OllamaError(Exception):
    pass


def list_models() -> list[str]:
    """Return all locally available Ollama model names."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
    except requests.exceptions.ConnectionError:
        return []
    except Exception as exc:  # noqa: BLE001
        raise OllamaError(f"Failed to list models: {exc}") from exc


def generate_text(
    model: str,
    prompt: str,
    system: str = "",
    temperature: float = 0.7,
    chunk_callback=None,
) -> str:
    """
    Send a completely stateless text generation request using streaming.
    No conversation history. No prior context.

    chunk_callback: optional callable(str) called with each token as it arrives.
    Returns the full accumulated response.
    """
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system

    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            stream=True,
            # 60s connect timeout; no read timeout (large models can be slow)
            timeout=(60, None),
        ) as resp:
            resp.raise_for_status()
            accumulated = []
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                try:
                    chunk = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                token = chunk.get("response", "")
                if token:
                    accumulated.append(token)
                    if chunk_callback:
                        chunk_callback(token)
                if chunk.get("done", False):
                    break
            return "".join(accumulated).strip()
    except requests.exceptions.ConnectionError as exc:
        raise OllamaError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise OllamaError(f"Generation failed: {exc}") from exc


def generate_with_image(
    model: str,
    prompt: str,
    image_path: str | Path,
    system: str = "",
    temperature: float = 0.4,
    chunk_callback=None,
) -> str:
    """
    Send a completely stateless vision request with one image using streaming.
    No conversation history. No prior context.

    chunk_callback: optional callable(str) called with each token as it arrives.
    Returns the full accumulated response.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise OllamaError(f"Image file not found: {image_path}")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload: dict = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": True,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system

    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=(60, None),
        ) as resp:
            resp.raise_for_status()
            accumulated = []
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                try:
                    chunk = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                token = chunk.get("response", "")
                if token:
                    accumulated.append(token)
                    if chunk_callback:
                        chunk_callback(token)
                if chunk.get("done", False):
                    break
            return "".join(accumulated).strip()
    except requests.exceptions.ConnectionError as exc:
        raise OllamaError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise OllamaError(f"Vision generation failed: {exc}") from exc


def is_ollama_running() -> bool:
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return resp.status_code == 200
    except Exception:  # noqa: BLE001
        return False
