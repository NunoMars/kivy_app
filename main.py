# -*- coding: utf-8 -*-
from __future__ import annotations
# Regroupement propre des imports et configuration initiale

# Standard library
import os
import sys
import re
import uuid
import locale
import random
import threading
# time import removed (unused)

from typing import Optional

# Third-party
import platform
import requests

# Local modules
from translations import MESSAGES

# Ads manager (local) — import sécurisé car peut échouer en environnement non-Android
try:
    from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
except Exception:
    def load_config():
        return {}

    class AdsManager:  # simple fallback stub
        def __init__(self, cfg):
            self.cfg = cfg

    def maybe_fetch_remote_config(cfg):
        return None

# Optional gradio client
try:
    from gradio_client import Client as GradioClient
    GRADIO_CLIENT_AVAILABLE = True
except Exception:
    GRADIO_CLIENT_AVAILABLE = False

# --- Kivy configuration (doit précéder l'import de Kivy lui-même) ---
# Choix du provider de texte / emoji selon plateforme
if platform.system() == "Linux" and "DISPLAY" not in os.environ:
    # Headless Linux: éviter d'imposer PIL provider
    os.environ.setdefault("KIVY_TEXT", "")
else:
    os.environ.setdefault("KIVY_TEXT", "pil")

# Trouver une police emoji courante
emoji_paths = []
if platform.system() == "Linux":
    emoji_paths = [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf",
    ]
elif platform.system() == "Windows":
    emoji_paths = [
        r"C:\Windows\Fonts\seguiemj.ttf",
        r"C:\Windows\Fonts\SegoeUIEmoji.ttf",
        r"C:\Windows\Fonts\Segoe UI Emoji.ttf",
    ]

# Kivy Config must be set before importing Kivy widgets
from kivy.config import Config  # noqa: E402
available_emoji = [p for p in emoji_paths if os.path.exists(p)]
Config.set("kivy", "default_font", ["DejaVuSans.ttf"] + available_emoji)
if available_emoji:
    try:
        from kivy.core.text import LabelBase

        LabelBase.register(name="emoji", fn_regular=available_emoji[0])
    except Exception:
        pass

os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
os.environ.setdefault("KIVY_NO_FILELOG", "1")
Config.set("graphics", "width", "300")
Config.set("graphics", "height", "600")
Config.set("kivy", "log_level", "warning")
Config.set("kivy", "show_cursor", "1")

# Import Kivy after configuration
import kivy  # noqa: E402
kivy.require("2.3.1")

# Kivy imports (grouped)  # noqa: E402
from kivy.app import App  # noqa: E402
from kivy.clock import Clock  # noqa: E402
from kivy.animation import Animation  # noqa: E402
from kivy.metrics import dp  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, Screen  # noqa: E402
from kivy.uix.label import Label  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
from kivy.uix.boxlayout import BoxLayout  # noqa: E402
from kivy.uix.image import Image  # noqa: E402
from kivy.uix.floatlayout import FloatLayout  # noqa: E402
from kivy.uix.popup import Popup  # noqa: E402
from kivy.uix.anchorlayout import AnchorLayout  # noqa: E402
from kivy.uix.scrollview import ScrollView  # noqa: E402
from kivy.uix.textinput import TextInput  # noqa: E402
from kivy.graphics import Color, Rectangle, RoundedRectangle  # noqa: E402

# JNI / Android (pyjnius) — optional with robust fallback
from typing import TYPE_CHECKING
PYJNIUS_AVAILABLE = True

# Provide static-only imports for type checkers / IDEs without forcing runtime import.
if TYPE_CHECKING:
    # These imports are only for linters/type-checkers and will not be executed at runtime.
    from jnius import autoclass, cast, JavaException, PythonJavaClass, java_method  # type: ignore

