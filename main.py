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
try:
    from plyer import notification as plyer_notification  # notifications locales
except Exception:
    plyer_notification = None
try:
    # Pour planifier l'alarme native via pyjnius
    import jnius
    _autoclass = jnius.autoclass
except Exception:
    _autoclass = None

# === Fonts locales ===
BASE_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
# Rendez disponibles les chemins locaux pour resource_find, utile sur Android
try:
    resource_add_path(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, "i18n")):
        resource_add_path(os.path.join(BASE_DIR, "i18n"))
except Exception:
    pass
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
        # Tirage / notifications
        self.enable_premium = False
        self._last_draw_date = None  # YYYY-MM-DD
        self._load_last_draw_date()
        # Consentement pubs (placeholder UMP): None=unknown, True/False
        self.consent_personalized = self._load_consent()
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

        # Appliquer une politique simple selon le consentement (placeholder UMP)
        try:
            if self.consent_personalized is None:
                # Consentement inconnu → activer pubs NON personnalisées (NPA) par défaut
                # Conforme RGPD : pubs contextuelles sans tracking utilisateur
                self.cfg["ads_enabled"] = True
                print("ℹ️ Consentement inconnu → pubs non personnalisées activées (NPA)")
            elif self.consent_personalized is False:
                # Pas de consentement → activer seulement des pubs non personnalisées (pas de test ads en prod)
                # TODO: brancher NPA=1 via wrapper KivMob quand exposé; en attendant on garde production standard.
                self.cfg["ads_enabled"] = True
                print("ℹ️ Consentement refusé → pubs non personnalisées activées (NPA)")
            else:
                # Consentement accordé → pubs personnalisées autorisées
                self.cfg["ads_enabled"] = True
                print("ℹ️ Consentement accordé → pubs personnalisées activées")
        except Exception:
            pass

        # AdsManager pré-initialisation (sera configuré après UMP + MobileAds.init)
        self.ads = None
        self._mobile_ads_ready = False
        print("ℹ️ Ads init différée jusqu'au MobileAds SDK ready")

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
                # Essai robuste via PythonActivity puis fallback LocaleList/Locale
                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = getattr(PythonActivity, 'mActivity', None) or PythonActivity.getApplication()
                    res = activity.getResources()
                    config = res.getConfiguration()
                    try:
                        locales = config.getLocales()
                        if locales and locales.size() > 0:
                            lang = locales.get(0).getLanguage()
                        else:
                            lang = config.locale.getLanguage()
                    except Exception:
                        lang = config.locale.getLanguage()
                except Exception:
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
            path = resource_find(rel) or resource_find(os.path.join("assets", rel))
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

            # 2) Fallback dev (exécution depuis sources) - chemin absolu depuis BASE_DIR
            abs_local = os.path.join(BASE_DIR, rel)
            if os.path.exists(abs_local):
                try:
                    with open(abs_local, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    Logger.info(f"I18N: loaded local '{abs_local}'")
                    return data
                except Exception as e:
                    last_err = e
                    Logger.error(f"I18N: read error for local '{abs_local}': {e}")
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
        try:
            self._schedule_daily_draw_reminder()
        except Exception as e:
            print(f"⚠️ schedule reminder failed: {e}")
        # Planifier alarm native (si Android)
        try:
            if _autoclass is not None and kivy_platform == 'android':
                PythonActivity = _autoclass('org.kivy.android.PythonActivity')
                ctx = getattr(PythonActivity, 'mActivity', None)
                if ctx is not None:
                    AlarmScheduler = _autoclass('org.tarot.AlarmScheduler')
                    AlarmScheduler.scheduleDaily(ctx)
                    print("⏰ AlarmManager: rappel quotidien planifié (natif)")
        except Exception as e:
            print(f"⚠️ AlarmManager schedule failed: {e}")

        # UMP: lancer la requête de consentement native et POLLER jusqu'à 8s (300–500ms)
        try:
            if _autoclass is not None and kivy_platform == 'android':
                PythonActivity = _autoclass('org.kivy.android.PythonActivity')
                act = getattr(PythonActivity, 'mActivity', None)
                ConsentBridge = _autoclass('org.tarot.ConsentBridge')
                if act is not None and ConsentBridge is not None:
                    ConsentBridge.request(act)
                    self._ump_elapsed = 0.0
                    def _poll_consent(_dt):
                        try:
                            self._ump_elapsed += _dt
                            res = ConsentBridge.getResult()
                            decided = (res is not None)
                            timeout = self._ump_elapsed >= 8.0
                            if decided or timeout:
                                Clock.unschedule(_poll_consent)
                                # Politique release: par défaut pas de personnalisation (NPA)
                                if not decided:
                                    effective = False
                                    print("🧾 UMP timeout -> personnalisation=False (par défaut)")
                                else:
                                    # Si UMP dit non requis, nous restons non personnalisés par défaut.
                                    effective = False if bool(res) else False
                                    print(f"🧾 UMP décidé (res={bool(res)}) -> personnalisation={effective}")
                                self.set_user_consent(effective)
                                # CORRECTIF: Ne plus créer AdsManager ici, il sera créé par _on_init_complete
                                # après MobileAds.initialize() qui est appelé plus tard dans on_start()
                                print("ℹ️ Consentement enregistré, ads seront initialisées après MobileAds.init")
                        except Exception as _e:
                            print(f"⚠️ UMP poll failed: {_e}")
                    from kivy.clock import Clock as _Clock
                    _Clock.schedule_interval(_poll_consent, 0.4)
        except Exception as e:
            print(f"⚠️ UMP request failed: {e}")
        # --- Initialisation Mobile Ads (Google) non bloquante ---
        try:
            if PYJNIUS_AVAILABLE and os.environ.get('DISABLE_MOBILE_ADS','0') != '1':
                from jnius import autoclass  # type: ignore
                MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
                # App ID vient du AndroidManifest (meta-data). L'init est asynchrone.
                def _on_init_complete(status):
                    try:
                        print(f"✅ MobileAds init status: {status}")
                        self._mobile_ads_ready = True
                        # CORRECTIF: Initialiser AdsManager maintenant que le SDK est prêt
                        if not self.ads and self.cfg.get("ads_enabled", False):
                            try:
                                from ads_manager import AdsManager
                                self.ads = AdsManager(self.cfg)
                                # Lancer le setup complet (banner + interstitiel)
                                self.ads.setup_ads_after_sdk_ready()
                                print("✅ Pubs configurées après MobileAds.initialize")
                            except Exception as _e:
                                print(f"⚠️ Erreur init AdsManager post-SDK: {_e}")
                    except Exception as _e:
                        print(f"⚠️ Erreur callback MobileAds init: {_e}")
                MobileAds.initialize(self.activity or None, _on_init_complete)
                print("⏳ MobileAds.initialize lancé")
            else:
                print("ℹ️ Mobile Ads non initialisé (pyjnius indisponible ou désactivé)")
        except Exception as e:
            print(f"⚠️ Erreur initialisation MobileAds: {e}")

        # Placeholder consentement (GDPR) - à remplacer par SDK Consent si ciblage UE
        if os.environ.get('EU_USER','0') == '1':
            print("🔐 Consentement UE requis - Implémenter User Messaging Platform SDK")

        # Programme l'application des traductions et police au prochain frame
        try:
            from kivy.clock import Clock  # type: ignore
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
                            from kivy.uix.floatlayout import FloatLayout  # type: ignore
                            from kivy.uix.label import Label  # type: ignore
                            from kivy.graphics import Color, Rectangle  # type: ignore

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
                                from kivy.clock import Clock as _Clock  # type: ignore
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

    # === Notifications / Tirage quotidien ===
    def _today_str(self):
        try:
            import datetime as _dt
            return _dt.date.today().isoformat()
        except Exception:
            return ""

    def _load_last_draw_date(self):
        try:
            p = os.path.join(self.user_data_dir, "last_draw.json")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self._last_draw_date = d.get("date")
        except Exception:
            self._last_draw_date = None

    def _save_last_draw_date(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            p = os.path.join(self.user_data_dir, "last_draw.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"date": self._last_draw_date}, f)
        except Exception as e:
            print(f"⚠️ save last_draw failed: {e}")

    def record_draw_today(self):
        self._last_draw_date = self._today_str()
        self._save_last_draw_date()

    def did_draw_today(self) -> bool:
        return (self._last_draw_date or "") == self._today_str()

    def _seconds_until_today_11(self):
        try:
            import datetime as _dt
            now = _dt.datetime.now()
            target = now.replace(hour=11, minute=0, second=0, microsecond=0)
            if target <= now:
                # déjà passé aujourd'hui → planifier demain 11h
                target = target + _dt.timedelta(days=1)
            return max(1, int((target - now).total_seconds()))
        except Exception:
            return 3600

    def _schedule_daily_draw_reminder(self):
        # Planifie un check à 11h locale (ou demain si 11h passé) tant que l'app tourne.
        # Limitation: si l'app est tuée, aucune notif. Prochaine itération: service Android.
        delay = self._seconds_until_today_11()
        def _fire(_dt):
            try:
                self._maybe_notify_draw_reminder()
            finally:
                # replanifier pour le lendemain
                try:
                    Clock.schedule_once(_fire, 24*3600)
                except Exception:
                    pass
        Clock.schedule_once(_fire, delay)

    def _maybe_notify_draw_reminder(self):
        try:
            today = self._today_str()
            if self._last_draw_date == today:
                return  # déjà fait
            title = self.tr("messages.app_title") if callable(getattr(self, 'tr', None)) else "Ma Carte de Tarot"
            body = self.tr("messages.daily_reminder") if callable(getattr(self, 'tr', None)) else "Votre carte du jour vous attend ✨"
            if plyer_notification:
                try:
                    plyer_notification.notify(title=title, message=body, app_name="Tarot", timeout=10)
                    print("🔔 Notification tirage envoyée")
                except Exception as e:
                    print(f"⚠️ Notification failed: {e}")
        except Exception as e:
            print(f"⚠️ maybe_notify failed: {e}")

    # === Consentement (placeholder UMP) ===
    def _consent_file(self):
        try:
            return os.path.join(self.user_data_dir, "consent.json")
        except Exception:
            return os.path.join(BASE_DIR, "consent.json")

    def _load_consent(self):
        try:
            p = self._consent_file()
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                v = d.get("personalized")
                if isinstance(v, bool):
                    return v
        except Exception:
            pass
        return None

    def _save_consent(self, personalized: bool | None):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            p = self._consent_file()
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"personalized": personalized}, f)
        except Exception as e:
            print(f"⚠️ save consent failed: {e}")

    def set_user_consent(self, personalized: bool):
        # Appeler ceci quand un flux UMP réel sera intégré
        self.consent_personalized = bool(personalized)
        self._save_consent(self.consent_personalized)
        
        # CORRECTIF: Mettre à jour cfg AVANT que MobileAds.init ne crée AdsManager
        try:
            # Dans tous les cas, activer les pubs (personnalisées ou non selon consentement)
            self.cfg["ads_enabled"] = True
            
            if self.consent_personalized:
                print(f"🔐 Consentement accordé → pubs personnalisées activées")
            else:
                print(f"🔐 Consentement refusé → pubs non personnalisées activées (NPA)")
        except Exception as e:
            print(f"⚠️ Update ads config failed after consent change: {e}")
        
        # Ne plus créer AdsManager ici, il sera instancié par le callback MobileAds.initialize
        
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
                try:
                    self._save_premium_status()
                except Exception:
                    pass
                print(f"✨ Premium activé ! (provider={provider})")

                # Journalisation locale + feedback utilisateur
                try:
                    self.append_iap_log(f"SUCCESS {provider} {product_id}")
                    self.show_iap_feedback(self._tr("messages.purchase_success") if callable(getattr(self, '_tr', None)) else "Achat réussi !", success=True)
                except Exception as _el:
                    print(f"⚠️ IAP feedback/log failed: {_el}")

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

                # Ouvrir automatiquement le chat Mme T après achat
                try:
                    from popups import MmeTChatPopup
                    drawn = getattr(self, 'last_drawn_cards', None)
                    price_txt = None
                    try:
                        if self.billing:
                            price_txt = self.billing.get_product_price()
                    except Exception:
                        price_txt = None
                    popup = MmeTChatPopup(language=self.lang, provider=provider, price_text=price_txt, drawn_cards=drawn, tr=self.tr)
                    popup.open()
                except Exception as _e:
                    print(f"ℹ️ Ouverture chat Mme T échouée (facultatif): {_e}")
        except Exception as e:
            print(f"⚠️ Erreur on_purchase_success: {e}")
            self.enable_premium = False
            try:
                self._save_premium_status()
            except Exception:
                pass

    # --- IAP utilitaires: log persistant + popup feedback ---
    def append_iap_log(self, line: str):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            log_path = os.path.join(self.user_data_dir, "iap_debug.log")
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {line}\n")
        except Exception as exc:
            print(f"⚠️ append_iap_log failed: {exc}")

    def show_iap_feedback(self, message: str, success: bool = True):
        # Import retardé pour éviter erreurs de résolution hors environnement Kivy (analyse statique)
        if 'kivy' not in sys.modules:
            print(f"ℹ️ IAP feedback (popup) ignoré: environnement Kivy non initialisé")
            return
        try:
            from kivy.uix.popup import Popup  # type: ignore
            from kivy.uix.label import Label  # type: ignore
            color = [0.2, 0.6, 0.25, 1] if success else [0.85, 0.25, 0.25, 1]
            title = "Achat" if success else "Achat échoué"
            try:
                if hasattr(self, '_tr') and callable(self._tr):
                    title = self._tr("messages.purchase_title") if success else self._tr("messages.purchase_failed")
            except Exception:
                pass
            popup = Popup(title=title,
                          content=Label(text=message, color=color, font_name=getattr(self, 'font_body', 'Body')),
                          size_hint=(0.85, 0.32))
            popup.open()
        except Exception as exc:
            print(f"⚠️ show_iap_feedback failed: {exc}")

    # === Premium persistence ===
    def _premium_file(self):
        try:
            return os.path.join(self.user_data_dir, "premium.json")
        except Exception:
            return os.path.join(BASE_DIR, "premium.json")

    def _load_premium_status(self):
        try:
            p = self._premium_file()
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.enable_premium = bool(d.get("enabled", False))
        except Exception:
            pass

    def _save_premium_status(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            p = self._premium_file()
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"enabled": bool(self.enable_premium)}, f)
        except Exception as e:
            print(f"⚠️ save premium failed: {e}")

