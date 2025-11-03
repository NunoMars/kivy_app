# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import sys
import re
import uuid
import locale
import random
import threading
import requests
import traceback
import time
import json

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

# === Config Kivy (avant import kivy) ===
from kivy.config import Config
IS_ANDROID = "ANDROID_ARGUMENT" in os.environ  # <- fiable avec p4a

if not IS_ANDROID:
    Config.set("graphics", "width", "540")
    Config.set("graphics", "height", "1080")
    Config.set("graphics", "multisamples", "0")
    Config.set("kivy", "log_level", "warning")
    Config.set("kivy", "show_cursor", "1")
    os.environ["KIVY_DPI"] = "420"  # simulation desktop seulement
else:
    # Sur Android, ne force rien
    os.environ.pop("KIVY_DPI", None)


import kivy
kivy.require("2.3.1")

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, DictProperty, ListProperty
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
from kivy.resources import resource_find, resource_add_path
from kivy.logger import Logger
from kivy.utils import platform as kivy_platform  # évite la collision avec le stdlib

# === Fonts locales ===
BASE_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
if os.path.isdir(FONTS_DIR):
    resource_add_path(FONTS_DIR)
    try:
        LabelBase.register(name="Body", fn_regular="fonts/DejaVuSans.ttf")
    except Exception as e:
        print("### FIX POLICE: fallback police Kivy ->", e)

# Police par défaut utilisée dans toute l’app (doit correspondre au nom enregistré via LabelBase.register)
BODY_FONT = "Body"

# === Gestion pyjnius (Android bridge) ===
PYJNIUS_AVAILABLE = True
try:
    import importlib
    jnius = importlib.import_module("jnius")
    autoclass = getattr(jnius, "autoclass", None)
    cast = getattr(jnius, "cast", None)
    try:
        from android.runnable import run_on_ui_thread
    except Exception:
        # Desktop fallback
        def run_on_ui_thread(func):
            return func
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
    AboutScreen,
)
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config

DEFAULT_MME_T_SPACE = "https://huggingface.co/spaces/Loupy222/mme_t"
# === Fonction debug i18n ===
def debug_check_i18n():
    rel = "i18n/lang/fr.json"
    path = resource_find(rel)
    print(f"[I18N DEBUG] resource_find({rel}) -> {path}")
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[I18N DEBUG] open OK, top-level keys: {list(data.keys())[:5]}")
        except Exception as e:
            print(f"[I18N DEBUG] open FAILED: {e}")
    else:
        print("[I18N DEBUG] path is None or file missing on filesystem")

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
                owner_slug = re.sub(r"[^a-z0-9-]", "-", owner.lower()).strip("-") or owner.lower()
                space_slug = re.sub(r"[^a-z0-9-]", "-", space.lower()).strip("-") or space.lower()
                return f"https://{owner_slug}-{space_slug}.hf.space"
    return url

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

def debug_list_i18n_dir():
    # resource_find ne marche pas pour un dossier; on log juste la vue locale s'il existe
    base = os.path.join(BASE_DIR, "i18n", "lang")
    if os.path.isdir(base):
        try:
            files = os.listdir(base)
            Logger.info(f"I18N: local dir {base} -> {files}")
        except Exception as e:
            Logger.error(f"I18N: cannot list {base}: {e}")
    else:
        Logger.info("I18N: no local i18n/lang directory (OK on Android)")

