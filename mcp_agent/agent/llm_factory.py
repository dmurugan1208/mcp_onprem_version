"""
LLM factory — returns Claude via Anthropic API (only supported provider).

All other LLM providers (xAI, HuggingFace, Groq, Bedrock) have been disabled.

Config precedence (highest → lowest):
  1. sajhamcpserver/config/llm_config.json  (set via Super Admin UI)
  2. Environment variables (.env)
"""
import json
import os
import pathlib

_CONFIG_PATH = pathlib.Path(__file__).parent.parent / 'sajhamcpserver' / 'config' / 'llm_config.json'


def _load_file_config() -> dict:
    """Load llm_config.json. Returns empty dict if missing or invalid."""
    try:
        if _CONFIG_PATH.exists():
            return json.loads(_CONFIG_PATH.read_text())
    except Exception:
        pass
    return {}


def create_llm():
    """Create and return Anthropic ChatAnthropic LLM (only supported provider)."""
    file_cfg = _load_file_config()

    # Use Anthropic provider only (all others disabled)
    from langchain_anthropic import ChatAnthropic
    prov_cfg = file_cfg.get('anthropic', {})
    api_key = prov_cfg.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
    model   = prov_cfg.get('model')    or os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
    max_tok = prov_cfg.get('max_tokens') or int(os.getenv('LLM_MAX_TOKENS', '8192'))

    return ChatAnthropic(
        model=model,
        api_key=api_key,
        temperature=0,
        streaming=True,
        max_tokens=int(max_tok),
    )
