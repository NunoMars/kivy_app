from __future__ import annotations

# Clés de mapping pour accéder aux bons champs de signification selon la langue
SIGNIFICATION_KEY_MAP = {
    "fr": {
        "keywords": {"upright": "a l'endroit", "reversed": "a l'envers"},
        "detail": {
            "upright": "signification a l'endroit",
            "reversed": "signification a l'envers",
        },
    },
    "en": {
        "keywords": {"upright": "upright", "reversed": "reversed"},
        "detail": {
            "upright": "signification upright",
            "reversed": "signification reversed",
        },
    },
    "pt": {
        "keywords": {"upright": "direita", "reversed": "invertida"},
        "detail": {
            "upright": "signification direita",
            "reversed": "signification invertida",
        },
    },
    # Add additional languages detected in i18n/lang/*.json
    "pt_br": {
        "keywords": {"upright": "direita", "reversed": "invertida"},
        "detail": {
            "upright": "signification direita",
            "reversed": "signification invertida",
        },
    },
    "es": {
        "keywords": {"upright": "a la derecha", "reversed": "invertida"},
        "detail": {
            "upright": "signification a la derecha",
            "reversed": "signification invertida",
        },
    },
    "es_latam": {
        "keywords": {"upright": "a la derecha", "reversed": "invertida"},
        "detail": {
            "upright": "signification a la derecha",
            "reversed": "signification invertida",
        },
    },
    "it": {
        "keywords": {"upright": "dritto", "reversed": "rovesciato"},
        "detail": {
            "upright": "signification dritto",
            "reversed": "signification rovesciato",
        },
    },
    "de": {
        "keywords": {"upright": "aufrecht", "reversed": "umgekehrt"},
        "detail": {
            "upright": "Bedeutung aufrecht",
            "reversed": "Bedeutung umgekehrt",
        },
    },
    "ru": {
        "keywords": {"upright": "прямое", "reversed": "перевернутое"},
        "detail": {
            "upright": "значение прямое",
            "reversed": "значение перевернутое",
        },
    },
    "tr": {
        "keywords": {"upright": "düz", "reversed": "ters"},
        "detail": {
            "upright": "anlam düz",
            "reversed": "anlam ters",
        },
    },
    "ja": {
        "keywords": {"upright": "正位置", "reversed": "逆位置"},
        "detail": {
            "upright": "解釈 正位置",
            "reversed": "解釈 逆位置",
        },
    },
    "zh": {
        "keywords": {"upright": "正位", "reversed": "逆位"},
        "detail": {
            "upright": "含义 正位",
            "reversed": "含义 逆位",
        },
    },
}
"""i18n module - centralise les traductions et mappings de cartes.

Ce module expose une API unique pour :
- tr, get_system_language, set_app_language, MESSAGES
- get_card_image_path, get_french_card_name
- get_card_name_for_lang
- get_cards_signification

Il s'appuie sur les modules existants (translations, card_image_mapping, card_name_mapping, signification)
pour minimiser la duplication et permettre un point d'entrée unique pour la logique i18n.
"""
import os
import json
from pathlib import Path
from functools import lru_cache

# Exposer directement les objets existants depuis les modules spécialisés
try:
    from translations import MESSAGES, tr, get_system_language, set_app_language  # type: ignore
except Exception:
    # Fallbacks très légers si translations manquent
    MESSAGES = {}

    def tr(key: str, **kwargs):
        return kwargs and (str(key).format(**kwargs)) or key

    def get_system_language():
        import os
        return (os.environ.get('APP_LANG') or 'fr')[:2]

    def set_app_language(lang: str):
        # best-effort noop
        return None


# --- JSON per-language loader -------------------------------------------------
# The JSON files live in the `i18n/lang` subfolder of the project root.
LANG_DIR = os.path.join(os.path.dirname(__file__), 'i18n', 'lang')


def _lang_json_path(lang: str) -> str:
    """Return the path to the lang json file if lang provided, else ''."""
    if not lang:
        return ''
    safe = str(lang).lower().replace('-', '_')
    path = os.path.join(LANG_DIR, f"{safe}.json")
    return path

@lru_cache(maxsize=16)
def _load_lang_json(lang: str) -> dict:
    """Charge le JSON de langue si présent. Retourne dict ou {}."""
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


try:
    # prefer the consolidated cards_mapping module
    from cards_mapping import get_card_image_path, get_french_card_name, get_card_name_for_lang  # type: ignore
except Exception:
    # graceful fallbacks when consolidated module is not available
    def get_card_image_path(card_name, state='droite'):
        return 'tarot_img/Back.jpg'

    def get_french_card_name(name):
        return name

    def get_card_name_for_lang(french_name, target_lang):
        return french_name

def get_cards_signification():
    """Retourne le dict des signification en privilégiant les JSON par langue.

    Si la langue courante n'a pas de signification, on tente `fr` comme source
    unique de secours. Ne fait plus appel à `signification.py`.
    """
    try:
        lang = get_system_language()
    except Exception:
        lang = None

    # tenter la langue demandée
    if lang:
        sig = load_lang_significations(lang)
        if sig:
            return sig

    # fallback: utiliser la version française si présente
    try:
        fr_sig = load_lang_significations('fr')
        if fr_sig:
            return fr_sig
    except Exception:
        pass

    return {}

__all__ = [
    'MESSAGES', 'tr', 'get_system_language', 'set_app_language',
    'get_card_image_path', 'get_french_card_name', 'get_card_name_for_lang',
    'get_cards_signification',
    'load_lang_messages', 'load_lang_significations'
]


def load_lang_messages(lang: str) -> dict:
    """Return messages dict from JSON for lang if present, else empty dict."""
    try:
        data = _load_lang_json(lang)
        msgs = data.get('messages', {}) if isinstance(data, dict) else {}
        return msgs or {}
    except Exception:
        return {}


def load_lang_significations(lang: str) -> dict:
    """Return significations dict from JSON for lang if present, else empty dict."""
    try:
        data = _load_lang_json(lang)
        sig = data.get('significations', {}) if isinstance(data, dict) else {}
        return sig or {}
    except Exception:
        return {}


def tr(key: str, lang: str | None = None, **kwargs) -> str:
    """Translate key using per-lang JSON if available, otherwise delegate to original tr().

    If lang is None, uses get_system_language(). This wrapper keeps backward compatibility
    with code that calls tr(key, **kwargs).
    """
    try:
        chosen = lang or get_system_language()
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

    # Fallback to previously imported tr (from translations) if present
    try:
        from translations import tr as _orig_tr  # type: ignore
        return _orig_tr(key, **kwargs)
    except Exception:
        # Very last fallback: try global MESSAGES dict
        try:
            cur = get_system_language()
            txt = MESSAGES.get(cur, MESSAGES.get('fr', {})).get(key, key)
            if kwargs and isinstance(txt, str):
                try:
                    return txt.format(**kwargs)
                except Exception:
                    return txt
            return txt
        except Exception:
            return key


# Note: canonical get_cards_signification is defined earlier in this module and
# returns JSON-based signification data (with 'fr' fallback). No wrapper needed.
