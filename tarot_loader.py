import locale
from signification import cards_signification as cards_fr
from signification_pt import cards_signification as cards_pt

def get_cards_signification():
    """Charge les significations des cartes selon la langue du système"""
    try:
        lang = locale.getdefaultlocale()[0]
        if lang and lang.startswith('pt'):
            return cards_pt
        return cards_fr
    except:
        return cards_fr  # Français par défaut en cas d'erreur

# Mapping des états selon la langue
CARD_STATES = {
    'fr': {
        'upright': "a l'endroit",
        'reversed': "a l'envers",
        'signification_prefix': "signification "
    },
    'pt': {
        'upright': "direita",
        'reversed': "invertida",
        'signification_prefix': "signification "
    }
}

def get_card_state(state_type, lang=None):
    """Retourne l'état de la carte dans la bonne langue"""
    if not lang:
        lang = locale.getdefaultlocale()[0]
        lang = 'pt' if lang and lang.startswith('pt') else 'fr'
    
    return CARD_STATES.get(lang, CARD_STATES['fr']).get(state_type)
