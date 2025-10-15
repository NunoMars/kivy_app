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
try:
    from cards_mapping import (
        get_card_image_path,
        get_french_card_name,
        get_card_name_for_lang,
    )
except Exception:
    def get_card_image_path(card_name, state='droite'):
        return 'tarot_img/Back.jpg'

    def get_french_card_name(name):
        return name

    def get_card_name_for_lang(french_name, target_lang):
        return french_name


def get_cards_signification() -> dict:
    try:
        lang = get_system_language()
    except Exception:
        lang = None
    if lang:
        sig = load_lang_significations(lang)
        if sig:
            return sig
    fr_sig = load_lang_significations('fr')
    return fr_sig or {}


# Mapping used by UI to find the correct keys inside signification bundles.
# This small mapping is structural (field names), not user-facing UI text.
SIGNIFICATION_KEY_MAP = {
    "fr": {
        "keywords": {"upright": "a l'endroit", "reversed": "a l'envers"},
        "detail": {"upright": "signification a l'endroit", "reversed": "signification a l'envers"},
    },
    "en": {
        "keywords": {"upright": "upright", "reversed": "reversed"},
        "detail": {"upright": "signification upright", "reversed": "signification reversed"},
    },
    "pt": {
        "keywords": {"upright": "direita", "reversed": "invertida"},
        "detail": {"upright": "signification direita", "reversed": "signification invertida"},
    },
}


# Expose an empty MESSAGES dict (source of truth remains the JSON files)
MESSAGES = {}


__all__ = [
    'tr', 'get_system_language', 'set_app_language', 'load_lang_messages',
    'load_lang_significations', 'get_cards_signification', 'get_card_image_path',
    'get_card_name_for_lang', 'get_french_card_name', 'MESSAGES', 'SIGNIFICATION_KEY_MAP'
]
