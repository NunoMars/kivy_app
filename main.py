# -*- coding: utf-8 -*-
from __future__ import annotations

# === Imports standards ===
import os
import sys
import re
import uuid
import locale
import random
import threading
import platform
import requests
import traceback
import time
import json
from typing import Optional, TYPE_CHECKING

# === Configuration préliminaire Kivy / Environnement ===
os.environ["KIVY_IMAGE"] = "sdl2"
os.environ["KIVY_DPI"] = "420"
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
os.environ.setdefault("KIVY_NO_FILELOG", "1")

# === Fonction test de connexion ===
def has_internet(timeout: float = 2.0) -> bool:
    try:
        r = requests.head("https://www.google.com/generate_204", timeout=timeout)
        return r.status_code in (200, 204)
    except Exception:
        return False

# === Traductions globales ===
translations = {}

# === Détection de la langue système ===
def pick_supported_lang(tag: str, supported=("fr","en","pt","es","de","it","nl","ru","ja","zh","tr")) -> str:
    if not tag:
        return "en"
    primary = tag.split("-", 1)[0].lower()
    return primary if primary in supported else "en"


def get_system_language() -> str:
    # 1) Variables d'environnement (utile pour tests)
    try:
        forced = os.environ.get("APP_LANG") or os.environ.get("LANGUAGE")
        if forced:
            return forced[:2].lower()
    except Exception:
        pass

    # 2) Détection Android via pyjnius
    try:
        from jnius import autoclass, cast

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        VERSION = autoclass('android.os.Build$VERSION')  # ✅ Correct
        activity = PythonActivity.mActivity
        if activity is None:
            raise RuntimeError("Activity not ready")
        ctx = cast('android.content.Context', activity)

        # Android 13+ : langue par app
        if VERSION.SDK_INT >= 33:
            LocaleManager = autoclass('android.app.LocaleManager')
            svc = ctx.getSystemService(Context.LOCALE_SERVICE)  # ✅ Correct
            lm = cast('android.app.LocaleManager', svc)
            app_locales = lm.getApplicationLocales()
            if app_locales is not None and not app_locales.isEmpty():
                return pick_supported_lang(app_locales.toLanguageTags())

        # Android 7.0+ : locales système
        resources = ctx.getResources()
        config = resources.getConfiguration()
        if VERSION.SDK_INT >= 24:
            locales = config.getLocales()
            if locales is not None and not locales.isEmpty():
                return pick_supported_lang(locales.get(0).toLanguageTag())
        else:
            loc = config.locale
            tag = getattr(loc, 'toLanguageTag', None)
            tag = loc.toLanguageTag() if tag else f"{loc.getLanguage()}-{loc.getCountry()}" if loc.getCountry() else loc.getLanguage()
            return pick_supported_lang(tag)
    except Exception as e:
        print(f"🌍 Échec détection Android avancée: {e}")

    # 3) Fallback locale classique
    try:
        system_locale = (locale.getdefaultlocale()[0] or "").lower()
        for prefix in ("fr","pt","en","es","de","it","nl","ru","ja","zh","tr"):
            if system_locale.startswith(prefix):
                return prefix
    except Exception:
        pass
    return "fr"


# === Imports Kivy après configuration ===
from kivy.config import Config
Config.set("graphics", "width", "540")
Config.set("graphics", "height", "1080")
Config.set("graphics", "multisamples", "0")
Config.set("kivy", "log_level", "warning")
Config.set("kivy", "show_cursor", "1")

import kivy
kivy.require("2.3.1")

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# === Fonts locales ===
BASE_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
if os.path.isdir(FONTS_DIR):
    resource_add_path(FONTS_DIR)
    try:
        LabelBase.register(name="Body", fn_regular="fonts/DejaVuSans.ttf")
    except Exception as e:
        print("### FIX POLICE: fallback police Kivy ->", e)

# === Gestion pyjnius (Android bridge) ===
PYJNIUS_AVAILABLE = True
try:
    import importlib
    jnius = importlib.import_module("jnius")
    autoclass = getattr(jnius, "autoclass", None)
    cast = getattr(jnius, "cast", None)
    from android.runnable import run_on_ui_thread
except Exception:
    PYJNIUS_AVAILABLE = False
    def cast(cls, obj): return obj
    def run_on_ui_thread(func): return func

# === Imports des modules refactorisés ===
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
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
from kivy.utils import platform  # ✅ pour éviter ton bug "platform non défini"

DEFAULT_MME_T_SPACE = "https://huggingface.co/spaces/Loupy222/mme_t"


def _normalize_mme_t_backend_url(raw_url: str) -> str:
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


# === Fallbacks globales ===
translations = {}

def tr(key: str, **kwargs) -> str:
    parts = key.split('.')
    cur = translations
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return ""
    txt = cur
    if kwargs and isinstance(txt, str):
        try:
            return txt.format(**kwargs)
        except Exception:
            return txt
    return txt


MME_T_BACKEND_URL = _normalize_mme_t_backend_url(os.environ.get("MME_T_BACKEND_URL", DEFAULT_MME_T_SPACE))
MME_T_DEFAULT_MODEL = os.environ.get("MME_T_MODEL", "gemini-1.5-flash")