# Runtime-safe dynamic import with graceful fallback if jnius is not available.
try:
    import importlib

    jnius = importlib.import_module("jnius")
    autoclass = getattr(jnius, "autoclass", None)
    cast = getattr(jnius, "cast", None)
    JavaException = getattr(jnius, "JavaException", Exception)
    PythonJavaClass = getattr(jnius, "PythonJavaClass", type("PythonJavaClass", (), {}))
    java_method = getattr(jnius, "java_method", lambda sig: (lambda f: f))

    try:
        from android.runnable import run_on_ui_thread  # type: ignore
    except Exception:
        def run_on_ui_thread(func):
            return func

except Exception:
    PYJNIUS_AVAILABLE = False
    autoclass = None

    def cast(cls, obj):
        return obj

    JavaException = Exception

    class PythonJavaClass:
        pass

    def java_method(signature):
        def decorator(func):
            return func
        return decorator

    def run_on_ui_thread(func):
        return func

# Import des modules refactorisés
from billing import (
    GooglePurchasesUpdatedListener,
    GoogleBillingStateListener,
    GoogleProductDetailsListener,
    LaunchBillingRunnable,
    AmazonPurchasingListener,
    InAppPurchaseManager,
)
from popups import (
    ChatBubble,
    AdPopup,
    FullScreenCardPopup,
    LoadingPopup,
    MmeTChatPopup,
    AdsPopup,
)
from screens import (
    RootScreen,
    CardScreen,
    ResponseScreen,
)

# Defaults
DEFAULT_MME_T_SPACE = "https://huggingface.co/spaces/Loupy222/mme_t"


def _normalize_mme_t_backend_url(raw_url: str) -> str:
    """Normalise une URL de backend Mme T en renvoyant une URL finale.
    Exemple: converts 'https://huggingface.co/spaces/Owner/space' to 'https://owner-space.hf.space'
    """
    url = (raw_url or "").strip()
    if not url:
        return ""
    url = url.rstrip("/")
    if "huggingface.co/spaces/" in url:
        suffix = url.split("huggingface.co/spaces/")[-1].strip("/")
        if suffix:
            parts = suffix.split("/")
            if len(parts) >= 2:
                owner, space = parts[:2]
                owner_slug = re.sub(r"[^a-z0-9-]", "-", owner.lower())
                space_slug = re.sub(r"[^a-z0-9-]", "-", space.lower())
                owner_slug = owner_slug.strip("-") or owner.lower()
                space_slug = space_slug.strip("-") or space.lower()
                return f"https://{owner_slug}-{space_slug}.hf.space"
    return url


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
print(f"🌍 Langue détectée: {CURRENT_LANG}")


def tr(key: str, **kwargs) -> str:
    txt = MESSAGES.get(CURRENT_LANG, MESSAGES.get("fr", {})).get(key, "")
    if kwargs and isinstance(txt, str):
        try:
            return txt.format(**kwargs)
        except Exception:
            return txt
    return txt


MME_T_BACKEND_URL = _normalize_mme_t_backend_url(os.environ.get("MME_T_BACKEND_URL", DEFAULT_MME_T_SPACE))
MME_T_DEFAULT_MODEL = os.environ.get("MME_T_MODEL", "gemini-1.5-flash")

# Note: Kivy Config a déjà été réglé plus haut; ici on évite ré-imports redondants.

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
}

# Import des significations selon la langue détectée
# Le gestionnaire de publicités `ads_manager` a été importé en haut avec fallback sécurisé
try:
    if CURRENT_LANG == "en":
        from signification_en import get_cards_signification  # Maintenant correct !
        print("✓ Significations EN importées")
    elif CURRENT_LANG == "pt": 
        from signification_pt import get_cards_signification
        print("✓ Significations PT importées")
    else:
        from signification_fr import get_cards_signification
        print("✓ Significations FR importées")
except Exception as e:
    print(f"✗ Erreur significations: {e}")

try:
    from card_image_mapping import get_card_image_path
    print("✓ Mapping images importé")
except Exception as e:
    print(f"✗ Erreur mapping: {e}")
    def get_card_image_path(card, state):
        base_path = "tarot_img/MajorArcanaCards"
        if state == "a l'envers":
            return os.path.join(base_path, f"{card} a l'envers.jpg")
        return os.path.join(base_path, f"{card}.jpg")


