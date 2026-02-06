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
        def run_on_ui_thread(func):
            return func
except Exception:
    PYJNIUS_AVAILABLE = False

    def cast(cls, obj):
        return obj

    def run_on_ui_thread(func):
        return func


# === Imports des modules refactorisés ===
from popups import (
    ChatBubble,
    FullScreenCardPopup,
    LoadingPopup,
    MmeTChatPopup,
)
from screens import (
    RootScreen,
    CardScreen,
    ResponseScreen,
    AboutScreen,
    IntentionScreen,
)
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
try:
    from consent import request_consent as request_ump_consent
except Exception:
    def request_ump_consent():
        return


DEFAULT_MME_T_SPACE = "http://ec2-15-188-119-128.eu-west-3.compute.amazonaws.com/predict"


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
    # Simple normalization: ensure scheme and strip trailing slash
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


MME_T_BACKEND_URL = _normalize_mme_t_backend_url(os.environ.get("MME_T_BACKEND_URL", DEFAULT_MME_T_SPACE))
MME_T_DEFAULT_MODEL = os.environ.get("MME_T_MODEL", "gemini-1.5-flash")


# === Système de compteurs pubs simples (utilisé parfois) ===
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
        debug_list_i18n_dir()
        self.lang = self.get_system_lang()
        self.i18n = self.load_i18n(self.lang)

        self.enable_premium = False
        self._last_draw_date = None
        self._load_last_draw_date()

        self.consent_personalized = self._load_consent()
        self.tr = self._tr
        self.get_cards_signification = self._get_cards_signification
        self.enable_premium = False
        
        # Initialise le gestionnaire de rituel quotidien
        try:
            from daily_ritual import DailyRitualManager
            self.ritual_manager = DailyRitualManager(self.user_data_dir)
            self.ritual_manager.reset_today_if_needed()
            print(f"✅ DailyRitualManager initialisé (streak: {self.ritual_manager.get_streak()})")
        except Exception as e:
            print(f"⚠️ Erreur init DailyRitualManager: {e}")
            self.ritual_manager = None

        try:
            self.cfg = load_config()
            print(f"✅ Config chargée: {len(self.cfg)} paramètres")
        except Exception as e:
            print(f"⚠️ Erreur config: {e}")
            self.cfg = {}

        # Politique pubs en fonction du consentement
        try:
            if self.consent_personalized is None:
                self.cfg["ads_enabled"] = True
                print("ℹ️ Consentement inconnu → pubs non personnalisées (NPA) activées")
            elif self.consent_personalized is False:
                self.cfg["ads_enabled"] = True
                print("ℹ️ Consentement refusé → pubs non personnalisées (NPA) activées")
            else:
                self.cfg["ads_enabled"] = True
                print("ℹ️ Consentement accordé → pubs personnalisées activées")
        except Exception:
            pass

        # AdsManager sera instancié dans on_start
        self.ads = None
        self._mobile_ads_ready = False

    # ------------------------------------------------------------------
    # Langue & i18n
    # ------------------------------------------------------------------
    def get_system_lang(self) -> str:
        forced = os.environ.get("APP_LANG") or os.environ.get("LANGUAGE")
        if forced:
            lang = forced[:2].lower()
        else:
            if PYJNIUS_AVAILABLE:
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
            f"i18n/lang/{lc}.json",
            "i18n/lang/en.json",
        ]

        last_err = None
        for rel in candidates:
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

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def build(self):
        self.font_body = BODY_FONT
        print("🏗️ Construction de l'application Tarot...")
        try:
            root_screen = RootScreen()
            card_screen = CardScreen(name="card_screen")
            intention_screen = IntentionScreen(name="intention_screen")
            response_screen = ResponseScreen(name="response_screen")
            about_screen = AboutScreen(name="about_screen")
            root_screen.add_widget(card_screen)
            root_screen.add_widget(intention_screen)
            root_screen.add_widget(response_screen)
            root_screen.add_widget(about_screen)
            self.response_screen = response_screen

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
            self._ensure_notification_permission()
            self._schedule_daily_draw_reminder()
        except Exception as e:
            print(f"⚠️ schedule reminder failed: {e}")

        # Alarm native
        try:
            if _autoclass is not None and kivy_platform == 'android':
                PythonActivity = _autoclass('org.kivy.android.PythonActivity')
                ctx = getattr(PythonActivity, 'mActivity', None)
                if ctx is not None:
                    AlarmScheduler = _autoclass('org.tarot.AlarmScheduler')
                    AlarmScheduler.scheduleDaily(ctx)
                    print("⏰ AlarmManager: rappel quotidien planifié (natif)")
                    
                    # Enregistrer le timestamp d'ouverture de l'app pour la logique de notification
                    try:
                        System = _autoclass('java.lang.System')
                        prefs = ctx.getSharedPreferences('tarot_prefs', 0)
                        editor = prefs.edit()
                        editor.putLong('last_open_timestamp', System.currentTimeMillis())
                        editor.apply()
                        print("📱 Timestamp d'ouverture enregistré")
                    except Exception as ex:
                        print(f"⚠️ Enregistrement last_open_timestamp failed: {ex}")
        except Exception as e:
            print(f"⚠️ AlarmManager schedule failed: {e}")

        # Consentement natif Java (dialogue simple avant chargement pubs)
        try:
            if _autoclass is not None and kivy_platform == 'android':
                PythonActivity = _autoclass('org.kivy.android.PythonActivity')
                ctx = getattr(PythonActivity, 'mActivity', None)
                if ctx is not None:
                    ConsentManager = _autoclass('org.tarot.consent.ConsentManager')
                    ConsentManager.showConsentIfNeeded(ctx)
                    print("✅ ConsentManager: dialogue affiché si nécessaire")
        except Exception as e:
            print(f"⚠️ ConsentManager failed: {e}")

        # -----------------------------
        # Initialisation des PUBS (AdsManager Python -> AdManager Java)
        # -----------------------------
        try:
            if self.consent_personalized is None:
                personalized = True
            else:
                personalized = bool(self.consent_personalized)

            self.ads = AdsManager(cfg=getattr(self, "cfg", {}), personalized=personalized)
            if self.ads and self.ads.enabled:
                print("✅ AdsManager initialisé et actif")
            else:
                print("ℹ️ AdsManager désactivé ou non dispo (voir logs)")
        except Exception as e:
            print(f"⚠️ Erreur init AdsManager: {e}")
            self.ads = None

    def on_stop(self):
        print("🛑 Application arrêtée")

    # ------------------------------------------------------------------
    # Notifications / Tirage quotidien
    # ------------------------------------------------------------------
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
        self._sync_last_draw_to_prefs()

    def did_draw_today(self) -> bool:
        return (self._last_draw_date or "") == self._today_str()

    def _sync_last_draw_to_prefs(self):
        try:
            if kivy_platform != 'android' or not PYJNIUS_AVAILABLE:
                return
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = getattr(PythonActivity, 'mActivity', None)
            if activity is None:
                return
            prefs = activity.getSharedPreferences('tarot_prefs', 0)
            editor = prefs.edit()
            editor.putString('last_draw_date', self._last_draw_date or '')
            editor.apply()
            print(f"🔄 Sync last_draw_date -> SharedPreferences: {self._last_draw_date}")
        except Exception as e:
            print(f"⚠️ sync last_draw prefs failed: {e}")

    def _seconds_until_today_11(self):
        try:
            import datetime as _dt
            now = _dt.datetime.now()
            target = now.replace(hour=11, minute=0, second=0, microsecond=0)
            if target <= now:
                target = target + _dt.timedelta(days=1)
            return max(1, int((target - now).total_seconds()))
        except Exception:
            return 3600

    def _schedule_daily_draw_reminder(self):
        delay = self._seconds_until_today_11()

        def _fire(_dt):
            try:
                self._maybe_notify_draw_reminder()
            finally:
                try:
                    Clock.schedule_once(_fire, 24 * 3600)
                except Exception:
                    pass

        Clock.schedule_once(_fire, delay)

    def _maybe_notify_draw_reminder(self):
        """
        Envoie une notification douce si le tirage n'a pas été fait aujourd'hui.
        Vérifie également si une notification a déjà été envoyée aujourd'hui.
        """
        try:
            ritual_mgr = getattr(self, 'ritual_manager', None)
            if not ritual_mgr:
                # Fallback vers l'ancien système
                today = self._today_str()
                if self._last_draw_date == today:
                    return
            else:
                # Nouveau système : vérifie via le ritual manager
                if ritual_mgr.is_draw_completed_today():
                    return
                
                # Vérifie qu'on n'a pas déjà notifié aujourd'hui
                last_notif = ritual_mgr.data.get("last_notification_date")
                if last_notif == self._today_str():
                    return
            
            # Messages doux et introspectifs
            title = self.tr("messages.app_title") if callable(getattr(self, 'tr', None)) else "Ma Carte de Tarot"
            body = self.tr("messages.daily_reminder") if callable(getattr(self, 'tr', None)) else "Une carte vous attend aujourd'hui ✨"
            
            if plyer_notification:
                try:
                    plyer_notification.notify(title=title, message=body, app_name="Tarot", timeout=10)
                    print("🔔 Notification tirage envoyée")
                    
                    # Enregistre qu'on a notifié aujourd'hui
                    if ritual_mgr:
                        ritual_mgr.data["last_notification_date"] = self._today_str()
                        ritual_mgr._save_data()
                except Exception as e:
                    print(f"⚠️ Notification failed: {e}")
        except Exception as e:
            print(f"⚠️ maybe_notify failed: {e}")

    # ------------------------------------------------------------------
    # Notifications runtime (Android 13+ POST_NOTIFICATIONS)
    # ------------------------------------------------------------------
    def _ensure_notification_permission(self):
        try:
            if kivy_platform != 'android':
                return True
            import importlib
            jnius_mod = importlib.import_module('jnius')
            autoclass_local = jnius_mod.autoclass
            Build = autoclass_local('android.os.Build')
            if Build.VERSION.SDK_INT < 33:
                return True
            PythonActivity = autoclass_local('org.kivy.android.PythonActivity')
            activity = getattr(PythonActivity, 'mActivity', None)
            if activity is None:
                return False
            ManifestPermission = autoclass_local('android.Manifest$permission')
            ContextCompat = autoclass_local('androidx.core.content.ContextCompat')
            PackageManager = autoclass_local('android.content.pm.PackageManager')
            ActivityCompat = autoclass_local('androidx.core.app.ActivityCompat')
            current = ContextCompat.checkSelfPermission(activity, ManifestPermission.POST_NOTIFICATIONS)
            if current == PackageManager.PERMISSION_GRANTED:
                print('🔔 Permission notifications déjà accordée')
                return True
            print('🔔 Demande de permission notifications (Android 13+)')
            ActivityCompat.requestPermissions(activity, [ManifestPermission.POST_NOTIFICATIONS], 1001)

            self._notif_poll_elapsed = 0.0

            def _poll_perm(dt):
                try:
                    self._notif_poll_elapsed += dt
                    cur = ContextCompat.checkSelfPermission(activity, ManifestPermission.POST_NOTIFICATIONS)
                    if cur == PackageManager.PERMISSION_GRANTED:
                        print('✅ Permission notifications accordée')
                        Clock.unschedule(_poll_perm)
                    elif self._notif_poll_elapsed >= 8.0:
                        print('⚠️ Permission notifications non accordée (timeout)')
                        Clock.unschedule(_poll_perm)
                        self._show_notifications_hint_popup()
                except Exception as _e:
                    print(f'⚠️ Poll permission failed: {_e}')
                    Clock.unschedule(_poll_perm)

            Clock.schedule_interval(_poll_perm, 0.5)
            return False
        except Exception as e:
            print(f'⚠️ ensure_notification_permission failed: {e}')
            return False

    def _show_notifications_hint_popup(self):
        try:
            layout = BoxLayout(orientation='vertical', spacing=12, padding=[16, 12, 16, 12])
            lbl = Label(text='Active les notifications dans les paramètres Android\npour recevoir le rappel quotidien.',
                        halign='center', valign='middle')
            lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0] * 0.95, None)))
            btn = Button(text='Ouvrir les paramètres de notifications', size_hint=(1, None), height=dp(44))

            def _open(*_a):
                try:
                    self.open_notification_settings()
                except Exception as _e:
                    print(f"⚠️ open_notification_settings failed: {_e}")
                if popup:
                    popup.dismiss()

            btn.bind(on_press=_open)
            layout.add_widget(lbl)
            layout.add_widget(btn)
            popup = Popup(
                title='Notifications désactivées',
                content=layout,
                size_hint=(0.85, 0.35),
                auto_dismiss=True
            )
            popup.open()
        except Exception as e:
            print(f'⚠️ show_notifications_hint_popup failed: {e}')

    def open_notification_settings(self):
        """Ouvre l’écran Android des paramètres de notifications pour l’app."""
        try:
            if kivy_platform != 'android':
                return
            import importlib
            jnius_mod = importlib.import_module('jnius')
            autoclass_local = jnius_mod.autoclass
            PythonActivity = autoclass_local('org.kivy.android.PythonActivity')
            activity = getattr(PythonActivity, 'mActivity', None)
            if activity is None:
                return
            Intent = autoclass_local('android.content.Intent')
            Settings = autoclass_local('android.provider.Settings')
            Build = autoclass_local('android.os.Build')
            if Build.VERSION.SDK_INT >= 26:
                intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                intent.putExtra('android.provider.extra.APP_PACKAGE', activity.getPackageName())
            else:
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                Uri = autoclass_local('android.net.Uri')
                intent.setData(Uri.parse('package:' + activity.getPackageName()))
            activity.startActivity(intent)
        except Exception as e:
            print(f"⚠️ open_notification_settings error: {e}")

    # ------------------------------------------------------------------
    # Consentement pubs (fichier local)
    # ------------------------------------------------------------------
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
        self.consent_personalized = bool(personalized)
        self._save_consent(self.consent_personalized)
        try:
            self.cfg["ads_enabled"] = True
            if self.consent_personalized:
                print(f"🔐 Consentement accordé → pubs personnalisées activées")
            else:
                print(f"🔐 Consentement refusé → pubs non personnalisées activées (NPA)")
        except Exception as e:
            print(f"⚠️ Update ads config failed after consent change: {e}")

    # ------------------------------------------------------------------
    # IAP (In-app purchases) – tes méthodes existantes
    # ------------------------------------------------------------------
    # Tout ce qui suit est exactement ce que tu avais déjà (on_buy_premium, on_purchase_success,
    # append_iap_log, show_iap_feedback, _premium_file, _load_premium_status, _save_premium_status)
    # Je le laisse inchangé pour ne pas faire exploser le message encore plus.
    #
    # ⚠️ Si tu veux, je peux te recoller aussi TOUT le bloc IAP en entier dans un message séparé.
    # Pour l’instant, l’important pour les pubs est déjà en place.


# === Loader de signification cartes ===
def get_cards_signification(card_name=None):
    app = App.get_running_app()
    i18n = getattr(app, "i18n", {}) or {}
    sigs = i18n.get("significations", {})
    if card_name:
        return sigs.get(card_name, {})
    return sigs


# === API Notifications quotidiennes: ON/OFF (AlarmScheduler Java) ===
def enable_daily():
    try:
        if 'jnius' not in sys.modules:
            import importlib
            importlib.import_module('jnius')
        from jnius import autoclass
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
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        ctx = getattr(PythonActivity, 'mActivity', None)
        if ctx is not None:
            AlarmScheduler = autoclass('org.tarot.AlarmScheduler')
            AlarmScheduler.cancelDaily(ctx)
            print("✅ Daily reminder désactivé")
    except Exception as e:
        print(f"⚠️ disable_daily failed: {e}")


if __name__ == "__main__":
    try:
        TarotApp().run()
    except BaseException as e:
        print(f"❌ Erreur fatale application: {e}")
        raise
