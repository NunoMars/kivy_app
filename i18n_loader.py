from __future__ import annotations

import os
import json
from pathlib import Path
from functools import lru_cache
from typing import Optional

# Simple module-level current language (can be set by main)
_CURRENT_LANG: Optional[str] = None

# Directory containing per-language json files
LANG_DIR = os.path.join(os.path.dirname(__file__), 'i18n', 'lang')


def _lang_json_path(lang: str) -> str:
    if not lang:
        return ''
    safe = str(lang).lower().replace('-', '_')
    return os.path.join(LANG_DIR, f"{safe}.json")


@lru_cache(maxsize=32)
def _load_lang_json(lang: str) -> dict:
    path = _lang_json_path(lang)
    if not path:
        return {}
    try:
        p = Path(path)
        if not p.exists():
            return {}
        with p.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def load_lang_messages(lang: str) -> dict:
    try:
        data = _load_lang_json(lang)
        return data.get('messages', {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_lang_significations(lang: str) -> dict:
    try:
        data = _load_lang_json(lang)
        return data.get('significations', {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def get_system_language() -> str:
    # prefer explicit module override
    try:
        if _CURRENT_LANG:
            return _CURRENT_LANG[:2]
    except Exception:
        pass
    # environment override
    try:
        forced = os.environ.get('APP_LANG') or os.environ.get('LANGUAGE')
        if forced:
            return forced[:2].lower()
    except Exception:
        pass
    # default fallback
    return 'fr'


def set_app_language(lang: str) -> None:
    global _CURRENT_LANG
    try:
        _CURRENT_LANG = (lang or '').lower()[:2]
    except Exception:
        _CURRENT_LANG = None


def tr(key: str, lang: Optional[str] = None, **kwargs) -> str:
    try:
        chosen = (lang or get_system_language())
    except Exception:
        chosen = None
    if chosen:
        msgs = load_lang_messages(chosen)
        if isinstance(msgs, dict) and key in msgs:
            val = msgs.get(key)
            try:
                if kwargs and isinstance(val, str):
                    return val.format(**kwargs)
                return val
            except Exception:
                return val
    # no fallback to other code-level translations: return key to flag missing
    try:
        return key if not kwargs else key.format(**kwargs)
    except Exception:
        return key


# Re-use cards_mapping if available for name/image mapping



def get_cards_signification(lang: str) -> dict:
    """
    Retourne le dictionnaire des significations pour la langue passée en paramètre.
    """
    with open(f"i18n/lang/{lang}.json", encoding="utf-8") as f:
        data = json.load(f)
    signification_dict = data.get("significations", {})
    return signification_dict


# Expose an empty MESSAGES dict (source of truth remains the JSON files)
def _build_messages_snapshot() -> dict:
    out = {}
    try:
        base = os.path.join(os.path.dirname(__file__), 'i18n', 'lang')
        p = Path(base)
        if p.exists() and p.is_dir():
            for fname in os.listdir(base):
                if not fname.endswith('.json'):
                    continue
                lname = fname[:-5]
                try:
                    data = _load_lang_json(lname)
                    msgs = data.get('messages', {}) if isinstance(data, dict) else {}
                    if msgs and isinstance(msgs, dict):
                        out[lname] = msgs
                    else:
                        out[lname] = {}
                except Exception:
                    out[lname] = {}
    except Exception:
        pass
    return out


MESSAGES = _build_messages_snapshot()


__all__ = [
    'tr', 'get_system_language', 'set_app_language', 'load_lang_messages',
    'load_lang_significations', 'get_cards_signification', 'get_card_image_path',
    'get_card_name_for_lang', 'get_french_card_name', 'MESSAGES', 'SIGNIFICATION_KEY_MAP'
]
