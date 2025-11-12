# -*- coding: utf-8 -*-
"""
consent.py — UMP (User Messaging Platform) minimaliste

Objectif: déclencher la collecte/maj du consentement sans bloquer l'UI.
- A appeler tôt au démarrage (on_start), non bloquant
- Si un formulaire est requis, il s'affichera; sinon, noop
- Tous les retours sont ignorés (logs seulement)
"""
from __future__ import annotations

from kivy.utils import platform
from kivy.logger import Logger

try:
    from jnius import PythonJavaClass, autoclass, java_method  # type: ignore
    try:
        from android.runnable import run_on_ui_thread  # type: ignore
    except Exception:  # desktop fallback
        def run_on_ui_thread(func):
            return func
except Exception:  # pragma: no cover - non-Android
    PythonJavaClass = None  # type: ignore
    autoclass = None  # type: ignore

    def java_method(sig):  # type: ignore
        def _d(f):
            return f
        return _d

    def run_on_ui_thread(func):  # type: ignore
        return func


class _OnConsentInfoUpdateSuccess(PythonJavaClass if PythonJavaClass else object):
    __javainterfaces__ = ["com/google/android/ump/ConsentInformation$OnConsentInfoUpdateSuccessListener"]

    def __init__(self, activity):
        if PythonJavaClass:
            super().__init__()
        self.activity = activity

    @java_method("()V")
    def onConsentInfoUpdateSuccess(self):  # pragma: no cover - Android runtime only
        try:
            UserMessagingPlatform = autoclass("com.google.android.ump.UserMessagingPlatform")
            Logger.info("UMP: consent info update success - try loadAndShowConsentFormIfRequired")

            class _OnFormDismissed(PythonJavaClass if PythonJavaClass else object):
                __javainterfaces__ = [
                    "com/google/android/ump/UserMessagingPlatform$OnConsentFormDismissedListener"
                ]

                def __init__(self):
                    if PythonJavaClass:
                        super().__init__()

                @java_method("(Lcom/google/android/ump/FormError;)V")
                def onConsentFormDismissed(self, formError):  # pragma: no cover
                    try:
                        if formError is not None:
                            Logger.warning(
                                "UMP: consent form dismissed with error code=%s msg=%s",
                                formError.getErrorCode(),
                                formError.getMessage(),
                            )
                        else:
                            Logger.info("UMP: consent form dismissed (no error)")
                    except Exception:
                        Logger.info("UMP: form dismissed (no detail)")

            listener = _OnFormDismissed()
            UserMessagingPlatform.loadAndShowConsentFormIfRequired(self.activity, listener)
        except Exception as exc:
            Logger.warning(f"UMP: loadAndShowConsentFormIfRequired failed: {exc}")


class _OnConsentInfoUpdateFailure(PythonJavaClass if PythonJavaClass else object):
    __javainterfaces__ = ["com/google/android/ump/ConsentInformation$OnConsentInfoUpdateFailureListener"]

    def __init__(self):
        if PythonJavaClass:
            super().__init__()

    @java_method("(Lcom/google/android/ump/FormError;)V")
    def onConsentInfoUpdateFailure(self, formError):  # pragma: no cover
        try:
            if formError is not None:
                Logger.warning(
                    "UMP: info update failure code=%s msg=%s",
                    formError.getErrorCode(),
                    formError.getMessage(),
                )
            else:
                Logger.warning("UMP: info update failure (no error)")
        except Exception:
            Logger.warning("UMP: info update failure (no details)")


def request_consent():
    """Déclenche une requête de consentement UMP non bloquante (Android seulement)."""
    if platform != "android" or autoclass is None:
        return

    @run_on_ui_thread
    def _go():
        try:
            Activity = autoclass("org.kivy.android.PythonActivity")
            activity = getattr(Activity, "mActivity", None)
            if activity is None:
                Logger.info("UMP: no Android activity, skip")
                return

            # Builder: new ConsentRequestParameters.Builder().build()
            Builder = autoclass("com.google.android.ump.ConsentRequestParameters$Builder")
            params = Builder().build()

            UserMessagingPlatform = autoclass("com.google.android.ump.UserMessagingPlatform")
            consentInformation = UserMessagingPlatform.getConsentInformation(activity)

            success = _OnConsentInfoUpdateSuccess(activity)
            failure = _OnConsentInfoUpdateFailure()

            consentInformation.requestConsentInfoUpdate(activity, params, success, failure)
            Logger.info("UMP: requestConsentInfoUpdate launched")
        except Exception as exc:
            Logger.warning(f"UMP: request_consent failed: {exc}")

    _go()