# === Loader de signification cartes ===
def get_cards_signification(card_name=None):
    app = App.get_running_app()
    i18n = getattr(app, "i18n", {}) or {}
    sigs = i18n.get("significations", {})
    if card_name:
        return sigs.get(card_name, {})  # aucun I/O, pas de fallback fichier
    return sigs


# === API Notifications quotidiennes: ON/OFF ===
def enable_daily():
    try:
        # Import différé protégé (évite erreurs lint hors Android)
        if 'jnius' not in sys.modules:
            import importlib
            importlib.import_module('jnius')
        from jnius import autoclass  # type: ignore
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ctx = getattr(PythonActivity, 'mActivity', None)
        if ctx is not None:
            AlarmScheduler = autoclass('org.tarot.AlarmScheduler')
            AlarmScheduler.scheduleDaily(ctx)
            print("✅ Daily reminder activé")
    except Exception as e:
        print(f"⚠️ enable_daily failed: {e}")


def disable_daily():
    try:
        if 'jnius' not in sys.modules:
            import importlib
            importlib.import_module('jnius')
        from jnius import autoclass  # type: ignore
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ctx = getattr(PythonActivity, 'mActivity', None)
        if ctx is not None:
            AlarmScheduler = autoclass('org.tarot.AlarmScheduler')
            AlarmScheduler.cancelDaily(ctx)
            print("✅ Daily reminder désactivé")
    except Exception as e:
        print(f"⚠️ disable_daily failed: {e}")


# === Entrée principale ===
if __name__ == "__main__":
    try:
        TarotApp().run()
    except BaseException as e:
        print(f"❌ Erreur fatale application: {e}")
        raise
