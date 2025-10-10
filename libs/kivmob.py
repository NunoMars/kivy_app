#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KivMob - Simplified AdMob wrapper for Kivy
Compatible with Google Mobile Ads SDK
"""
from kivy.utils import platform
from kivy.logger import Logger


class TestIds:
    """Test Ad Unit IDs provided by Google"""
    BANNER = "ca-app-pub-3940256099942544/6300978111"
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"
    REWARDED = "ca-app-pub-3940256099942544/5224354917"
    REWARDED_INTERSTITIAL = "ca-app-pub-3940256099942544/5354046379"
    APP_OPEN = "ca-app-pub-3940256099942544/3419835294"


class KivMob:
    """
    Wrapper simplifié pour Google AdMob sur Android
    """
    
    def __init__(self, app_id=""):
        """
        Initialize KivMob
        
        Args:
            app_id (str): AdMob App ID (format: ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX)
        """
        self.app_id = app_id
        self._is_initialized = False
        self._banner_visible = False
        
        if platform == 'android':
            try:
                from jnius import autoclass, cast
                from android.runnable import run_on_ui_thread
                
                self.autoclass = autoclass
                self.cast = cast
                self.run_on_ui_thread = run_on_ui_thread
                
                # Import Android classes
                self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
                self.AdView = autoclass('com.google.android.gms.ads.AdView')
                self.AdRequest = autoclass('com.google.android.gms.ads.AdRequest')
                self.AdSize = autoclass('com.google.android.gms.ads.AdSize')
                self.InterstitialAd = autoclass('com.google.android.gms.ads.interstitial.InterstitialAd')
                self.InterstitialAdLoadCallback = autoclass('com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback')
                self.MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
                self.AdError = autoclass('com.google.android.gms.ads.AdError')
                self.LoadAdError = autoclass('com.google.android.gms.ads.LoadAdError')
                self.FullScreenContentCallback = autoclass('com.google.android.gms.ads.FullScreenContentCallback')
                
                # Get activity and context
                self.activity = self.PythonActivity.mActivity
                self.context = self.activity.getApplicationContext()
                
                # AdMob objects
                self.banner_ad = None
                self.interstitial_ad = None
                
                Logger.info("KivMob: Initialized on Android")
                
            except Exception as e:
                Logger.error(f"KivMob: Failed to initialize Android classes: {e}")
                platform = None  # Fallback to non-Android mode
        
        if platform != 'android':
            Logger.warning("KivMob: Not running on Android, ads disabled")
    
    def is_initialized(self):
        """Check if AdMob is initialized"""
        return self._is_initialized
    
    @property
    def run_on_ui_thread(self):
        """Get or create run_on_ui_thread decorator"""
        if platform == 'android':
            try:
                from android.runnable import run_on_ui_thread
                return run_on_ui_thread
            except:
                pass
        
        # Fallback: no-op decorator
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def initialize(self):
        """Initialize AdMob SDK"""
        if platform != 'android':
            Logger.warning("KivMob: Cannot initialize on non-Android platform")
            return
        
        @self.run_on_ui_thread
        def init():
            try:
                self.MobileAds.initialize(self.context)
                self._is_initialized = True
                Logger.info("KivMob: AdMob SDK initialized")
            except Exception as e:
                Logger.error(f"KivMob: Failed to initialize SDK: {e}")
        
        init()
    
    def new_banner(self, ad_unit_id, size=None):
        """
        Create a banner ad
        
        Args:
            ad_unit_id (str): Banner Ad Unit ID
            size: AdSize (default: BANNER)
        """
        if platform != 'android':
            return
        
        @self.run_on_ui_thread
        def create():
            try:
                if size is None:
                    ad_size = self.AdSize.BANNER
                else:
                    ad_size = size
                
                self.banner_ad = self.AdView(self.context)
                self.banner_ad.setAdSize(ad_size)
                self.banner_ad.setAdUnitId(ad_unit_id)
                
                Logger.info(f"KivMob: Banner created with ID {ad_unit_id}")
            except Exception as e:
                Logger.error(f"KivMob: Failed to create banner: {e}")
        
        create()
    
    def add_banner(self, position="bottom"):
        """
        Add banner to screen
        
        Args:
            position (str): "top" or "bottom"
        """
        if platform != 'android' or not self.banner_ad:
            return
        
        @self.run_on_ui_thread
        def add():
            try:
                from jnius import autoclass
                
                # Get layout params classes
                LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
                LinearLayout = autoclass('android.widget.LinearLayout')
                Gravity = autoclass('android.view.Gravity')
                
                # Create layout params
                params = LayoutParams(
                    LayoutParams.MATCH_PARENT,
                    LayoutParams.WRAP_CONTENT
                )
                
                # Get root layout
                layout = self.activity.findViewById(0x01020002)  # android.R.id.content
                
                if layout:
                    # Set gravity
                    if hasattr(layout, 'setGravity'):
                        if position == "top":
                            layout.setGravity(Gravity.TOP)
                        else:
                            layout.setGravity(Gravity.BOTTOM)
                    
                    # Add banner
                    layout.addView(self.banner_ad, params)
                    
                    # Load ad
                    ad_request = self.AdRequest.Builder().build()
                    self.banner_ad.loadAd(ad_request)
                    
                    self._banner_visible = True
                    Logger.info(f"KivMob: Banner added at {position}")
                else:
                    Logger.error("KivMob: Could not find root layout")
                    
            except Exception as e:
                Logger.error(f"KivMob: Failed to add banner: {e}")
        
        add()
    
    def remove_banner(self):
        """Remove banner from screen"""
        if platform != 'android' or not self.banner_ad or not self._banner_visible:
            return
        
        @self.run_on_ui_thread
        def remove():
            try:
                layout = self.activity.findViewById(0x01020002)
                if layout and self.banner_ad:
                    layout.removeView(self.banner_ad)
                    self._banner_visible = False
                    Logger.info("KivMob: Banner removed")
            except Exception as e:
                Logger.error(f"KivMob: Failed to remove banner: {e}")
        
        remove()
    
    def request_interstitial(self, ad_unit_id):
        """
        Request (load) an interstitial ad
        
        Args:
            ad_unit_id (str): Interstitial Ad Unit ID
        """
        if platform != 'android':
            return
        
        @self.run_on_ui_thread
        def load():
            try:
                ad_request = self.AdRequest.Builder().build()
                
                # Create load callback (simplified - no actual callback implementation)
                callback = self.InterstitialAdLoadCallback()
                
                # Load interstitial
                self.InterstitialAd.load(
                    self.context,
                    ad_unit_id,
                    ad_request,
                    callback
                )
                
                Logger.info(f"KivMob: Interstitial requested with ID {ad_unit_id}")
            except Exception as e:
                Logger.error(f"KivMob: Failed to request interstitial: {e}")
        
        load()
    
    def show_interstitial(self):
        """Show the loaded interstitial ad"""
        if platform != 'android' or not self.interstitial_ad:
            Logger.warning("KivMob: No interstitial loaded")
            return
        
        @self.run_on_ui_thread
        def show():
            try:
                if self.interstitial_ad:
                    self.interstitial_ad.show(self.activity)
                    Logger.info("KivMob: Interstitial shown")
            except Exception as e:
                Logger.error(f"KivMob: Failed to show interstitial: {e}")
        
        show()
    
    def is_interstitial_loaded(self):
        """Check if interstitial is loaded and ready"""
        return self.interstitial_ad is not None
    
    def destroy_interstitial(self):
        """Destroy the interstitial ad"""
        self.interstitial_ad = None
        Logger.info("KivMob: Interstitial destroyed")


__all__ = ['KivMob', 'TestIds']