try:
    from card_name_mapping import get_card_name_for_lang
    print("✓ Card name mapping importé")
except Exception as e:
    print(f"✗ Erreur card name mapping: {e}")
    def get_card_name_for_lang(french_name, target_lang):
        return french_name


# Système de compteur pour les publicités
READING_COUNT = 0
ADS_FREQUENCY = 3  # Afficher une pub toutes les 3 lectures

def should_show_ad():
    """Détermine s'il faut afficher une publicité"""
    global READING_COUNT
    READING_COUNT += 1
    return READING_COUNT % ADS_FREQUENCY == 0

def reset_reading_count():
    """Remet le compteur à zéro (pour les tests)"""
    global READING_COUNT
    READING_COUNT = 0


class TarotApp(App):
    """Application principale de tarot"""

    def build(self):
        """Construit l'application"""
        print("🏗️ Construction de l'application Tarot...")

        # Charger la configuration
        try:
            self.cfg = load_config()
            print(f"✅ Config chargée: {len(self.cfg)} paramètres")
        except Exception as e:
            print(f"⚠️ Erreur config: {e}")
            self.cfg = {}

        # Initialiser le gestionnaire de publicités
        try:
            self.ads = AdsManager(self.cfg)
            print("✅ Gestionnaire de pubs initialisé")
        except Exception as e:
            print(f"⚠️ Erreur pubs: {e}")
            self.ads = None

        # Initialiser le système de facturation
        try:
            self.billing = InAppPurchaseManager()
            print("✅ Système de facturation initialisé")
        except Exception as e:
            print(f"⚠️ Erreur facturation: {e}")
            self.billing = None

        # Créer l'écran racine avec les écrans
        try:
            root_screen = RootScreen()

            # Ajouter les écrans
            card_screen = CardScreen(name="main_screen")
            response_screen = ResponseScreen(name="response_screen")

            root_screen.add_widget(card_screen)
            root_screen.add_widget(response_screen)

            # Forcer le bouton premium actif en mode desktop/test
            import sys
            if not hasattr(sys, 'getandroidapilevel'):
                # On est en desktop, simuler la boutique prête
                response_screen.update_premium_button(True, "2,49€", "simulation")

            # Démarrer sur l'écran principal
            root_screen.current = "main_screen"

            print("✅ Écrans créés et configurés")
            return root_screen

        except Exception as e:
            print(f"❌ Erreur création écrans: {e}")
            import traceback
            traceback.print_exc()
            return None

    def on_purchase_success(self, product_id, provider):
        """Callback appelé quand un achat est réussi"""
        print(f"✅ Achat réussi: {product_id} via {provider}")

        # Ouvrir le chat Mme T si c'est le bon produit
        if product_id == "premium_chat_luna":
            try:
                app = App.get_running_app()
                if app and app.root:
                    response_screen = app.root.get_screen("response_screen")
                    if response_screen:
                        response_screen.open_mme_t_chat(provider=provider)
            except Exception as e:
                print(f"❌ Erreur ouverture chat: {e}")

    def on_purchase_error(self, message, provider="unknown"):
        """Callback appelé en cas d'erreur d'achat"""
        print(f"❌ Erreur achat ({provider}): {message}")

        # Afficher un popup d'erreur
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.uix.boxlayout import BoxLayout

            layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
            label = Label(text=f"Erreur d'achat:\n{message}")
            btn = Button(text="Fermer", size_hint_y=None, height=40)
            layout.add_widget(label)
            layout.add_widget(btn)

            popup = Popup(title="Erreur", content=layout, size_hint=(0.8, 0.4))
            btn.bind(on_release=popup.dismiss)
            popup.open()

        except Exception as e:
            print(f"❌ Erreur affichage popup: {e}")

    def on_start(self):
        """Appelé au démarrage de l'application"""
        print("🚀 Application démarrée")

    def on_stop(self):
        """Appelé à l'arrêt de l'application"""
        print("🛑 Application arrêtée")


if __name__ == "__main__":
    TarotApp().run()










