# -*- coding: utf-8 -*-
"""
Module signification - Interface unifiée pour les significations de cartes
Importe depuis le module de langue approprié selon CURRENT_LANG
"""

import os
import locale

def get_system_language() -> str:
    try:
        lang = os.environ.get("LANG", "") or locale.getdefaultlocale()[0] or ""
        if isinstance(lang, str):
            lang = lang.lower()
            if lang.startswith("pt"):
                return "pt"
            if lang.startswith("en"):
                return "en"
        return "fr"
    except Exception:
        return "fr"

CURRENT_LANG = get_system_language()

# Import depuis le module de langue approprié
if CURRENT_LANG == "fr":
    from signification_fr import get_cards_signification
elif CURRENT_LANG == "en":
    from signification_en import get_cards_signification
elif CURRENT_LANG == "pt":
    from signification_pt import get_cards_signification
else:
    # Fallback vers français
    from signification_fr import get_cards_signification

# Import des fonctions communes
from card_name_mapping import get_card_name_for_lang
from card_image_mapping import get_card_image_path