# === Système de compteurs pubs ===
READING_COUNT = 0
ADS_FREQUENCY = 3
def should_show_ad():
    global READING_COUNT
    READING_COUNT += 1
    return READING_COUNT % ADS_FREQUENCY == 0
def reset_reading_count():
    global READING_COUNT
    READING_COUNT = 0


# === Classe principale App ===
class TarotApp(App):
    """Application principale de tarot"""

    def build(self):
        print("🏗️ Construction de l'application Tarot...")
        self.tr = tr
        self.get_cards_signification = get_cards_signification

        # Chargement config et modules
        try:
            self.cfg = load_config()
            print(f"✅ Config chargée: {len(self.cfg)} paramètres")
        except Exception as e:
            print(f"⚠️ Erreur config: {e}")
            self.cfg = {}

        try:
            self.ads = AdsManager(self.cfg)
            print("✅ Gestionnaire de pubs initialisé")
        except Exception as e:
            print(f"⚠️ Erreur pubs: {e}")
            self.ads = None

        try:
            self.billing = InAppPurchaseManager()
            print("✅ Système de facturation initialisé")
        except Exception as e:
            print(f"⚠️ Erreur facturation: {e}")
            self.billing = None

        # Créer l’écran principal
        try:
            root_screen = RootScreen()
            card_screen = CardScreen(name="main_screen")
            response_screen = ResponseScreen(name="response_screen")
            root_screen.add_widget(card_screen)
            root_screen.add_widget(response_screen)
            self.response_screen = response_screen
            if not hasattr(sys, 'getandroidapilevel'):
                response_screen.update_premium_button(True, "2,49€", "simulation")
            root_screen.current = "main_screen"
            print("✅ Écrans créés et configurés")

            # Lancer détection langue après création UI
            Clock.schedule_once(self._init_locale, 0)
            return root_screen
        except Exception as e:
            print(f"❌ Erreur création écrans: {e}")
            traceback.print_exc()
            return None

    def _init_locale(self, *_):
        """Détection tardive de la langue + chargement traductions"""
        global translations
        lang = get_system_language()
        self.lang = lang
        print(f"🌍 Langue détectée: {lang}")
        try:
            path = os.path.join(os.path.dirname(__file__), "i18n", "lang", f"{lang}.json")
            with open(path, "r", encoding="utf-8") as f:
                translations = json.load(f)
            print(f"✅ Traductions chargées pour la langue: {lang}")
            # Rafraîchir les labels traduits de CardScreen
            try:
                card_screen = self.root.get_screen("main_screen")
                card_screen.tr = tr
                card_screen.lang = lang
                card_screen.refresh_translations()
            except Exception as e:
                print(f"⚠️ Erreur mise à jour CardScreen: {e}")
        except Exception as e:
            print(f"⚠️ Erreur chargement {lang}: {e}")
            fallback = os.path.join(os.path.dirname(__file__), "i18n", "lang", "fr.json")
            with open(fallback, "r", encoding="utf-8") as f:
                translations = json.load(f)
            print("✅ Fallback français chargé")


    def on_start(self):
        print("🚀 Application démarrée")

    def on_stop(self):
        print("🛑 Application arrêtée")


# === Loader de signification cartes ===
def get_cards_signification(card_name=None):
    sigs = translations.get("significations", {})
    if card_name:
        if card_name in sigs:
            return sigs[card_name]
        try:
            fr_path = os.path.join(os.path.dirname(__file__), "i18n", "lang", "fr.json")
            with open(fr_path, "r", encoding="utf-8") as f:
                fr_data = json.load(f)
            fr_sigs = fr_data.get("significations", {})
            if card_name in fr_sigs:
                result = fr_sigs[card_name].copy()
                result["fallback"] = True
                print(f"🌍 Fallback français pour carte: {card_name}")
                return result
        except Exception as e:
            print(f"🌍 Erreur fallback français: {e}")
        return {}
    return sigs


# === Gestion erreurs startup ===
def _write_startup_traceback(exc: BaseException) -> None:
    try:
        import traceback as _traceback
        from datetime import datetime as _dt
        tb = _traceback.format_exc()
        now = _dt.utcnow().isoformat() + "Z"
        contents = f"Timestamp: {now}\nException: {exc!r}\n\nTraceback:\n{tb}\n"
        sdcard_path = "/sdcard/macartedetarot_startup_traceback.txt"
        written = False
        try:
            if os.path.exists("/sdcard"):
                with open(sdcard_path, "w", encoding="utf-8") as f:
                    f.write(contents)
                written = True
        except Exception:
            written = False
        if not written:
            local_path = os.path.join(BASE_DIR, "startup_traceback.txt")
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(contents)
        print("--- Startup traceback written ---")
        print(contents)
    except Exception:
        pass


# === Entrée principale ===
if __name__ == "__main__":
    try:
        TarotApp().run()
    except BaseException as e:
        _write_startup_traceback(e)
        raise
