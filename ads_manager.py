#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdsManager - Gestionnaire de publicités AdMob avec configuration JSON
Permet de changer les IDs de pub sans recompiler l'app
"""
import os
import json
import threading
from kivy.app import App  # type: ignore
from kivy.utils import platform  # type: ignore
from kivy.logger import Logger  # type: ignore

# Import kivmob from libs folder (embedded in app)
import sys
import os
# Add libs to path if not already there
libs_path = os.path.join(os.path.dirname(__file__), 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

try:
    from kivmob import KivMob, TestIds  # type: ignore
except Exception as e:
    Logger.warning(f"AdMob: kivmob not available: {e}")
    KivMob = None
    TestIds = None

try:
    import requests
except Exception:
    requests = None


def load_config() -> dict:
    """
    Charge la configuration avec priorité:
    1. user_data_dir/config.json (modifiable sans rebuild)
    2. config.default.json (embarqué dans l'app)
    
    Returns:
        dict: Configuration fusionnée
    """
    app = App.get_running_app()
    cfg = {}
    
    # 1) Configuration utilisateur (prioritaire)
    try:
        # Vérifier que l'app est lancée avant d'accéder à user_data_dir
        if app is not None:
            user_config_path = os.path.join(app.user_data_dir, "config.json")
            if os.path.exists(user_config_path):
                with open(user_config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                Logger.info(f"AdMob: Loaded user config from {user_config_path}")
        else:
            Logger.info("AdMob: App not yet running, skipping user config")
    except Exception as e:
        Logger.warning(f"AdMob: Failed to read user config: {e}")

    # 2) Configuration par défaut (fallback)
    try:
        here = os.path.dirname(__file__)
        default_config_path = os.path.join(here, "config.default.json")
        with open(default_config_path, "r", encoding="utf-8") as f:
            base = json.load(f)
        base.update(cfg)  # Merge: user config override defaults
        cfg = base
        Logger.info("AdMob: Loaded default config")
    except Exception as e:
        Logger.error(f"AdMob: Failed to read default config: {e}")
        # Fallback minimal si aucune config
        cfg = {
            "ads_enabled": False,
            "ads_test_mode": True,
            "ads_frequency": 3
        }

    return cfg


class AdsManager:
    """
    Gestionnaire de publicités AdMob
    Supporte bannières et interstitiels avec configuration JSON
    """
    
    def __init__(self, cfg: dict):
        """
        Initialize AdMob with configuration
        
        Args:
            cfg (dict): Configuration dictionary from load_config()
        """
        self.cfg = cfg
        self.sdk = None
        self.enabled = bool(cfg.get("ads_enabled", False))
        self.test_mode = bool(cfg.get("ads_test_mode", True))
        self.banner_enabled = bool(cfg.get("banner_enabled", True))
        self.interstitial_enabled = bool(cfg.get("interstitial_enabled", True))
        
        # Compteur pour interstitiels
        self._draw_count = 0
        self._ads_frequency = int(cfg.get("ads_frequency", 3))
        
        # CORRECTIF: garder référence forte sur callbacks Java pour éviter GC
        self._banner_load_callback = None
        self._interstitial_load_callback = None
        
        if not self.enabled:
            Logger.info("AdMob: Disabled by config")
            return
            
        if not KivMob:
            Logger.warning("AdMob: KivMob not available, ads disabled")
            self.enabled = False
            return
        
        # Android only
        if platform != "android":
            Logger.info(f"AdMob: Not on Android (platform={platform}), ads disabled")
            self.enabled = False
            return

        # Initialize AdMob — délégué après MobileAds.initialize via wait_mobile_ads_ready()
        # Pour l'instant, créer seulement l'instance KivMob
        try:
            app_id = self.cfg.get("admob_app_id")
            if self.test_mode and TestIds:
                app_id = getattr(TestIds, "APP", app_id or "")
            self.sdk = KivMob(app_id)
            Logger.info(f"AdMob: KivMob instance created (app_id={app_id})")
        except Exception as e:
            Logger.error(f"AdMob: Failed to create KivMob instance: {e}")
            self.enabled = False
            return
        
        # Optionnel: initialiser les SDK de médiation si des clés sont fournies
        try:
            self._initialize_mediation_sdks()
        except Exception as e:
            Logger.warning(f"Ads: Mediation SDK init skipped/failed: {e}")


    def setup_ads_after_sdk_ready(self):
        """
        Appelée APRÈS que MobileAds.initialize() soit terminé.
        Crée et charge les bannières + interstitiels de manière sûre.
        """
        if not self.sdk or not self.enabled:
            Logger.warning("AdMob: SDK not ready or ads disabled")
            return
        
        try:
            self._initialize_admob()
            Logger.info("AdMob: Ads setup completed after SDK initialization ✅")
        except Exception as e:
            Logger.error(f"AdMob: Failed to setup ads after SDK ready: {e}")

    def _initialize_admob(self):
        """Initialize AdMob SDK with IDs from config"""
        app_id = self.cfg.get("admob_app_id")
        banner_id = self.cfg.get("admob_banner_id")
        inter_id = self.cfg.get("admob_inter_id")

        # Use test IDs if in test mode
        if self.test_mode:
            Logger.info("AdMob: Using TEST IDs")
            app_id = getattr(TestIds, "APP", app_id or "")
            banner_id = getattr(TestIds, "BANNER", banner_id or "")
            inter_id = getattr(TestIds, "INTERSTITIAL", inter_id or "")
        else:
            Logger.info("AdMob: Using PRODUCTION IDs")

        try:
            # SDK instance déjà créée dans __init__, juste initialiser ici
            if not self.sdk._is_initialized:
                self.sdk.initialize()

            # Setup banner
            if self.banner_enabled and banner_id:
                banner_top = self.cfg.get("banner_position", "bottom") == "top"
                self.sdk.new_banner(banner_id, top=banner_top)
                self.sdk.request_banner()
                self.sdk.show_banner()
                Logger.info(f"AdMob: Banner initialized (position={'top' if banner_top else 'bottom'})")

            # Setup interstitial
            if self.interstitial_enabled and inter_id:
                self.sdk.new_interstitial(inter_id)
                Logger.info("AdMob: Interstitial initialized")

            Logger.info("AdMob: Fully initialized ✅")
            
        except Exception as e:
            Logger.error(f"AdMob: Initialization failed: {e}")
            self.enabled = False


    def _initialize_mediation_sdks(self):
        """Optionally initialize mediation SDKs (ironSource/AppLovin) when running on Android.
        These inits are not strictly required with AdMob mediation adapters, but recommended.
        """
        if platform != "android":
            return
        try:
            from jnius import autoclass  # type: ignore
        except Exception:
            Logger.info("Ads: pyjnius not available; skip mediation init")
            return

        # Acquire Activity
        activity = None
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = getattr(PythonActivity, "mActivity", None)
        except Exception:
            pass
        if activity is None:
            Logger.info("Ads: No Android activity; skip mediation init")
            return

        # ironSource (LevelPlay)
        try:
            app_key = self.cfg.get("ironsource_app_key") or os.environ.get("IRONSOURCE_APP_KEY") or "243005255"
            IronSource = autoclass("com.ironsource.mediationsdk.IronSource")
            IronSource.init(activity, app_key)
            Logger.info("Ads: ironSource initialized")
            # Optionally request user consent if known
            try:
                consent = os.environ.get("IRONSOURCE_CONSENT")
                if consent in ("1", "true", "True"):
                    IronSource.setConsent(True)
                elif consent in ("0", "false", "False"):
                    IronSource.setConsent(False)
            except Exception:
                pass
        except Exception as e:
            Logger.info(f"Ads: ironSource init skipped: {e}")

        # AppLovin SDK (optional)
        try:
            sdk_key = self.cfg.get("applovin_sdk_key") or os.environ.get("APPLOVIN_SDK_KEY")
            if sdk_key:
                AppLovinSdk = autoclass("com.applovin.sdk.AppLovinSdk")
                sdk = AppLovinSdk.getInstance(activity)
                if sdk:
                    sdk.initializeSdk(activity, None)
                    Logger.info("Ads: AppLovin SDK initialized")
        except Exception as e:
            Logger.info(f"Ads: AppLovin init skipped: {e}")

    def on_card_drawn(self):
        """
        Call this method every time a card is drawn
        Will show interstitial based on frequency setting
        """
        if not self.enabled or not self.interstitial_enabled:
            return
            
        self._draw_count += 1
        Logger.info(f"AdMob: Card drawn #{self._draw_count}")
        
        if self._draw_count % self._ads_frequency == 0:
            self.show_interstitial()

    def show_interstitial(self):
        """Show interstitial ad if loaded"""
        if not self.sdk or not self.interstitial_enabled:
            return
            
        try:
            if self.sdk.is_interstitial_loaded():
                Logger.info("AdMob: Showing interstitial")
                self.sdk.show_interstitial()
                # Request next one
                self.sdk.request_interstitial()
            else:
                Logger.warning("AdMob: Interstitial not loaded yet")
                # Try to request again
                self.sdk.request_interstitial()
        except Exception as e:
            Logger.error(f"AdMob: Failed to show interstitial: {e}")

    def show_banner(self):
        """Show banner if enabled"""
        if self.sdk and self.banner_enabled:
            try:
                self.sdk.show_banner()
                Logger.info("AdMob: Banner shown")
            except Exception as e:
                Logger.error(f"AdMob: Failed to show banner: {e}")

    def hide_banner(self):
        """Hide banner"""
        if self.sdk and self.banner_enabled:
            try:
                self.sdk.hide_banner()
                Logger.info("AdMob: Banner hidden")
            except Exception as e:
                Logger.error(f"AdMob: Failed to hide banner: {e}")


def maybe_fetch_remote_config(cfg: dict):
    """
    Optional: fetch remote JSON and save to user_data_dir/config.json
    Then the app can be restarted to apply new config
    
    Args:
        cfg (dict): Current configuration (with potential remote_config_url)
    """
    if not requests:
        Logger.warning("AdMob: requests module not available, remote config disabled")
        return
        
    url = (cfg or {}).get("remote_config_url") or ""
    if not url:
        Logger.info("AdMob: No remote_config_url configured")
        return
        
    app = App.get_running_app()
    
    def _work():
        try:
            Logger.info(f"AdMob: Fetching remote config from {url}")
            r = requests.get(url, timeout=6)
            r.raise_for_status()
            data = r.json()
            
            # Save to user_data_dir
            os.makedirs(app.user_data_dir, exist_ok=True)
            out_path = os.path.join(app.user_data_dir, "config.json")
            
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            Logger.info(f"AdMob: Remote config saved to {out_path}")
            Logger.info("AdMob: Restart app to apply new configuration")
            
            # TODO: Optionally show a Kivy Popup:
            # "Configuration mise à jour ! Redémarrez l'app pour appliquer les changements."
            
        except Exception as e:
            Logger.error(f"AdMob: Remote config fetch failed: {e}")
    
    # Android 14+: éviter les threads bloquants et threads non-daemon qui empêchent la fermeture
    threading.Thread(target=_work, daemon=True).start()

class ConsentStatus:
    UNKNOWN = 0
    REQUIRED = 1
    NOT_REQUIRED = 2

def maybe_request_consent():
    """
    Placeholder consentement UE (User Messaging Platform SDK).
    Pour conformité 2025, intégrer le SDK UMP côté Java/Kotlin et l'exposer via pyjnius.
    Ici, on ne bloque pas le thread UI et on log seulement.
    """
    try:
        from kivy.logger import Logger  # type: ignore
        if os.environ.get('EU_USER','0') == '1':
            Logger.info("Consent: EU user flagged -> implement UMP SDK if needed")
        else:
            Logger.info("Consent: Not an EU user (env EU_USER != 1)")
    except Exception:
        pass


# Exemple d'utilisation dans main.py:
"""
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config

class TarotApp(App):
    def build(self):
        # Charger config
        self.cfg = load_config()
        
        # Optionnel: récupérer config à distance
        maybe_fetch_remote_config(self.cfg)
        
        # Initialiser AdMob
        self.ads = AdsManager(self.cfg)
        
        # ... reste du code ...
        return root_widget
    
    def on_card_drawn(self):
        # Appeler à chaque tirage de carte
        self.ads.on_card_drawn()
"""
