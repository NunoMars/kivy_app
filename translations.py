import locale

MESSAGES = {
    "fr": {
        "draw_card": "TIRER UNE CARTE",
        "drawing_card": "JE TIRE UNE CARTE...",
        "concentrating": "Concentration en cours...",
        "preparing_arcana": "Préparation des arcanes...",
        "upright": "⬆ À L'ENDROIT ⬆",
        "reversed": "⬇ À L'ENVERS ⬇",
        "thanks": "✨ J'espère que votre prédiction vous a plu ! ✨",
        "continue_exploring": "🔮 Continuez à explorer les mystères du tarot ! 🔮",
        "new_reading": "✨ Nouveau tirage",
        "new_reading_countdown": "✨ Nouveau tirage ({seconds}s) ✨",
        "app_title": "Bienvenue dans le tarot divinatoire",
        "draw_instruction": "Touchez la carte\npour une prédiction",
        "crystals_ad": "💎 Boutique Cristaux & Minéraux - Livraison gratuite 💎",
        "love_ad": "💕 Trouvez l'Amour avec Astrologie+ 💕\nCompatibilité amoureuse basée sur votre thème astral",
        "tarot_course_ad": "🔮 Formation Tarot Professionnel 🔮\nDevenez cartomancien certifié - Inscription gratuite",
        "tap_to_return": "Touchez la carte pour revenir",
        "touch_to_enlarge": "🔍 Touchez pour agrandir",
        "your_card": "Votre carte",
        "support_app": "Soutenez l'application",
        "ad_message": "Cette application gratuite vous plaît ?\nAidez-nous à la maintenir et l'améliorer !",
        "later": "Plus tard",
        "support": "Soutenir",
    },
    "pt": {
        "draw_card": "TIRAR UMA CARTA",
        "drawing_card": "ESTOU A TIRAR UMA CARTA...",
        "concentrating": "A concentrar...",
        "preparing_arcana": "A preparar os arcanos...",
        "upright": "⬆ DIREITA ⬆",
        "reversed": "⬇ INVERTIDA ⬇",
        "thanks": "✨ Espero que tenha gostado da sua previsão! ✨",
        "continue_exploring": "🔮 Continue a explorar os mistérios do tarot! 🔮",
        "new_reading": "✨ Nova leitura",
        "new_reading_countdown": "✨ Nova leitura ({seconds}s) ✨",
        "app_title": "Bem-vindo ao tarot divinatório",
        "draw_instruction": "Toque na carta\npara uma previsão",
        "crystals_ad": "💎 Loja de Cristais & Minerais - Envio grátis 💎",
        "love_ad": "💕 Encontre o Amor com Astrologia+ 💕\nCompatibilidade amorosa baseada no seu mapa astral",
        "tarot_course_ad": "🔮 Curso Profissional de Tarot 🔮\nTorne-se cartomante certificado - Inscrição gratuita",
        "tap_to_return": "Toque na carta para voltar",
        "touch_to_enlarge": "🔍 Toque para ampliar",
        "your_card": "Sua carta",
        "support_app": "Apoie o App",
        "ad_message": "Gosta desta aplicação gratuita?\nAjude-nos a mantê-la e melhorá-la!",
        "later": "Mais tarde",
        "support": "Apoiar",
    },
    "en": {
        "draw_card": "DRAW A CARD",
        "drawing_card": "I'M DRAWING A CARD...",
        "concentrating": "Concentrating...",
        "preparing_arcana": "Preparing the arcana...",
        "upright": "⬆ UPRIGHT ⬆",
        "reversed": "⬇ REVERSED ⬇",
        "thanks": "✨ I hope you enjoyed your reading! ✨",
        "continue_exploring": "🔮 Continue exploring the mysteries of tarot! 🔮",
        "new_reading": "✨ New reading",
        "new_reading_countdown": "✨ New reading ({seconds}s) ✨",
        "app_title": "Welcome to divination tarot",
        "draw_instruction": "Touch the card\nfor a prediction",
        "crystals_ad": "💎 Crystals & Minerals Shop - Free shipping 💎",
        "love_ad": "💕 Find Love with Astrology+ 💕\nLove compatibility based on your birth chart",
        "tarot_course_ad": "🔮 Professional Tarot Course 🔮\nBecome a certified cartomancer - Free registration",
        "tap_to_return": "Tap the card to return",
        "touch_to_enlarge": "🔍 Touch to enlarge", 
        "your_card": "Your card",
        "support_app": "Support the App",
        "ad_message": "Do you like this free application?\nHelp us maintain and improve it!",
        "later": "Later",
        "support": "Support",
    }
}

def get_system_language():
    """Détecte la langue du système"""
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            if system_locale.startswith('fr'):
                return 'fr'
            elif system_locale.startswith('pt'):
                return 'pt'
            elif system_locale.startswith('en'):
                return 'en'
    except:
        pass
    return 'fr'  # Français par défaut

def tr(key, **kwargs):
    """Traduit une clé selon la langue du système"""
    current_language = get_system_language()
    
    if current_language in MESSAGES and key in MESSAGES[current_language]:
        message = MESSAGES[current_language][key]
    elif key in MESSAGES['fr']:  # Fallback français
        message = MESSAGES['fr'][key]
    else:
        message = key  # Retourne la clé si aucune traduction
    
    # Formatter avec les paramètres si nécessaire
    try:
        return message.format(**kwargs)
    except:
        return message
