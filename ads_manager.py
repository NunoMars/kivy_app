#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdsManager - Gestionnaire de publicités AdMob avec configuration JSON
Permet de changer les IDs de pub sans recompiler l'app
"""
import os
import json
import threading
from kivy.app import App
from kivy.utils import platform
from kivy.logger import Logger

# Import kivmob from libs folder (embedded in app)
import sys
import os
# Add libs to path if not already there
libs_path = os.path.join(os.path.dirname(__file__), 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

try:
    from kivmob import KivMob, TestIds
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

        # Initialize AdMob
        self._initialize_admob()

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
            # Initialize SDK
            self.sdk = KivMob(app_id)
            Logger.info(f"AdMob: Initialized with app_id={app_id}")

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
                self.sdk.request_interstitial()
                Logger.info("AdMob: Interstitial initialized")

            Logger.info("AdMob: Fully initialized ✅")
            
        except Exception as e:
            Logger.error(f"AdMob: Initialization failed: {e}")
            self.enabled = False
            self.sdk = None

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
    
    threading.Thread(target=_work, daemon=False).start()


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
