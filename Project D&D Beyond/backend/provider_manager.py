"""
provider_manager.py
Unified dispatcher for local (Ollama) and online AI providers.
Manages provider selection and API key storage in config/providers.json.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROVIDERS_CONFIG = PROJECT_ROOT / "config" / "providers.json"

# Provider identifiers
LOCAL = "local"
OPENAI = "openai"
GROK = "grok"
ANTHROPIC = "anthropic"

PROVIDER_LABELS = {
    LOCAL:     "Local (Ollama)",
    OPENAI:    "OpenAI (ChatGPT)",
    GROK:      "Grok (xAI)",
    ANTHROPIC: "Anthropic (Claude)",
}

# Default model lists for online providers (user can type custom names too)
PROVIDER_MODELS = {
    OPENAI:    ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o3-mini"],
    GROK:      ["grok-3", "grok-3-mini", "grok-2-vision-1212"],
    ANTHROPIC: ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"],
}

_cache: dict = {}


# ---------------------------------------------------------------------------
# Config persistence
# ---------------------------------------------------------------------------

def _load() -> dict:
    global _cache
    if PROVIDERS_CONFIG.exists():
        try:
            _cache = json.loads(PROVIDERS_CONFIG.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            _cache = {}
    return _cache


def _save() -> None:
    PROVIDERS_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    PROVIDERS_CONFIG.write_text(json.dumps(_cache, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Provider / model selection
# ---------------------------------------------------------------------------

def get_provider() -> str:
    return _load().get("provider", LOCAL)


def set_provider(name: str) -> None:
    _load()
    _cache["provider"] = name
    _save()


def get_api_key(provider: str) -> str:
    return _load().get("api_keys", {}).get(provider, "")


def set_api_key(provider: str, key: str) -> None:
    _load()
    _cache.setdefault("api_keys", {})[provider] = key
    _save()


def get_models_for_provider(provider: str) -> list[str]:
    if provider == LOCAL:
        from backend import llm_handler
        if llm_handler.is_ollama_running():
            return llm_handler.list_models()
        return []
    return list(PROVIDER_MODELS.get(provider, []))


def is_provider_ready(provider: str) -> bool:
    if provider == LOCAL:
        from backend import llm_handler
        return llm_handler.is_ollama_running()
    return bool(get_api_key(provider).strip())


# ---------------------------------------------------------------------------
# Unified generation — dispatches to Ollama or online handler
# ---------------------------------------------------------------------------

def generate_text(
    model: str,
    prompt: str,
    system: str = "",
    temperature: float = 0.7,
    chunk_callback=None,
) -> str:
    provider = get_provider()
    if provider == LOCAL:
        from backend import llm_handler
        return llm_handler.generate_text(model, prompt, system, temperature, chunk_callback)
    from backend import online_handler
    return online_handler.generate_text(
        provider=provider,
        api_key=get_api_key(provider),
        model=model,
        prompt=prompt,
        system=system,
        temperature=temperature,
        chunk_callback=chunk_callback,
    )


def generate_with_image(
    model: str,
    prompt: str,
    image_path,
    system: str = "",
    temperature: float = 0.4,
    chunk_callback=None,
) -> str:
    provider = get_provider()
    if provider == LOCAL:
        from backend import llm_handler
        return llm_handler.generate_with_image(model, prompt, image_path, system, temperature, chunk_callback)
    from backend import online_handler
    return online_handler.generate_with_image(
        provider=provider,
        api_key=get_api_key(provider),
        model=model,
        prompt=prompt,
        image_path=image_path,
        system=system,
        temperature=temperature,
        chunk_callback=chunk_callback,
    )
