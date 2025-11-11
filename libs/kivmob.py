#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight AdMob wrapper for Kivy / python-for-android.

The bundled AdsManager depends on the following surface:
- new_banner(ad_unit_id, top=False)
- request_banner()
- show_banner()
- hide_banner()
- new_interstitial(ad_unit_id)
- request_interstitial()
- show_interstitial()
- is_interstitial_loaded()

This module implements that API on top of Google Mobile Ads SDK 23+, using
Pyjnius bridges when running on Android. On desktop the calls silently no-op.
"""
from __future__ import annotations

from typing import Optional

from kivy.logger import Logger
from kivy.utils import platform

try:  # Android-only imports guarded for desktop execution (build, linters)
    from jnius import (  # type: ignore
        PythonJavaClass,
        autoclass,
        java_method,
    )
    from android.runnable import run_on_ui_thread  # type: ignore
except Exception:  # pragma: no cover - import errors on non-Android env
    PythonJavaClass = autoclass = java_method = None  # type: ignore

    def run_on_ui_thread(func):  # type: ignore
        return func


class TestIds:
    """Official Google test identifiers."""

    BANNER = "ca-app-pub-3940256099942544/6300978111"
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"
    REWARDED = "ca-app-pub-3940256099942544/5224354917"
    REWARDED_INTERSTITIAL = "ca-app-pub-3940256099942544/5354046379"
    APP_OPEN = "ca-app-pub-3940256099942544/3419835294"


class KivMob:
    """Minimal bridge around the Google Mobile Ads SDK for Kivy apps."""

    def __init__(self, app_id: str = "", enable_npa: bool = False) -> None:
        self.app_id = app_id
        self._is_initialized = False
        self.banner_ad = None
        self.banner_position = "bottom"
        self._banner_visible = False
        self.interstitial_ad = None
        self._interstitial_unit_id: Optional[str] = None
        self.enable_npa = enable_npa  # Non-Personalized Ads (RGPD)

        if platform != "android" or autoclass is None:
            Logger.warning("KivMob: Not running on Android, ads disabled")
            self.activity = None
            self.context = None
            return

        try:
            self.PythonActivity = autoclass("org.kivy.android.PythonActivity")
            self.AdView = autoclass("com.google.android.gms.ads.AdView")
            self.AdRequest = autoclass("com.google.android.gms.ads.AdRequest")
            self.AdSize = autoclass("com.google.android.gms.ads.AdSize")
            self.InterstitialAd = autoclass(
                "com.google.android.gms.ads.interstitial.InterstitialAd"
            )
            self.InterstitialAdLoadCallback = autoclass(
                "com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback"
            )
            self.MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
            
            # Classes pour NPA
            try:
                self.RequestConfiguration = autoclass(
                    "com.google.android.gms.ads.RequestConfiguration"
                )
                self.Bundle = autoclass("android.os.Bundle")
            except Exception:
                self.RequestConfiguration = None
                self.Bundle = None
                Logger.warning("KivMob: RequestConfiguration not available for NPA")

            self.activity = self.PythonActivity.mActivity
            self.context = self.activity.getApplicationContext()

            Logger.info("KivMob: Android bindings initialised")
        except Exception as exc:  # pragma: no cover - runtime on device only
            Logger.error(f"KivMob: Failed to access Android classes: {exc}")
            self.activity = None
            self.context = None

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def is_initialized(self) -> bool:
        return self._is_initialized

    def initialize(self) -> None:
        if platform != "android" or self.context is None:
            Logger.warning("KivMob: Cannot initialize outside Android")
            return

        @run_on_ui_thread
        def _init() -> None:
            try:
                self.MobileAds.initialize(self.context)
                self._is_initialized = True
                Logger.info("KivMob: MobileAds initialized")
                
                # Configurer NPA globalement si activé
                if self.enable_npa and self.RequestConfiguration:
                    try:
                        config = (
                            self.RequestConfiguration.Builder()
                            .setMaxAdContentRating(
                                self.RequestConfiguration.MAX_AD_CONTENT_RATING_G
                            )
                            .build()
                        )
                        self.MobileAds.setRequestConfiguration(config)
                        Logger.info("KivMob: NPA (Non-Personalized Ads) enabled globally")
                    except Exception as exc:
                        Logger.warning(f"KivMob: Failed to set NPA config: {exc}")
            except Exception as exc:  # pragma: no cover
                Logger.error(f"KivMob: MobileAds initialization failed: {exc}")

        _init()

    def _build_ad_request(self) -> any:
        """Construit une AdRequest avec support NPA (Non-Personalized Ads)."""
        try:
            builder = self.AdRequest.Builder()
            
            # Ajouter npa=1 pour pubs non personnalisées (RGPD)
            if self.enable_npa and self.Bundle:
                try:
                    extras = self.Bundle()
                    extras.putString("npa", "1")
                    # Pour AdMob
                    AdMobAdapter = autoclass("com.google.ads.mediation.admob.AdMobAdapter")
                    builder.addNetworkExtrasBundle(AdMobAdapter, extras)
                    Logger.info("KivMob: NPA parameter added to ad request")
                except Exception as exc:
                    Logger.warning(f"KivMob: Failed to add NPA bundle: {exc}")
            
            return builder.build()
        except Exception as exc:
            Logger.error(f"KivMob: Failed to build ad request: {exc}")
            # Fallback: requête simple sans NPA
            return self.AdRequest.Builder().build()

    # ------------------------------------------------------------------
    # Banner API
    # ------------------------------------------------------------------
    def new_banner(self, ad_unit_id: str, top: bool = False) -> None:
        if platform != "android" or self.context is None:
            return

        @run_on_ui_thread
        def _create() -> None:
            try:
                self.banner_position = "top" if top else "bottom"
                self.banner_ad = self.AdView(self.context)
                self.banner_ad.setAdSize(self.AdSize.BANNER)
                self.banner_ad.setAdUnitId(ad_unit_id)
                Logger.info(
                    "KivMob: Banner created (%s, position=%s)",
                    ad_unit_id,
                    self.banner_position,
                )
            except Exception as exc:
                Logger.error(f"KivMob: Failed to create banner: {exc}")
                self.banner_ad = None

        _create()

    def request_banner(self) -> None:
        if platform != "android" or not self.banner_ad:
            return

        @run_on_ui_thread
        def _load() -> None:
            try:
                ad_request = self._build_ad_request()
                self.banner_ad.loadAd(ad_request)
                Logger.info("KivMob: Banner load requested")
            except Exception as exc:
                Logger.error(f"KivMob: Failed to request banner: {exc}")

        _load()

    def show_banner(self) -> None:
        if platform != "android" or not self.banner_ad:
            return

        @run_on_ui_thread
        def _show() -> None:
            try:
                FrameLayout = autoclass("android.widget.FrameLayout")
                Gravity = autoclass("android.view.Gravity")

                layout = self.activity.findViewById(0x01020002)  # android.R.id.content
                if not layout:
                    Logger.error("KivMob: Root layout not found")
                    return

                params = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    Gravity.TOP if self.banner_position == "top" else Gravity.BOTTOM,
                )

                parent = self.banner_ad.getParent()
                if parent:
                    parent.removeView(self.banner_ad)

                layout.addView(self.banner_ad, params)
                self._banner_visible = True
                Logger.info("KivMob: Banner attached to UI")
            except Exception as exc:
                Logger.error(f"KivMob: Failed to show banner: {exc}")

        _show()

    def hide_banner(self) -> None:
        if platform != "android" or not self.banner_ad or not self._banner_visible:
            return

        @run_on_ui_thread
        def _hide() -> None:
            try:
                layout = self.activity.findViewById(0x01020002)
                if layout:
                    layout.removeView(self.banner_ad)
                    self._banner_visible = False
                    Logger.info("KivMob: Banner removed")
            except Exception as exc:
                Logger.error(f"KivMob: Failed to hide banner: {exc}")

        _hide()

    # ------------------------------------------------------------------
    # Interstitial API
    # ------------------------------------------------------------------
    class _InterstitialCallback(PythonJavaClass if PythonJavaClass else object):
        __javaclass__ = "com/google/android/gms/ads/interstitial/InterstitialAdLoadCallback"

        def __init__(self, outer: "KivMob") -> None:
            if PythonJavaClass:
                super().__init__()
            self.outer = outer

        @java_method("(Lcom/google/android/gms/ads/interstitial/InterstitialAd;)V")
        def onAdLoaded(self, ad) -> None:  # pragma: no cover - Java call
            self.outer.interstitial_ad = ad
            Logger.info("KivMob: Interstitial loaded")

        @java_method("(Lcom/google/android/gms/ads/LoadAdError;)V")
        def onAdFailedToLoad(self, error) -> None:  # pragma: no cover - Java call
            self.outer.interstitial_ad = None
            try:
                Logger.warning(
                    "KivMob: Interstitial failed (code=%s): %s",
                    error.getCode(),
                    error.getMessage(),
                )
            except Exception:
                Logger.warning("KivMob: Interstitial failed to load")

    def new_interstitial(self, ad_unit_id: str) -> None:
        if platform != "android" or self.context is None:
            return
        self._interstitial_unit_id = ad_unit_id
        self.request_interstitial()

    def request_interstitial(self) -> None:
        if (
            platform != "android"
            or self.context is None
            or not self._interstitial_unit_id
        ):
            return

        @run_on_ui_thread
        def _load() -> None:
            try:
                ad_request = self._build_ad_request()
                callback = KivMob._InterstitialCallback(self)
                self.InterstitialAd.load(
                    self.context,
                    self._interstitial_unit_id,
                    ad_request,
                    callback,
                )
                Logger.info(
                    "KivMob: Requesting interstitial (%s)",
                    self._interstitial_unit_id,
                )
            except Exception as exc:
                Logger.error(f"KivMob: Failed to request interstitial: {exc}")

        _load()

    def is_interstitial_loaded(self) -> bool:
        return self.interstitial_ad is not None

    def show_interstitial(self) -> None:
        if platform != "android":
            Logger.warning("KivMob: Cannot show interstitial outside Android")
            return
        if not self.interstitial_ad:
            Logger.warning("KivMob: No interstitial ready")
            return

        @run_on_ui_thread
        def _show() -> None:
            try:
                self.interstitial_ad.show(self.activity)
                Logger.info("KivMob: Interstitial displayed")
                self.interstitial_ad = None
                # Preload the next one immediately for smoother UX
                self.request_interstitial()
            except Exception as exc:
                Logger.error(f"KivMob: Failed to show interstitial: {exc}")

        _show()

    def destroy_interstitial(self) -> None:
        self.interstitial_ad = None
        Logger.info("KivMob: Interstitial destroyed")


__all__ = ["KivMob", "TestIds"]
