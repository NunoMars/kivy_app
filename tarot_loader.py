import locale

def get_system_language():
    """Détecte la langue du système"""
    try:
        lang = locale.getdefaultlocale()[0]
        if lang and lang.startswith("pt"):
            return "pt"
        elif lang and lang.startswith("en"):
            return "en"
        elif lang and lang.startswith("es"):
            return "es"
        elif lang and lang.startswith("de"):
            return "de"
        elif lang and lang.startswith("it"):
            return "it"
        else:
            return "fr"
    except:
        return "fr"

def get_cards_signification():
    """Charge les significations des cartes selon la langue du système"""
    lang = get_system_language()
    
    try:
        if lang == "fr":
            from signification import cards_signification
        elif lang == "pt":
            from signification_pt import cards_signification
        elif lang == "en":
            from signification_us import cards_signification
        elif lang == "es":
            from signification_es import cards_signification
        elif lang == "de":
            from signification_de import cards_signification
        elif lang == "it":
            from signification_it import cards_signification
        else:
            from signification import cards_signification
        return cards_signification
    except ImportError as e:
        print(f"Erreur d'import des significations: {e}")
        from signification import cards_signification
        return cards_signification

# Mapping des états selon la langue
CARD_STATES = {
    'fr': {
        'upright': "droite",
        'reversed': "a l'envers",
        'signification_prefix': "signification "
    },
    'pt': {
        'upright': "direita",
        'reversed': "invertida",
        'signification_prefix': "signification "
    },
    'en': {
        'upright': "upright",
        'reversed': "reversed",
        'signification_prefix': "signification "
    },
    'es': {
        'upright': "derecha",
        'reversed': "invertida",
        'signification_prefix': "signification "
    },
    'de': {
        'upright': "aufrecht",
        'reversed': "umgekehrt",
        'signification_prefix': "signification "
    },
    'it': {
        'upright': "dritta",
        'reversed': "rovesciata",
        'signification_prefix': "signification "
    }
}

def get_card_state(state_type):
    """Retourne l'état de la carte selon la langue"""
    lang = get_system_language()
    
    if lang in CARD_STATES:
        return CARD_STATES[lang][state_type]
    else:
        # Fallback français
        return CARD_STATES['fr'][state_type]

def get_signification_key(state_type):
    """Retourne la clé de signification selon la langue"""
    lang = get_system_language()
    
    if lang in CARD_STATES:
        return CARD_STATES[lang]['signification_prefix'] + CARD_STATES[lang][state_type]
    else:
        # Fallback français
        return CARD_STATES['fr']['signification_prefix'] + CARD_STATES['fr'][state_type]
