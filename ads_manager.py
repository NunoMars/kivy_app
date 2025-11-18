# ads_manager.py
# Gestion unifiée des pubs autour du AdManager Java (org.tarot.ads.AdManager)

import os
import json

from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock

PYJNIUS_AVAILABLE = False
try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    PYJNIUS_AVAILABLE = True
except Exception as e:
    Logger.warning(f"ads_manager: pyjnius indisponible: {e}")

    def run_on_ui_thread(func):
        # fallback desktop
        return func


# --------------------------------------------------
# Chargement config (optionnel) pour ne pas casser load_config()
# --------------------------------------------------
def load_config():
    """
    Essaie de charger config.default.json (comme avant).
    Si absent, renvoie un dict avec defaults.
    """
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "config.default.json")
    cfg = {
        "ads_enabled": True,
        "ads_frequency": 3,
    }
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg.update(data or {})
            Logger.info(f"ads_manager.load_config: {len(cfg)} clés")
    except Exception as e:
        Logger.warning(f"ads_manager.load_config: erreur lecture config.default.json: {e}")
    return cfg


def maybe_fetch_remote_config(*args, **kwargs):
    """
    Stub pour compatibilité. Tu peux l’ignorer ou plus tard
    faire un fetch HTTP d’une config distante.
    """
    return None


# --------------------------------------------------
# Helper activité Java
# --------------------------------------------------
def _get_activity():
    if not PYJNIUS_AVAILABLE or platform != "android":
        return None
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = getattr(PythonActivity, "mActivity", None)
        if activity is None:
            activity = PythonActivity.getApplication()
        return activity
    except Exception as e:
        Logger.error(f"ads_manager: impossible de récupérer l'Activity: {e}")
        return None


# --------------------------------------------------
# Classe AdsManager vue par Python (app.ads)
# --------------------------------------------------
class AdsManager:
    """
    Wrapper Python autour de org.tarot.ads.AdManager (Java).
    Fournit:
        - enabled (bool)
        - show_banner()
        - hide_banner()
        - show_interstitial(callback=None)
        - on_card_drawn()  (compteur fréquence)
    De façon à ce que screens.py puisse rester tel quel.
    """

    def __init__(self, cfg=None, personalized=True):
        self.cfg = cfg or {}
        self.enabled = bool(self.cfg.get("ads_enabled", True))
        try:
            self.frequency = int(self.cfg.get("ads_frequency", 3))
        except Exception:
            self.frequency = 3

        self._draw_count = 0

        if platform != "android":
            Logger.info("AdsManager: pas Android → pubs désactivées (mode dev)")
            self.enabled = False
            return

        if not PYJNIUS_AVAILABLE:
            Logger.info("AdsManager: pyjnius manquant → pubs désactivées")
            self.enabled = False
            return

        if not self.enabled:
            Logger.info("AdsManager: ads_enabled = False → pas d'init")
            return

        activity = _get_activity()
        if activity is None:
            Logger.warning("AdsManager: Activity introuvable, pubs non initialisées")
            self.enabled = False
            return

        try:
            self._AdManager = autoclass("org.tarot.ads.AdManager")

            @run_on_ui_thread
            def _init():
                try:
                    # ✅ AdManager.java init() prend uniquement l'Activity (IDs hardcodés)
                    self._AdManager.init(activity)
                    # ⚠️ Le consentement est géré par ConsentManager.java, pas ici
                    # On prépare tout de suite une bannière + un interstitiel
                    self._AdManager.loadBanner(activity)
                    self._AdManager.loadInterstitial(activity)
                    Logger.info(
                        f"AdsManager: initialisé (freq={self.frequency})"
                    )
                except Exception as e:
                    Logger.error(f"AdsManager: init Java échoué: {e}")

            _init()
        except Exception as e:
            Logger.error(f"AdsManager: erreur __init__: {e}")
            self.enabled = False

    # -----------------------------
    # BANNIÈRE
    # -----------------------------
    def show_banner(self):
        if not self.enabled or platform != "android" or not PYJNIUS_AVAILABLE:
            return
        activity = _get_activity()
        if activity is None:
            return

        @run_on_ui_thread
        def _show():
            try:
                self._AdManager.showBanner(activity)
                Logger.info("AdsManager: show_banner() appelé")
            except Exception as e:
                Logger.error(f"AdsManager: show_banner failed: {e}")

        _show()

    def hide_banner(self):
        if not self.enabled or platform != "android" or not PYJNIUS_AVAILABLE:
            return
        activity = _get_activity()
        if activity is None:
            return

        @run_on_ui_thread
        def _hide():
            try:
                self._AdManager.hideBanner(activity)
                Logger.info("AdsManager: hide_banner() appelé")
            except Exception as e:
                Logger.error(f"AdsManager: hide_banner failed: {e}")

        _hide()

    # -----------------------------
    # INTERSTITIEL
    # -----------------------------
    def show_interstitial(self, callback=None):
        """
        Affiche un interstitiel si prêt.
        `callback` est appelé après (ou tout de suite si pas prêt).
        """
        if not self.enabled or platform != "android" or not PYJNIUS_AVAILABLE:
            if callback:
                try:
                    callback()
                except Exception as e:
                    Logger.error(f"AdsManager: callback interstitial (no-ads) failed: {e}")
            return

        activity = _get_activity()
        if activity is None:
            if callback:
                try:
                    callback()
                except Exception as e:
                    Logger.error(f"AdsManager: callback interstitial (no-activity) failed: {e}")
            return

        def _safe_callback(_dt=None):
            if callback:
                try:
                    callback()
                except Exception as e:
                    Logger.error(f"AdsManager: callback interstitial failed: {e}")

        @run_on_ui_thread
        def _show():
            try:
                if self._AdManager.isInterstitialReady():
                    Logger.info("AdsManager: interstitial READY → show + callback différé")
                    self._AdManager.showInterstitial(activity)
                    # on laisse 0.5s avant le callback (approx)
                    Clock.schedule_once(_safe_callback, 0.5)
                else:
                    Logger.info("AdsManager: interstitial NOT READY → callback direct")
                    _safe_callback()
            except Exception as e:
                Logger.error(f"AdsManager: show_interstitial failed: {e}")
                _safe_callback()

        _show()

    # -----------------------------
    # Compteur pour les tirages
    # -----------------------------
    def on_card_drawn(self):
        """
        Appelé depuis CardScreen.perform_card_draw().
        Toutes les `frequency` cartes, on tente une interstitielle.
        """
        if not self.enabled:
            return
        self._draw_count += 1
        Logger.info(f"AdsManager: on_card_drawn #{self._draw_count}")
        if self.frequency > 0 and (self._draw_count % self.frequency) == 0:
            self.show_interstitial(callback=None)
