from __future__ import annotations

from kivy.logger import Logger

try:
    from jnius import autoclass
except Exception:  # pragma: no cover - non Android
    autoclass = None


PRODUCT_ID = "premium_features"


def _get_activity():
    if autoclass is None:
        return None
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        return getattr(PythonActivity, "mActivity", None)
    except Exception as e:  # pragma: no cover
        Logger.warning(f"NativeBilling: impossible de récupérer l'activité: {e}")
        return None


def _get_billing_manager():
    if autoclass is None:
        return None
    try:
        return autoclass("org.tarot.billing.BillingManager")
    except Exception as e:  # pragma: no cover
        Logger.warning(f"NativeBilling: BillingManager introuvable: {e}")
        return None


def init():
    """Initialise le Billing natif via BillingManager Kotlin.

    Sans effet hors Android.
    """

    bm = _get_billing_manager()
    activity = _get_activity()
    if not bm or not activity:
        Logger.info("NativeBilling.init: environnement non Android ou BillingManager absent")
        return
    try:
        bm.init(activity)
        Logger.info("NativeBilling.init: appel à BillingManager.init() effectué")
    except Exception as e:  # pragma: no cover
        Logger.warning(f"NativeBilling.init: erreur lors de l'init: {e}")


def is_ready() -> bool:
    bm = _get_billing_manager()
    if not bm:
        return False
    try:
        return bool(bm.isBillingReady())
    except Exception as e:  # pragma: no cover
        Logger.warning(f"NativeBilling.is_ready: erreur: {e}")
        return False


def purchase_premium():
    """Lance l'achat du produit premium principal."""

    bm = _get_billing_manager()
    activity = _get_activity()
    if not bm or not activity:
        Logger.info("NativeBilling.purchase_premium: BillingManager ou activity manquants")
        return
    try:
        bm.purchase(activity, PRODUCT_ID)
        Logger.info("NativeBilling.purchase_premium: appel à BillingManager.purchase() effectué")
    except Exception as e:  # pragma: no cover
        Logger.warning(f"NativeBilling.purchase_premium: erreur: {e}")


def has_premium() -> bool:
    """Retourne True si le produit premium a déjà été acheté."""

    bm = _get_billing_manager()
    if not bm:
        return False
    try:
        return bool(bm.hasPurchased(PRODUCT_ID))
    except Exception as e:  # pragma: no cover
        Logger.warning(f"NativeBilling.has_premium: erreur: {e}")
        return False