class TarotApp(App):
    """Application principale de tarot"""

    def __init__(self, **kw):
        super().__init__(**kw)
        debug_list_i18n_dir()  # Sanity check visible dans le logcat
        self.lang = self.get_system_lang()
        self.i18n = self.load_i18n(self.lang)
        self.tr = self._tr
        self.get_cards_signification = self._get_cards_signification
        # --- AJOUT IAP (flag premium) ---
        self.enable_premium = False

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

    def get_system_lang(self) -> str:
        forced = os.environ.get("APP_LANG") or os.environ.get("LANGUAGE")
        if forced:
            lang = forced[:2].lower()
        else:
            if PYJNIUS_AVAILABLE:
                try:
                    LocaleList = autoclass('android.os.LocaleList')
                    Build = autoclass('android.os.Build')
                    Locale = autoclass('java.util.Locale')
                    if Build.VERSION.SDK_INT >= 24:
                        locales = LocaleList.getDefault()
                        if locales and locales.size() > 0:
                            lang = locales.get(0).getLanguage()
                        else:
                            lang = Locale.getDefault().getLanguage()
                    else:
                        lang = Locale.getDefault().getLanguage()
                except Exception:
                    lang = (locale.getdefaultlocale()[0] or 'en')[:2]
            else:
                lang = (locale.getdefaultlocale()[0] or 'en')[:2]

        # Sélectionne une langue supportée
        l = lang.lower()
        return ('fr' if l.startswith('fr') else
                'pt' if l.startswith('pt') else
                'es' if l.startswith('es') else
                'de' if l.startswith('de') else
                'it' if l.startswith('it') else
                'nl' if l.startswith('nl') else
                'ru' if l.startswith('ru') else
                'ja' if l.startswith('ja') else
                'zh' if l.startswith('zh') else
                'tr' if l.startswith('tr') else 'en')

    def load_i18n(self, lang_code: str) -> dict:
        lc = (lang_code or "").strip().lower()
        candidates = [
            f"i18n/lang/{lc}.json",   # langue demandée
            "i18n/lang/en.json",      # fallback unique
        ]

        last_err = None
        for rel in candidates:
            # 1) Ressource packagée (Android / desktop si resource_add_path a été appelé)
            path = resource_find(rel)
            if path:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    Logger.info(f"I18N: loaded packaged '{rel}' -> {path}")                  
                    return data
                except Exception as e:
                    last_err = e
                    Logger.error(f"I18N: read error for packaged '{path}': {e}")
                    continue

            # 2) Fallback dev (exécution depuis sources)
            if os.path.exists(rel):
                try:
                    with open(rel, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    Logger.info(f"I18N: loaded local '{rel}'")
                    print(f"I18N: loaded local '{rel}'")
                    return data
                except Exception as e:
                    last_err = e
                    Logger.error(f"I18N: read error for local '{rel}': {e}")
                    continue

            Logger.debug(f"I18N: candidate not found: {rel}")

        raise FileNotFoundError(f"I18N: not found {candidates}. last_err={last_err}")

    def _tr(self, key, **kwargs):
        # key peut être "messages.app_title" ou "significations.major_00.name"
        parts = key.split('.')
        val = self.i18n
        try:
            for p in parts:
                val = val[p]
            if kwargs and isinstance(val, str):
                try:
                    return val.format(**kwargs)
                except Exception:
                    return val
            return val
        except Exception:
            return f"[{key}]"

    def _get_cards_signification(self):
        return self.i18n.get("significations", {})

    def build(self):
        # Police disponible pour tous les écrans via App.get_running_app().font_body
        self.font_body = BODY_FONT
        print("🏗️ Construction de l'application Tarot...")
        try:
            root_screen = RootScreen()
            card_screen = CardScreen(name="card_screen")
            response_screen = ResponseScreen(name="response_screen")
            about_screen = AboutScreen(name="about_screen")
            root_screen.add_widget(card_screen)
            root_screen.add_widget(response_screen)
            root_screen.add_widget(about_screen)
            self.response_screen = response_screen

            # Les traductions et polices sont appliquées dans on_start (UI attachée)

            # Simule le prix premium sur desktop
            if not hasattr(sys, 'getandroidapilevel'):
                response_screen.update_premium_button(True, "2,49€", "simulation")

            root_screen.current = "card_screen"
            print("✅ Écrans créés et configurés")
            return root_screen
        except Exception as e:
            print(f"❌ Erreur création écrans: {e}")
            traceback.print_exc()
            return None

    def on_start(self):
        print("🚀 Application démarrée")
        debug_check_i18n()
        # Programme l'application des traductions et police au prochain frame
        try:
            from kivy.clock import Clock
            def _apply_all(_dt):
                try:
                    root = getattr(self, 'root', None)
                    if not root:
                        return
                    for scr in getattr(root, 'screens', []) or []:
                        try:
                            if hasattr(scr, 'apply_i18n'):
                                scr.apply_i18n()
                            if hasattr(scr, '_refresh_fonts'):
                                scr._refresh_fonts()
                        except Exception as e:
                            print(f"⚠️ Warning applying i18n/fonts in on_start for {scr}: {e}")
                    # Ajoute un overlay global de debug au-dessus de tout pour vérifier le rendu texte
                    # Désactivé par défaut en production. Pour activer temporairement, exportez:
                    # DEBUG_GLOBAL_OVERLAY=1
                    try:
                        if os.environ.get('DEBUG_GLOBAL_OVERLAY', '0') != '1':
                            # Overlay disabled by default
                            print('MAIN: global debug overlay disabled')
                        else:
                            from kivy.uix.floatlayout import FloatLayout
                            from kivy.uix.label import Label
                            from kivy.graphics import Color, Rectangle

                            # Determine proper target to receive the overlay: prefer the active Screen
                            target = None
                            try:
                                if hasattr(root, 'current_screen') and root.current_screen is not None:
                                    target = root.current_screen
                                elif hasattr(root, 'get_screen') and getattr(root, 'current', None):
                                    try:
                                        target = root.get_screen(root.current)
                                    except Exception:
                                        target = None
                            except Exception:
                                target = None
                            if target is None:
                                target = root

                            overlay = FloatLayout()

                            with overlay.canvas.before:
                                Color(0, 0, 0, 0.85)
                                # use target size so the bg matches the screen/container
                                bg = Rectangle(pos=(0, 0), size=(getattr(target, 'width', 0), getattr(target, 'height', 0)))

                            # Bind pour suivre la taille du target
                            def _sync_rect(inst, val):
                                try:
                                    bg.size = (getattr(target, 'width', 0), getattr(target, 'height', 0))
                                except Exception:
                                    pass
                            try:
                                target.bind(size=_sync_rect)
                            except Exception:
                                pass

                            lbl = Label(text=f"DEBUG GLOBAL: lang={getattr(self, 'lang', None)}\ntr(app_title)={self._tr('messages.app_title')}", halign='center', valign='middle', color=(1,1,1,1), font_size='22sp')
                            lbl.bind(size=lambda i,v: setattr(i, 'text_size', v))
                            overlay.add_widget(lbl)

                            try:
                                # add overlay to the determined target (Screen or root fallback)
                                target.add_widget(overlay)
                                print("MAIN: global debug overlay added to target", target)
                                # suppression après 20s
                                from kivy.clock import Clock as _Clock
                                def _remove_overlay(__dt):
                                    try:
                                        if overlay.parent:
                                            overlay.parent.remove_widget(overlay)
                                    except Exception:
                                        pass
                                _Clock.schedule_once(_remove_overlay, 20)
                            except Exception as e:
                                print(f"⚠️ Could not add global overlay to target: {e}")
                    except Exception as e:
                        print(f"⚠️ Error building global overlay: {e}")
                except Exception as e:
                    print(f"⚠️ Error in scheduled screen refresh: {e}")
            Clock.schedule_once(_apply_all, 0)
        except Exception as e:
            print(f"⚠️ Error scheduling screen refresh: {e}")

    def on_stop(self):
        print("🛑 Application arrêtée")
        
 # --- AJOUT IAP : action bouton "Acheter Premium" ---
    def on_buy_premium(self, *_):
        try:
            if self.billing and self.billing.is_ready():
                self.billing.purchase_product("premium_features")
            else:
                print("Paiement non prêt")
        except Exception as e:
            print(f"⚠️ Erreur on_buy_premium: {e}")

    # --- AJOUT IAP : callback succès appelé par billing.py ---
    def on_purchase_success(self, product_id, provider):
        try:
            if product_id == "premium_features":
                self.enable_premium = True
                print(f"✨ Premium activé ! (provider={provider})")

                # Optionnel : mettre à jour le bouton premium si l'écran l’expose
                try:
                    if hasattr(self, 'response_screen') and hasattr(self.response_screen, 'update_premium_button'):
                        # On masque/désactive le bouton d’achat côté UI
                        price_txt = None
                        try:
                            if self.billing:
                                price_txt = self.billing.get_product_price()
                        except Exception:
                            price_txt = None
                        self.response_screen.update_premium_button(False, price_txt, provider)
                except Exception as _e:
                    print(f"ℹ️ UI non mise à jour (facultatif): {_e}")
        except Exception as e:
            print(f"⚠️ Erreur on_purchase_success: {e}")
            self.enable_premium = False

# === Loader de signification cartes ===
def get_cards_signification(card_name=None):
    app = App.get_running_app()
    i18n = getattr(app, "i18n", {}) or {}
    sigs = i18n.get("significations", {})
    if card_name:
        return sigs.get(card_name, {})  # aucun I/O, pas de fallback fichier
    return sigs


# === Entrée principale ===
if __name__ == "__main__":
    try:
        TarotApp().run()
    except BaseException as e:
        print(f"❌ Erreur fatale application: {e}")
        raise
