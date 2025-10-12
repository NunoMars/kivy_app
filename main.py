__version__ = "0.01"

import os
import random
import locale
import uuid
import threading
import re

import requests
from translations import MESSAGES

try:
    from gradio_client import Client as GradioClient
    GRADIO_CLIENT_AVAILABLE = True
except ImportError:
    GRADIO_CLIENT_AVAILABLE = False
    print("⚠️ gradio_client non disponible, utilisation de requests REST")


DEFAULT_MME_T_SPACE = "https://huggingface.co/spaces/Loupy222/mme_t"


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
                owner_slug = re.sub(r"[^a-z0-9-]", "-", owner.lower())
                space_slug = re.sub(r"[^a-z0-9-]", "-", space.lower())
                owner_slug = owner_slug.strip("-") or owner.lower()
                space_slug = space_slug.strip("-") or space.lower()
                return f"https://{owner_slug}-{space_slug}.hf.space"
    return url

# Détecter la langue du système
def get_system_language():
    try:
        # Prend la variable d'environnement LANG si présente
        lang = os.environ.get("LANG", "")
        if lang.startswith("pt"):
            return "pt"
        elif lang.startswith("en"):
            return "en"
        else:
            return "fr"
    except:
        return "fr"

# Langue actuelle de l'application
CURRENT_LANG = get_system_language()
print(f"🌍 Langue détectée: {CURRENT_LANG}")

# Fonction helper pour obtenir les traductions
def tr(key, **kwargs):
    txt = MESSAGES[CURRENT_LANG].get(key, MESSAGES["fr"][key])
    if kwargs:
        try:
            return txt.format(**kwargs)
        except Exception:
            return txt
    return txt

# Variables globales MME_T (initialisées AVANT Kivy pour éviter les crashes Android)
MME_T_BACKEND_URL = _normalize_mme_t_backend_url(
    os.environ.get("MME_T_BACKEND_URL", DEFAULT_MME_T_SPACE)
)
MME_T_DEFAULT_MODEL = os.environ.get("MME_T_MODEL", "gemini-1.5-flash")

# Configuration Kivy
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '600')
Config.set('kivy', 'log_level', 'warning')
Config.set('kivy', 'show_cursor', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock, mainthread
from kivy.animation import Animation
from kivy.metrics import dp
import random
import os

from kivy.utils import platform

PYJNIUS_AVAILABLE = True
try:
    from jnius import (
        autoclass,
        cast,
        JavaException,
        PythonJavaClass,
        java_method,
    )
except Exception as jnius_exc:  # pragma: no cover - desktop fallback
    PYJNIUS_AVAILABLE = False
    autoclass = None
    cast = lambda cls, obj: obj  # type: ignore
    JavaException = Exception

    class PythonJavaClass(object):
        """Fallback stub when PyJNIus is unavailable."""

    def java_method(signature):  # type: ignore
        def decorator(func):
            return func

        return decorator

# Variables MME_T déjà initialisées plus haut (lignes ~68-72)

SIGNIFICATION_KEY_MAP = {
    "fr": {
        "keywords": {"upright": "a l'endroit", "reversed": "a l'envers"},
        "detail": {
            "upright": "signification a l'endroit",
            "reversed": "signification a l'envers",
        },
    },
    "en": {
        "keywords": {"upright": "upright", "reversed": "reversed"},
        "detail": {
            "upright": "signification upright",
            "reversed": "signification reversed",
        },
    },
    "pt": {
        "keywords": {"upright": "direita", "reversed": "invertida"},
        "detail": {
            "upright": "signification direita",
            "reversed": "signification invertida",
        },
    },
}

# Import des significations selon la langue détectée
# Import du gestionnaire de publicités AdMob
from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
try:
    if CURRENT_LANG == "en":
        from signification_en import get_cards_signification  # Maintenant correct !
        print("✓ Significations EN importées")
    elif CURRENT_LANG == "pt": 
        from signification_pt import get_cards_signification
        print("✓ Significations PT importées")
    else:
        from signification_fr import get_cards_signification
        print("✓ Significations FR importées")
except Exception as e:
    print(f"✗ Erreur significations: {e}")
    def get_cards_signification():
        return {"Le Mat": {"droite": "Nouveau départ", "a l'envers": "Imprudence"}}

try:
    from card_image_mapping import get_card_image_path
    print("✓ Mapping images importé")
except Exception as e:
    print(f"✗ Erreur mapping: {e}")
    def get_card_image_path(card, state):
        base_path = "tarot_img/MajorArcanaCards"
        if state == "a l'envers":
            return os.path.join(base_path, f"{card} a l'envers.jpg")
        return os.path.join(base_path, f"{card}.jpg")


try:
    from card_name_mapping import get_card_name_for_lang
    print("✓ Card name mapping importé")
except Exception as e:
    print(f"✗ Erreur card name mapping: {e}")
    def get_card_name_for_lang(french_name, target_lang):
        return french_name


# Système de compteur pour les publicités
READING_COUNT = 0
ADS_FREQUENCY = 3  # Afficher une pub toutes les 3 lectures

def should_show_ad():
    """Détermine s'il faut afficher une publicité"""
    global READING_COUNT
    READING_COUNT += 1
    return READING_COUNT % ADS_FREQUENCY == 0

def reset_reading_count():
    """Remet le compteur à zéro (pour les tests)"""
    global READING_COUNT
    READING_COUNT = 0


class GooglePurchasesUpdatedListener(PythonJavaClass):  # pragma: no cover - Android only
    """Gestion des retours d'achats Google Play Billing."""

    __javacontext__ = "app"
    __javainterfaces__ = [
        "com/android/billingclient/api/PurchasesUpdatedListener",
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method(
        "(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V"
    )
    def onPurchasesUpdated(self, billing_result, purchases):
        try:
            response_code = billing_result.getResponseCode()
            if (
                self.manager.google_client_class
                and response_code
                == self.manager.google_client_class.BillingResponseCode.OK
                and purchases
                and purchases.size() > 0
            ):
                purchase = purchases.get(0)
                print(
                    f"✅ Achat Google confirmé pour {purchase.getSkus()}"
                )
                self.manager._notify_success("google")
            elif (
                self.manager.google_client_class
                and response_code
                == self.manager.google_client_class.BillingResponseCode.USER_CANCELED
            ):
                print("ℹ️ Achat Google annulé par l'utilisateur")
                self.manager._notify_error(
                    "Achat annulé", provider="google", warn_only=True
                )
            else:
                print(
                    f"⚠️ Achat Google échoué - code: {response_code}"
                )
                self.manager._notify_error(
                    f"Erreur achat (code {response_code})",
                    provider="google",
                )
        except Exception as exc:  # pragma: no cover - Android only
            print(f"✗ Exception traitement achat Google: {exc}")
            self.manager._notify_error(
                "Erreur inattendue lors de l'achat",
                provider="google",
            )


class GoogleBillingStateListener(PythonJavaClass):  # pragma: no cover
    """Réception de l'état de connexion au service de facturation Google."""

    __javacontext__ = "app"
    __javainterfaces__ = [
        "com/android/billingclient/api/BillingClientStateListener",
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/android/billingclient/api/BillingResult;)V")
    def onBillingSetupFinished(self, billing_result):
        try:
            response_code = billing_result.getResponseCode()
            if (
                self.manager.google_client_class
                and response_code
                == self.manager.google_client_class.BillingResponseCode.OK
            ):
                print("✅ Connexion Billing Google établie")
                self.manager._on_google_billing_ready()
            else:
                print(
                    f"⚠️ Connexion Billing Google interrompue (code {response_code})"
                )
                self.manager._notify_error(
                    "Service de paiement indisponible",
                    provider="google",
                )
        except Exception as exc:
            print(f"✗ Exception connexion Billing Google: {exc}")
            self.manager._notify_error(
                "Erreur Billing Google", provider="google"
            )

    @java_method("()V")
    def onBillingServiceDisconnected(self):
        print("⚠️ Service Billing Google déconnecté")
        self.manager.billing_ready = False
        self.manager._dispatch_state_change()


class GoogleSkuDetailsListener(PythonJavaClass):  # pragma: no cover
    """Réception asynchrone des informations produit (Google)."""

    __javacontext__ = "app"
    __javainterfaces__ = [
        "com/android/billingclient/api/SkuDetailsResponseListener",
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method(
        "(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V"
    )
    def onSkuDetailsResponse(self, billing_result, sku_details_list):
        try:
            response_code = billing_result.getResponseCode()
            if (
                self.manager.google_client_class
                and response_code
                == self.manager.google_client_class.BillingResponseCode.OK
                and sku_details_list
                and sku_details_list.size() > 0
            ):
                details = sku_details_list.get(0)
                price_text = details.getPrice()
                self.manager.google_sku_details = details
                if price_text:
                    self.manager.display_price = price_text
                print(
                    "✅ Détails produit Google récupérés:"
                    f" {self.manager.display_price}"
                )
                self.manager._dispatch_state_change()
            else:
                print(
                    "⚠️ Détails produit Google indisponibles (code"
                    f" {response_code})"
                )
                self.manager._notify_error(
                    "Produit indisponible sur Play Store",
                    provider="google",
                )
        except Exception as exc:
            print(f"✗ Exception lecture SKU Google: {exc}")
            self.manager._notify_error(
                "Erreur produit sur Play Store", provider="google"
            )


class LaunchBillingRunnable(PythonJavaClass):  # pragma: no cover
    """Exécute le lancement du flux d'achat sur le thread UI Android."""

    __javacontext__ = "app"
    __javainterfaces__ = ["java/lang/Runnable"]

    def __init__(self, manager, billing_params):
        super().__init__()
        self.manager = manager
        self.billing_params = billing_params

    @java_method("()V")
    def run(self):
        try:
            if self.manager.google_billing_client and self.manager.activity:
                self.manager.google_billing_client.launchBillingFlow(
                    self.manager.activity, self.billing_params
                )
        except Exception as exc:
            print(f"✗ Exception lancement Billing Flow: {exc}")
            self.manager._notify_error(
                "Impossible de lancer l'achat", provider="google"
            )


class AmazonPurchasingListener(PythonJavaClass):  # pragma: no cover
    """Gestionnaire des callbacks Amazon IAP."""

    __javacontext__ = "app"
    __javainterfaces__ = ["com/amazon/device/iap/PurchasingListener"]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.request_status_class = None
        try:
            self.request_status_class = autoclass(
                "com.amazon.device.iap.model.PurchaseResponse$RequestStatus"
            )
        except Exception as exc:
            print(f"⚠️ Impossible de charger RequestStatus Amazon: {exc}")

    @java_method("(Lcom/amazon/device/iap/model/PurchaseResponse;)V")
    def onPurchaseResponse(self, response):
        try:
            status = response.getRequestStatus()
            if (
                self.request_status_class
                and status == self.request_status_class.SUCCESSFUL
            ):
                receipt = response.getReceipt()
                sku = receipt.getSku() if receipt else "?"
                print(f"✅ Achat Amazon confirmé pour {sku}")
                self.manager._notify_success("amazon")
            elif (
                self.request_status_class
                and status == self.request_status_class.ALREADY_PURCHASED
            ):
                print("ℹ️ Produit Amazon déjà acheté")
                self.manager._notify_success("amazon")
            elif (
                self.request_status_class
                and status == self.request_status_class.INVALID_SKU
            ):
                self.manager._notify_error(
                    "Produit Amazon invalide",
                    provider="amazon",
                )
            else:
                print(f"⚠️ Achat Amazon échoué ({status})")
                self.manager._notify_error(
                    "Achat Amazon échoué",
                    provider="amazon",
                )
        except Exception as exc:
            print(f"✗ Exception achat Amazon: {exc}")
            self.manager._notify_error(
                "Erreur Amazon IAP", provider="amazon"
            )

    @java_method("(Lcom/amazon/device/iap/model/ProductDataResponse;)V")
    def onProductDataResponse(self, response):
        print("ℹ️ Réponse ProductData Amazon reçue")

    @java_method("(Lcom/amazon/device/iap/model/PurchaseUpdatesResponse;)V")
    def onPurchaseUpdatesResponse(self, response):
        print("ℹ️ Réponse PurchaseUpdates Amazon reçue")

    @java_method("(Lcom/amazon/device/iap/model/UserDataResponse;)V")
    def onUserDataResponse(self, response):
        print("ℹ️ Réponse UserData Amazon reçue")


class InAppPurchaseManager:
    """Gestion unifiée des achats intégrés (Google / Amazon)."""

    GOOGLE_PRODUCT_ID = "chat_luna_premium"
    AMAZON_PRODUCT_ID = "chat_luna_premium"

    def __init__(self, on_success=None, on_error=None):
        self.on_success = on_success
        self.on_error = on_error
        self.activity = None
        self.mode = "disabled"  # "google" | "amazon" | "simulation" | "disabled"
        self.billing_ready = False
        self.display_price = "2,99€"
        self.google_billing_client = None
        self.google_client_class = None
        self.google_sku_details = None
        self.amazon_ready = False
        self.state_observers = []

        if platform == "android" and PYJNIUS_AVAILABLE:
            try:
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                self.activity = PythonActivity.mActivity
                package_name = self.activity.getPackageName()
                print(f"📦 Package Android détecté: {package_name}")
                if package_name and "amazon" in package_name.lower():
                    self.mode = "amazon"
                else:
                    self.mode = "google"
            except Exception as exc:
                print(f"✗ Impossible d'initialiser l'activité Android: {exc}")
                self.mode = "disabled"
        else:
            print("ℹ️ In-App non disponible (plateforme desktop ou PyJNIus absent)")
            if platform != "android":
                self.mode = "simulation"

    def add_state_listener(self, callback):
        """Ajoute un callback notifié à chaque changement d'état."""

        if callback not in self.state_observers:
            self.state_observers.append(callback)
        # notifier immédiatement de l'état courant
        self._dispatch_state_change()

    def _dispatch_state_change(self):
        for callback in list(self.state_observers):
            try:
                Clock.schedule_once(
                    lambda dt, cb=callback: cb(
                        self.is_ready(), self.display_price, self.mode
                    ),
                    0,
                )
            except Exception as exc:
                print(f"⚠️ Erreur notification observateur Billing: {exc}")

    def initialize(self):
        if self.mode == "google":
            self._setup_google_billing()
        elif self.mode == "amazon":
            self._setup_amazon_billing()
        else:
            self._dispatch_state_change()

    def is_ready(self):
        if self.mode == "google":
            return bool(self.billing_ready and self.google_sku_details)
        if self.mode == "amazon":
            return self.amazon_ready
        if self.mode == "simulation":
            return True
        return False

    def start_premium_purchase(self):
        if self.mode == "google":
            self._start_google_purchase()
        elif self.mode == "amazon":
            self._start_amazon_purchase()
        else:
            if self.mode == "simulation":
                print("ℹ️ Simulation achat sur plateforme non Android")
                self._notify_success("simulation")
            else:
                self._notify_error(
                    "Boutique indisponible", provider=self.mode or "inapp"
                )

    # --- Google Play Billing -------------------------------------------------
    def _setup_google_billing(self):
        if not self.activity:
            self._notify_error(
                "Aucun contexte Android disponible", provider="google"
            )
            return
        try:
            self.google_client_class = autoclass(
                "com.android.billingclient.api.BillingClient"
            )
            self.google_purchase_listener = GooglePurchasesUpdatedListener(self)
            self.google_billing_client = (
                self.google_client_class
                .newBuilder(self.activity)
                .setListener(self.google_purchase_listener)
                .enablePendingPurchases()
                .build()
            )
            self.google_state_listener = GoogleBillingStateListener(self)
            self.google_billing_client.startConnection(self.google_state_listener)
            print("⏳ Connexion à Google Play Billing...")
        except Exception as exc:
            print(f"✗ Erreur initialisation Billing Google: {exc}")
            self._notify_error(
                "Erreur Google Play Billing", provider="google"
            )

    def _on_google_billing_ready(self):
        self.billing_ready = True
        self._query_google_sku_details()
        self._dispatch_state_change()

    def _query_google_sku_details(self):
        if not self.google_billing_client:
            return
        try:
            ArrayList = autoclass("java.util.ArrayList")
            sku_list = ArrayList()
            sku_list.add(self.GOOGLE_PRODUCT_ID)
            params_builder = autoclass(
                "com.android.billingclient.api.SkuDetailsParams$Builder"
            )()
            params_builder = params_builder.setType(
                self.google_client_class.SkuType.INAPP
            )
            params_builder = params_builder.setSkusList(sku_list)
            params = params_builder.build()
            self.google_sku_listener = GoogleSkuDetailsListener(self)
            self.google_billing_client.querySkuDetailsAsync(
                params, self.google_sku_listener
            )
            print("⏳ Récupération des détails produit Google...")
        except Exception as exc:
            print(f"✗ Erreur requête SKU Google: {exc}")
            self._notify_error(
                "Impossible de récupérer le produit",
                provider="google",
            )

    def _start_google_purchase(self):
        if not self.google_billing_client:
            self._notify_error(
                "Service de facturation indisponible",
                provider="google",
            )
            return
        if not self.google_sku_details:
            self._notify_error(
                "Produit en cours de chargement",
                provider="google",
                warn_only=True,
            )
            self._query_google_sku_details()
            return
        try:
            params_builder = autoclass(
                "com.android.billingclient.api.BillingFlowParams$Builder"
            )()
            params_builder = params_builder.setSkuDetails(self.google_sku_details)
            params = params_builder.build()

            runnable = LaunchBillingRunnable(self, params)
            self.activity.runOnUiThread(runnable)
        except Exception as exc:
            print(f"✗ Exception lancement achat Google: {exc}")
            self._notify_error(
                "Impossible de lancer l'achat",
                provider="google",
            )

    # --- Amazon IAP ----------------------------------------------------------
    def _setup_amazon_billing(self):
        if not self.activity:
            self._notify_error(
                "Aucun contexte Android disponible", provider="amazon"
            )
            return
        try:
            self.amazon_service = autoclass(
                "com.amazon.device.iap.PurchasingService"
            )
            self.amazon_listener = AmazonPurchasingListener(self)
            self.amazon_service.registerListener(
                self.activity.getApplicationContext(), self.amazon_listener
            )
            # Déclenche une récupération d'état pour valider la disponibilité
            self.amazon_service.getUserData()
            self.amazon_service.getPurchaseUpdates(False)
            self.amazon_ready = True
            print("✅ Amazon IAP initialisé")
            self._dispatch_state_change()
        except Exception as exc:
            print(f"✗ Erreur initialisation Amazon IAP: {exc}")
            self._notify_error(
                "Erreur Amazon IAP", provider="amazon"
            )

    def _start_amazon_purchase(self):
        if not self.amazon_ready:
            self._notify_error(
                "Boutique Amazon en cours de préparation",
                provider="amazon",
                warn_only=True,
            )
            return
        try:
            self.amazon_service.purchase(self.AMAZON_PRODUCT_ID)
        except Exception as exc:
            print(f"✗ Erreur lancement achat Amazon: {exc}")
            self._notify_error(
                "Impossible de lancer l'achat",
                provider="amazon",
            )

    # --- Notifications -------------------------------------------------------
    def _notify_success(self, provider="google"):
        print(f"🎉 Achat réussi via {provider}")

        if self.on_success:
            Clock.schedule_once(
                lambda dt: self.on_success(provider=provider), 0
            )

    def _notify_error(
        self, message, provider="google", warn_only=False
    ):
        level = "⚠️" if warn_only else "✗"
        print(f"{level} {message} ({provider})")
        if self.on_error and not warn_only:
            Clock.schedule_once(
                lambda dt: self.on_error(message=message, provider=provider),
                0,
            )
# Classe pour la publicité
class AdPopup(Popup):
    """Popup de publicité"""
    
    def __init__(self, **kwargs):
        super(AdPopup, self).__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        self.separator_height = 0
        
        layout = BoxLayout(orientation="vertical", spacing=20, padding=[20, 20, 20, 20])
        
        # Background
        with layout.canvas.before:
            Color(0.1, 0.15, 0.3, 0.95)
            self.bg_rect = RoundedRectangle(
                pos=layout.pos, 
                size=layout.size,
                radius=[15, 15, 15, 15]
            )
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Titre publicité
        ad_title = Label(
            text=tr("support_app"),  # "Soutenez l'application"
            font_size="20sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.2,
            bold=True,
            halign='center',
            valign='middle',
        )
        ad_title.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.9, None)))
        layout.add_widget(ad_title)
        
        # Message
        ad_message = Label(
            text=tr("ad_message"),  # Message de soutien
            font_size="16sp",
            color=[1, 1, 1, 1],
            size_hint_y=0.4,
            halign='center',
            valign='middle',
        )
        ad_message.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.85, None)))
        layout.add_widget(ad_message)
        
        # Zone boutons
        button_layout = BoxLayout(orientation="horizontal", spacing=dp(16), size_hint_y=None, height=dp(50), pos_hint={'center_x': 0.5})
        
        # Bouton "Plus tard"
        later_btn = Button(
            text=tr("later"),  # "Plus tard"
            size_hint=(0.5, 1),
            font_size="16sp",
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1]
        )
        with later_btn.canvas.before:
            Color(0.5, 0.5, 0.5, 0.8)
            later_btn_bg = RoundedRectangle(pos=later_btn.pos, size=later_btn.size, radius=[25])
        later_btn.bind(pos=lambda i, v: setattr(later_btn_bg, 'pos', v), size=lambda i, v: setattr(later_btn_bg, 'size', v))
        later_btn.bind(on_press=self.close_ad)
        
        # Bouton "Soutenir"
        support_btn = Button(
            text=tr("support"),  # "Soutenir"
            size_hint=(0.5, 1),
            font_size="16sp",
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            bold=True
        )
        with support_btn.canvas.before:
            Color(0.2, 0.7, 0.2, 1)
            support_btn_bg = RoundedRectangle(pos=support_btn.pos, size=support_btn.size, radius=[25])
        support_btn.bind(pos=lambda i, v: setattr(support_btn_bg, 'pos', v), size=lambda i, v: setattr(support_btn_bg, 'size', v))
        support_btn.bind(on_press=self.open_support)
        
        button_layout.add_widget(later_btn)
        button_layout.add_widget(support_btn)
        layout.add_widget(button_layout)
        
        self.content = layout
        
        # Animation d'entrée
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.3)
        entrance_anim.start(self)
        
        # Auto-fermeture après 10 secondes
        Clock.schedule_once(self.auto_close, 10)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def close_ad(self, instance):
        print("🎯 Publicité fermée")
        exit_anim = Animation(opacity=0, duration=0.2)
        exit_anim.bind(on_complete=lambda *args: self.dismiss())
        exit_anim.start(self)
    
    def open_support(self, instance):
        print("💝 Ouverture page de soutien")
        # Ici vous pouvez ajouter le lien vers votre page de soutien
        self.close_ad(instance)
    
    def auto_close(self, dt):
        print("⏰ Auto-fermeture publicité")
        self.close_ad(None)


class FullScreenCardPopup(Popup):
    """Popup plein écran pour afficher la carte"""
    
    def __init__(self, card_image_source, card_name, card_state, **kwargs):
        super(FullScreenCardPopup, self).__init__(**kwargs)
        
        self.title = ""
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.separator_height = 0
        
        layout = BoxLayout(orientation="vertical", spacing=0)
        
        with layout.canvas.before:
            Color(0, 0, 0, 0.95)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header avec nom et état
        header = BoxLayout(orientation="vertical", size_hint_y=0.15, padding=[20, 10])
        
        title_label = Label(
            text=card_name,
            font_size="24sp",
            color=[0.9, 0.7, 0.3, 1],
            halign='center',
            valign='middle',
            bold=True
        )
        title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.9, None)))
        header.add_widget(title_label)
        
        state_label = Label(
            text=card_state,
            font_size="17sp",
            color=[0.8, 0.6, 0.4, 1],
            halign='center',
            valign='middle',
            bold=True
        )
        state_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.9, None)))
        header.add_widget(state_label)
        layout.add_widget(header)
        
        # Zone carte cliquable
        card_container = FloatLayout(size_hint_y=0.7)
        
        self.fullscreen_image = Image(
            source=card_image_source,
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        
        close_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        close_button.bind(on_press=self.close_fullscreen)
        
        card_container.add_widget(self.fullscreen_image)
        card_container.add_widget(close_button)
        layout.add_widget(card_container)
        
        # Footer
        footer = BoxLayout(orientation="vertical", size_hint_y=0.2, padding=[20, 10], spacing=dp(8))
        instruction = Label(
            text=tr("tap_to_return"),  # Au lieu de "Touchez la carte pour revenir"
            font_size="16sp",
            color=[0.7, 0.7, 0.7, 1],
            halign='center',
            valign='middle',
            italic=True
        )
        instruction.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        footer.add_widget(instruction)
        banner_text = random.choice([
            tr("crystals_ad"),
            tr("love_ad"),
            tr("tarot_course_ad"),
        ])
        ad_label = Label(
            text=banner_text,
            font_size="14sp",
            color=[1, 0.85, 0.3, 1],
            halign='center',
            valign='middle',
        )
        ad_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0] * 0.95, None)))
        footer.add_widget(ad_label)
        layout.add_widget(footer)
        
        self.content = layout
        
        # Animation d'entrée
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.3)
        entrance_anim.start(self)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def close_fullscreen(self, instance):
        exit_anim = Animation(opacity=0, duration=0.2)
        exit_anim.bind(on_complete=lambda *args: self.dismiss())
        exit_anim.start(self)


class LoadingPopup(Popup):
    """Popup de chargement avec animation d'images de dos de cartes"""
    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.7, 0.5)
        self.auto_dismiss = False
        self.separator_height = 0

        layout = BoxLayout(orientation="vertical", spacing=10, padding=[20, 20, 20, 20])

        # Label de chargement
        self.loading_label = Label(
            text=tr("concentrating"),
            font_size="17sp",
            color=[0.9, 0.7, 0.3, 1],
            halign='center',
            valign='middle',
        )
        self.loading_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        layout.add_widget(self.loading_label)

        # Zone animation
        self.anim_zone = FloatLayout(size_hint_y=0.8)
        layout.add_widget(self.anim_zone)

        # Deux tas fixes
        self.left_stack = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.05, 'center_y': 0.5},
            opacity=1
        )
        self.right_stack = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.7, 'center_y': 0.5},
            opacity=1
        )
        self.anim_zone.add_widget(self.left_stack)
        self.anim_zone.add_widget(self.right_stack)

        # Carte animée (au départ sur le tas de gauche)
        self.animated_card = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.05, 'center_y': 0.5},
            opacity=1
        )
        self.anim_zone.add_widget(self.animated_card)

        self.content = layout

        # Lance l'animation
        self.shuffle_direction = "right"
        self.shuffle_anim = None
        self.start_shuffle_animation()

        # Bannière publicitaire pendant le brassage
        ad_choices = ["crystals_ad", "love_ad", "tarot_course_ad"]
        chosen_ad = tr(random.choice(ad_choices))
        self.ad_banner = Label(
            text=chosen_ad,
            font_size="14sp",
            color=[1, 0.82, 0.35, 1],
            size_hint_y=None,
            height=dp(40),
            halign="center",
            valign="middle",
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0] * 0.95, None)))
        layout.add_widget(self.ad_banner)

        Clock.schedule_once(lambda dt: self.update_message(tr("preparing_arcana")), 1.5)
        Clock.schedule_once(lambda dt: self.update_message(tr("drawing_card")), 3)

    def start_shuffle_animation(self):
        # Animation de gauche à droite ou droite à gauche
        if self.shuffle_direction == "right":
            anim = Animation(pos_hint={'x': 0.7, 'center_y': 0.5}, duration=0.4)
            anim.bind(on_complete=lambda *a: self.switch_shuffle_direction())
            anim.start(self.animated_card)
        else:
            anim = Animation(pos_hint={'x': 0.05, 'center_y': 0.5}, duration=0.4)
            anim.bind(on_complete=lambda *a: self.switch_shuffle_direction())
            anim.start(self.animated_card)

    def switch_shuffle_direction(self):
        # Change de direction et relance l'animation
        self.shuffle_direction = "left" if self.shuffle_direction == "right" else "right"
        self.start_shuffle_animation()

    def update_message(self, message):
        self.loading_label.text = message

    def on_dismiss(self):
        # Stoppe l'animation si besoin (optionnel)
        if self.shuffle_anim:
            self.shuffle_anim.cancel_all(self.animated_card)


class RootScreen(ScreenManager):
    """Gestionnaire d'écrans"""
    
    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        print("RootScreen initialisé")


class CardScreen(Screen):
    """Écran principal responsable du tirage."""

    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)
        print("CardScreen créé")

        self.loading_popup = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        with layout.canvas.before:
            Color(0.2, 0.1, 0.3, 1)
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg.source = "tarot_img/bg.jpg"
        layout.bind(pos=self.update_bg, size=self.update_bg)

        self.title_label = Label(
            text=tr("app_title"),
            font_size="22sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.15,
            bold=True,
            halign='center',
            valign='middle',
        )
        self.title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None)))
        layout.add_widget(self.title_label)

        card_container = FloatLayout(size_hint_y=0.7)
        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.8, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )
        self.draw_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.8, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )
        self.draw_button.bind(on_press=self.draw_card)
        card_container.add_widget(self.card_image)
        card_container.add_widget(self.draw_button)
        layout.add_widget(card_container)

        self.instructions_label = Label(
            text=tr("draw_instruction"),
            font_size="18sp",
            color=[0.7, 0.5, 0.3, 1],
            size_hint_y=0.15,
            halign='center',
            valign='middle',
        )
        self.instructions_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        layout.add_widget(self.instructions_label)

        self.ad_banner = Label(
            text=tr("crystals_ad"),
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=0.08,
            halign='center',
            valign='middle',
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        layout.add_widget(self.ad_banner)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def draw_card(self, _instance):
        print("=== NOUVEAU TIRAGE ===")

        click_anim = Animation(opacity=0.3, duration=0.1)
        click_anim += Animation(opacity=1, duration=0.1)
        click_anim.start(self.draw_button)

        self.loading_popup = LoadingPopup()
        self.loading_popup.open()

        Clock.schedule_once(self.perform_card_draw, 4)

    def perform_card_draw(self, _dt):
        try:
            cards_signification = get_cards_signification()
            cards = list(cards_signification.keys())
            drawn_card = random.choice(cards)
            drawn_state = random.choice(["droite", "a l'envers"])

            print(f"Carte tirée: {drawn_card} - {drawn_state}")
            print(f"📊 Lecture #{READING_COUNT + 1}")

            if self.loading_popup:
                self.loading_popup.dismiss()

            app = App.get_running_app()
            if hasattr(app, "ads"):
                app.ads.on_card_drawn()

            def _show_response_screen(*_args):
                if self.manager:
                    response_screen = self.manager.get_screen("response_screen")
                    response_screen.setup_card(drawn_card, drawn_state)
                    self.manager.current = "response_screen"

            if should_show_ad():
                print("🎯 Affichage d'une grande publicité interstitielle maison")
                self.ads_popup = AdsPopup(on_close_callback=_show_response_screen)
                self.ads_popup.bind(on_dismiss=lambda *_: setattr(self, "ads_popup", None))
                self.ads_popup.open()
            else:
                _show_response_screen()

        except Exception as exc:
            print(f"Erreur tirage: {exc}")
            if self.loading_popup:
                self.loading_popup.dismiss()

    def on_enter(self, *args):
        print("Entrée sur CardScreen")


class ChatBubble(BoxLayout):
    """Simple chat bubble with rounded background."""

    def __init__(self, text: str, from_user: bool = False, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("spacing", dp(2))
        super().__init__(**kwargs)

        self.from_user = from_user
        self.max_width = dp(260)
        self.padding = (
            [dp(14), dp(9), dp(10), dp(9)] if from_user else [dp(10), dp(9), dp(14), dp(9)]
        )

        # Couleurs style Messenger
        bubble_color = [0.92, 0.92, 0.95, 1]  # Gris clair pour Mme T
        text_color = [0.2, 0.2, 0.2, 1]  # Texte noir
        if from_user:
            bubble_color = [0.35, 0.15, 0.55, 1]  # Violet pour utilisateur
            text_color = [1, 1, 1, 1]  # Texte blanc

        with self.canvas.before:
            self._bg_color = Color(*bubble_color)
            self._bg_rect = RoundedRectangle(radius=[dp(18)] * 4)

        self.label = Label(
            text="",
            font_size="15sp",
            color=text_color,
            halign="left",
            valign="top",
            size_hint=(None, None),
        )
        self.label.bind(texture_size=lambda *_: self._refresh())
        self.add_widget(self.label)

        self.bind(pos=self._update_bg, size=self._update_bg)
        self.set_text(text)

    def set_text(self, text: str) -> None:
        self.label.text = text
        self.label.texture_update()
        self._refresh()

    def set_max_width(self, width: float) -> None:
        try:
            width = float(width)
        except Exception:
            width = self.max_width
        self.max_width = max(dp(160), min(width, dp(360)))
        self._refresh()

    def _refresh(self) -> None:
        self.label.text_size = (self.max_width, None)
        self.label.texture_update()
        label_width, label_height = self.label.texture_size
        self.label.size = (min(label_width, self.max_width), label_height)
        left, top, right, bottom = self.padding
        self.width = self.label.width + left + right
        self.height = self.label.height + top + bottom
        self._update_bg()

    def _update_bg(self, *_args) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class MmeTChatPopup(Popup):
    """Fenetre modale modernisée pour la consultation premium avec Mme T."""

    INTRO_TEXTS = {
        "fr": "Bonjour ✨ Je suis Mme T, ta cartomancienne. Quelle question te preoccupe aujourd'hui ? En quoi puis-je t'aider ?",
        "en": "Hello ✨ I'm Mme T, your card reader. What question is on your mind today? How can I help you?",
        "es": "Hola ✨ Soy Mme T, tu cartomante. ¿Que pregunta te preocupa hoy? ¿En que puedo ayudarte?",
        "pt": "Ola ✨ Sou Mme T, a tua cartomante. Que questao te preocupa hoje? Em que posso ajudar-te?",
    }

    THANK_TEXTS = {
        "fr": "Merci d'avoir consulte Mme T. Reviens quand tu veux pour une nouvelle guidance.",
        "en": "Thank you for consulting Mme T. Come back anytime for another guidance.",
        "es": "Gracias por consultar a Mme T. Vuelve cuando quieras para otra guia.",
        "pt": "Obrigada por consultar Mme T. Volta quando quiseres para outra orientacao.",
    }

    def __init__(
        self,
        language="fr",
        provider="google",
        price_text=None,
        context_text="",
        on_session_complete=None,
        **kwargs,
    ):
        kwargs.setdefault("title", "")
        kwargs.setdefault("size_hint", (1, 1))  # Plein écran
        kwargs.setdefault("separator_height", 0)
        super().__init__(**kwargs)

        self.language = (language or "fr").lower()
        self.provider = provider or "google"
        self.price_text = price_text
        self.session_id = str(uuid.uuid4())
        self.backend_url = _normalize_mme_t_backend_url(MME_T_BACKEND_URL or DEFAULT_MME_T_SPACE)
        self.is_gradio_space = "hf.space" in (self.backend_url or "")
        self.context_text = context_text or ""
        self.conversation_history = []  # Historique [{"role": "user"/"assistant", "content": "..."}]
        self.model_id = MME_T_DEFAULT_MODEL
        self.awaiting_reply = False
        self.typewriter_event = None
        self._typewriter_index = 0
        self._typewriter_source = ""
        self._typewriter_on_complete = None
        self._active_bubble = None
        self.on_session_complete = on_session_complete
        self._close_reason = None
        self.chat_bubbles = []  # type: list[ChatBubble]
        
        # Animation de chargement
        self._loading_event = None
        self._loading_index = 0
        self._loading_bubble = None

        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(12), dp(12), dp(12)],
            spacing=dp(10),
        )

        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.98, 1)  # Fond blanc/gris clair comme Messenger
            self._panel_bg = RoundedRectangle(radius=[dp(20)] * 4)
        main_layout.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8), padding=[dp(8), dp(4)])
        
        # Bouton retour (gauche)
        back_btn = Button(
            text="←",
            size_hint=(None, None),
            width=dp(44),
            height=dp(44),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[0.35, 0.15, 0.55, 1],
            font_size="26sp",
            bold=True,
        )
        back_btn.bind(on_release=self._manual_close)
        
        title_label = Label(
            text="Mme T",
            font_size="17sp",
            color=[0.2, 0.2, 0.2, 1],
            halign="center",
            valign="middle",
            bold=True,
        )
        title_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        
        # Espace vide à droite pour équilibrer
        spacer = Label(size_hint=(None, None), width=dp(44), height=dp(44))
        
        header.add_widget(back_btn)
        header.add_widget(title_label)
        header.add_widget(spacer)
        
        main_layout.add_widget(header)

        self.status_label = Label(
            text=self._status_prefix(),
            font_size="11sp",
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height=dp(22),
            halign="center",
            valign="middle",
        )
        self.status_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0] * 0.95, val[1])))
        main_layout.add_widget(self.status_label)

        self.response_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=0)
        self.chat_container = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(4), dp(6), dp(4), dp(6)],
        )
        self.chat_container.bind(minimum_height=self.chat_container.setter("height"))
        self.response_scroll.add_widget(self.chat_container)
        main_layout.add_widget(self.response_scroll)

        # Zone de saisie style Messenger
        input_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52), spacing=dp(10), padding=[dp(10), dp(6)])
        
        self.question_input = TextInput(
            hint_text=self._label("ask_hint"),
            size_hint=(1, None),
            height=dp(40),
            multiline=False,
            background_normal='',
            background_color=[0.94, 0.94, 0.96, 1],
            foreground_color=[0.2, 0.2, 0.2, 1],
            cursor_color=[0.35, 0.15, 0.55, 1],
            padding=[dp(14), dp(10)],
            font_size="15sp",
        )
        
        self.send_btn = Button(
            text=self._label("send"),
            size_hint=(None, None),
            width=dp(75),
            height=dp(40),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="14sp",
            bold=True,
        )
        with self.send_btn.canvas.before:
            Color(0.35, 0.15, 0.55, 1)
            self.send_btn_bg = RoundedRectangle(pos=self.send_btn.pos, size=self.send_btn.size, radius=[20])
        self.send_btn.bind(pos=lambda i, v: setattr(self.send_btn_bg, 'pos', v), size=lambda i, v: setattr(self.send_btn_bg, 'size', v))
        self.send_btn.bind(on_press=self.on_send_question)
        
        input_container.add_widget(self.question_input)
        input_container.add_widget(self.send_btn)
        main_layout.add_widget(input_container)
        
        # Bouton de fermeture en bas
        close_btn_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(45), padding=[dp(10), dp(4)])
        self.close_btn = Button(
            text="✓ " + self._label("done"),
            size_hint=(1, None),
            height=dp(38),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="13sp",
        )
        with self.close_btn.canvas.before:
            Color(0.2, 0.6, 0.3, 1)
            self.close_btn_bg = RoundedRectangle(pos=self.close_btn.pos, size=self.close_btn.size, radius=[20])
        self.close_btn.bind(pos=lambda i, v: setattr(self.close_btn_bg, 'pos', v), size=lambda i, v: setattr(self.close_btn_bg, 'size', v))
        self.close_btn.bind(on_press=lambda *_: self.dismiss())
        close_btn_container.add_widget(self.close_btn)
        main_layout.add_widget(close_btn_container)

        self.content = main_layout

        self.bind(size=self._update_bubble_widths)
        self.response_scroll.bind(width=self._update_bubble_widths)

        if not self.backend_url:
            self.send_btn.disabled = True
            self.status_label.text = self._label("no_backend")
        else:
            self.start_typewriter(self.INTRO_TEXTS.get(self.language, self.INTRO_TEXTS["fr"]), sender="mme_t")

    def _status_prefix(self):
        base = {
            "fr": "Merci pour votre soutien",
            "en": "Thank you for your support",
            "es": "Gracias por tu apoyo",
            "pt": "Obrigada pelo teu apoio",
        }.get(self.language, "Merci pour votre soutien")
        provider_label = {
            "google": "Google Play",
            "amazon": "Amazon Appstore",
        }.get(self.provider, "")
        return f"{base}{' - ' + provider_label if provider_label else ''}"

    def _label(self, key):
        labels = {
            "send": {
                "fr": "Envoyer ma question",
                "en": "Send my question",
                "es": "Enviar mi pregunta",
                "pt": "Enviar a minha pergunta",
            },
            "ask_hint": {
                "fr": "Ta question...",
                "en": "Your question...",
                "es": "Tu pregunta...",
                "pt": "A tua questao...",
            },
            "send": {
                "fr": "Envoyer",
                "en": "Send",
                "es": "Enviar",
                "pt": "Enviar",
            },
            "sending": {
                "fr": "Connexion...",
                "en": "Connecting...",
                "es": "Conectando...",
                "pt": "A ligar...",
            },
            "connecting": {
                "fr": "Mme T arrive dans quelques instants...",
                "en": "Mme T will be here in a moment...",
                "es": "Mme T llegara en unos momentos...",
                "pt": "Mme T chegara em breve...",
            },
            "no_backend": {
                "fr": "Service indisponible : configurez MME_T_BACKEND_URL.",
                "en": "Service unavailable: configure MME_T_BACKEND_URL.",
            },
            "error": {
                "fr": "Mme T est indisponible. Verifie ta connexion et reessaie.",
                "en": "Mme T is unavailable. Check your connection and try again.",
                "es": "Mme T no esta disponible. Verifica tu conexion e intentalo de nuevo.",
                "pt": "Mme T esta indisponivel. Verifica a tua ligacao e tenta novamente.",
            },
            "done": {
                "fr": "Consultation terminee",
                "en": "Reading complete",
                "es": "Lectura completada",
                "pt": "Consulta concluida",
            },
        }
        bundle = labels.get(key, {})
        return bundle.get(self.language, bundle.get("en", ""))

    def _manual_close(self, *_args):
        self._close_reason = "manual"
        self.dismiss()

    def _update_panel_bg(self, instance, _value):
        if hasattr(self, "_panel_bg") and self._panel_bg:
            self._panel_bg.pos = instance.pos
            self._panel_bg.size = instance.size

    def _bubble_max_width(self) -> float:
        available = self.response_scroll.width - dp(56) if self.response_scroll else self.width * 0.7
        if available <= 0:
            available = self.width * 0.72
        return max(dp(180), min(available, self.width * 0.85))

    def _update_bubble_widths(self, *_args):
        if not self.chat_bubbles:
            return
        max_width = self._bubble_max_width()
        for bubble in self.chat_bubbles:
            bubble.set_max_width(max_width)

    def start_typewriter(self, text: str, sender: str = "mme_t", speed: float = 0.02, on_complete=None):
        if self.typewriter_event:
            self.typewriter_event.cancel()
            self.typewriter_event = None
        self._typewriter_source = text or ""
        self._typewriter_index = 0
        self._typewriter_on_complete = on_complete
        self._active_bubble = self._create_message_bubble("", sender)
        self._update_bubble_widths()
        if not self._typewriter_source:
            self._finalize_typewriter()
            return
        self.typewriter_event = Clock.schedule_interval(lambda dt: self._advance_typewriter(), speed)

    def add_message(self, text: str, sender: str) -> None:
        bubble = self._create_message_bubble(text, sender)
        bubble.set_text(text)
        self._update_bubble_widths()
        self._scroll_to_widget(bubble)

    def _advance_typewriter(self):
        if self._typewriter_index >= len(self._typewriter_source):
            self._finalize_typewriter()
            return False
        self._typewriter_index += 1
        if self._active_bubble:
            self._active_bubble.set_text(self._typewriter_source[: self._typewriter_index])
            self._scroll_to_widget(self._active_bubble)
        return True

    def _finalize_typewriter(self):
        if self.typewriter_event:
            self.typewriter_event.cancel()
            self.typewriter_event = None
        if self._active_bubble:
            self._active_bubble.set_text(self._typewriter_source)
            self._scroll_to_widget(self._active_bubble)
            self._active_bubble = None
        if self._typewriter_on_complete:
            callback = self._typewriter_on_complete
            self._typewriter_on_complete = None
            Clock.schedule_once(lambda _dt: callback(), 0)
        return False

    def _create_message_bubble(self, text: str, sender: str):
        from_user = sender == "user"
        anchor = AnchorLayout(
            size_hint=(1, None),
            anchor_x="right" if from_user else "left",
            anchor_y="center",
            padding=[dp(6), 0, dp(6), 0],
        )
        bubble = ChatBubble(text, from_user=from_user)
        bubble.set_max_width(self._bubble_max_width())
        anchor.add_widget(bubble)
        anchor.height = bubble.height + dp(4)
        bubble.bind(size=lambda _inst, val: setattr(anchor, "height", val[1] + dp(4)))
        self.chat_container.add_widget(anchor)
        self.chat_bubbles.append(bubble)
        self._scroll_to_widget(bubble)
        return bubble

    def _scroll_to_widget(self, widget):
        if not self.response_scroll:
            return
        Clock.schedule_once(lambda _dt: self.response_scroll.scroll_to(widget), 0.05)
    
    def _start_loading_animation(self):
        """Démarre l'animation de chargement avec messages rotatifs"""
        self._loading_index = 0
        
        # Récupérer les messages de chargement selon la langue
        loading_messages = MESSAGES.get(self.language, MESSAGES["fr"]).get("loading_messages", [
            "🔮 Je me concentre sur ta question...",
            "🃏 Mélange des cartes en cours...",
            "✨ Les énergies s'alignent...",
            "🌙 Consultation des astres...",
            "💫 Interprétation des arcanes...",
        ])
        
        # Créer la bulle de chargement
        self._loading_bubble = self._create_message_bubble(loading_messages[0], sender="mme_t")
        
        def _update_loading_message(dt):
            if not self._loading_bubble or self.awaiting_reply == False:
                return False  # Arrêter l'animation
            
            self._loading_index = (self._loading_index + 1) % len(loading_messages)
            new_text = loading_messages[self._loading_index]
            
            # Mettre à jour le texte de la bulle
            if hasattr(self._loading_bubble, 'label'):
                self._loading_bubble.label.text = new_text
            
            return True  # Continuer l'animation
        
        # Changer le message toutes les 2 secondes
        self._loading_event = Clock.schedule_interval(_update_loading_message, 2.0)
    
    def _stop_loading_animation(self):
        """Arrête et supprime l'animation de chargement"""
        if self._loading_event:
            self._loading_event.cancel()
            self._loading_event = None
        
        # Supprimer la bulle de chargement
        if self._loading_bubble:
            # Trouver le parent (anchor) de la bulle
            for child in self.chat_container.children:
                if isinstance(child, AnchorLayout):
                    for bubble_widget in child.children:
                        if bubble_widget == self._loading_bubble:
                            self.chat_container.remove_widget(child)
                            if self._loading_bubble in self.chat_bubbles:
                                self.chat_bubbles.remove(self._loading_bubble)
                            break
            self._loading_bubble = None

    def on_send_question(self, *_args):
        if self.awaiting_reply or not self.backend_url:
            return
        question = self.question_input.text.strip()
        if not question:
            return
        
        # LOG: Afficher la question dans le terminal
        print(f"\n{'='*60}")
        print(f"👤 QUESTION UTILISATEUR:")
        print(f"   {question}")
        print(f"{'='*60}\n")
        
        # Afficher le message utilisateur
        self.add_message(question, sender="user")
        self.question_input.text = ""
        self.question_input.disabled = True
        self.send_btn.disabled = True
        
        # Afficher "Mme T arrive dans quelques instants..."
        self.status_label.text = self._label("connecting")
        
        # Démarrer l'animation de chargement
        self._start_loading_animation()
        
        # Attendre 2.5 secondes avant de vraiment envoyer (effet humain)
        def _delayed_send():
            self.awaiting_reply = True
            self.send_btn.text = "..."
            
            # Ajouter la question à l'historique
            self.conversation_history.append({"role": "user", "content": question})
            
            # Construire le contexte complet avec l'historique
            full_context = self.context_text
            if len(self.conversation_history) > 1:  # Si on a déjà des échanges
                history_text = "\n\nHistorique de la conversation:\n"
                # Prendre tous les échanges sauf la question actuelle
                for entry in self.conversation_history[:-1]:
                    role = "Vous" if entry["role"] == "user" else "Mme T"
                    history_text += f"{role}: {entry['content']}\n"
                full_context = full_context + history_text
            
            print(f"[MME T DEBUG] Contexte envoyé (avec historique):\n{full_context}\n")
            
            payload = {
                "message": question,
                "language": self.language,
                "session_id": self.session_id,
                "model": self.model_id,
                "context": full_context,
            }
            threading.Thread(target=self._perform_request, args=(payload,), daemon=True).start()
        
        Clock.schedule_once(lambda dt: _delayed_send(), 2.5)

    def _perform_request(self, payload):
        try:
            if self.is_gradio_space:
                reply = self._call_gradio_backend(payload["message"], payload.get("context") or "")
            else:
                url = self.backend_url.rstrip("/") + "/chat"
                response = requests.post(url, json=payload, timeout=25)
                response.raise_for_status()
                data = response.json()
                reply = (data.get("reply") or "").strip()
                if not reply:
                    raise ValueError("Réponse vide")
            
            # LOG: Afficher la réponse dans le terminal
            print(f"\n{'='*60}")
            print(f"🔮 RÉPONSE MME T:")
            print(f"   {reply}")
            print(f"{'='*60}\n")
            
            Clock.schedule_once(lambda dt: self._on_success(reply), 0)
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ERREUR MME T:")
            print(f"   {str(e)}")
            print(f"{'='*60}\n")
            Clock.schedule_once(lambda dt: self._on_error(), 0)

    def _on_success(self, reply_text):
        # Arrêter l'animation de chargement
        self._stop_loading_animation()
        
        # Ajouter la réponse à l'historique
        self.conversation_history.append({"role": "assistant", "content": reply_text})
        
        self.awaiting_reply = False
        # Réactiver les champs pour permettre la conversation continue
        self.question_input.disabled = False
        self.send_btn.disabled = False
        self.send_btn.text = self._label("send")
        # Message encourageant à continuer la discussion
        continue_texts = {
            "fr": "Tu peux me poser d'autres questions sur cette lecture...",
            "en": "You can ask me more about this reading...",
            "es": "Puedes preguntarme más sobre esta lectura...",
            "pt": "Podes perguntar-me mais sobre esta leitura...",
            "de": "Du kannst mich mehr über diese Legung fragen...",
            "it": "Puoi chiedermi di più su questa lettura...",
        }
        self.status_label.text = continue_texts.get(self.language, continue_texts["fr"])
        self.start_typewriter(reply_text, sender="mme_t")

    def _schedule_session_close(self):
        # Cette fonction n'est plus appelée automatiquement
        # L'utilisateur ferme manuellement ou via un bouton
        if self._close_reason == "completed":
            return
        self._close_reason = "completed"
        Clock.schedule_once(lambda _dt: self.dismiss(), 1.5)

    def _on_error(self):
        # Arrêter l'animation de chargement
        self._stop_loading_animation()
        
        self.awaiting_reply = False
        self.send_btn.disabled = False
        self.send_btn.text = self._label("send")
        self.question_input.disabled = False
        self.status_label.text = self._label("error")
        self.start_typewriter(self._label("error"), sender="mme_t")

    def _call_gradio_backend(self, message: str, context_text: str) -> str:
        """Appelle le backend Gradio avec le client officiel ou REST en fallback"""
        
        # LOG: Afficher les paramètres envoyés
        print(f"\n{'='*60}")
        print(f"📤 ENVOI AU BACKEND:")
        print(f"   Message: {message}")
        print(f"   Contexte: {context_text or '(vide)'}")
        print(f"   URL: {self.backend_url}")
        print(f"{'='*60}\n")
        
        # Méthode 1: Client Gradio officiel (recommandé)
        if GRADIO_CLIENT_AVAILABLE:
            try:
                print(f"🔮 Connexion via Gradio Client...")
                # Extraire le Space ID depuis l'URL (ex: Loupy222/mme_t)
                space_id = self._extract_space_id(self.backend_url)
                
                if space_id:
                    print(f"📡 Space ID: {space_id}")
                    client = GradioClient(space_id)
                    print(f"✅ Client connecté!")
                    
                    result = client.predict(
                        message=message,
                        contexte=context_text or "",
                        api_name="/predict"
                    )
                    
                    if isinstance(result, str) and result.strip():
                        print(f"✅ Réponse reçue ({len(result)} caractères)")
                        return result.strip()
                    else:
                        print(f"⚠️ Format inattendu: {type(result)}")
                        
            except Exception as client_exc:
                print(f"⚠️ Gradio Client échoué: {client_exc}")
                print("🔄 Basculement vers REST API...")
        
        # Méthode 2: REST API Fallback
        base_url = (self.backend_url or "").rstrip("/")
        print(f"🔗 Tentative de connexion REST à: {base_url}")
        
        # Réveil du backend (requis pour Hugging Face Spaces)
        try:
            wake_response = requests.get(base_url, timeout=15)
            print(f"✅ Backend réveillé : {wake_response.status_code}")
        except Exception as wake_exc:
            print(f"⚠️ Réveil backend échoué: {wake_exc}")
        
        # Payload Gradio pour la fonction consulter_madame_t(message, contexte)
        payload = {
            "data": [message, context_text or ""]
        }
        
        # Tester plusieurs endpoints Gradio possibles
        endpoints = [
            "/call/consulter_btn",  # ID du bouton "Consulter"
            "/api/consulter_madame_t", 
            "/api/predict", 
            "/run/predict",
        ]
        
        for endpoint in endpoints:
            try:
                full_url = f"{base_url}{endpoint}"
                print(f"📡 Tentative {endpoint}: {full_url}")
                print(f"📤 Payload: {payload}")
                
                response = requests.post(full_url, json=payload, timeout=60)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 404:
                    print(f"❌ Endpoint {endpoint} non trouvé, passage au suivant...")
                    continue
                
                response.raise_for_status()
                data = response.json()
                print(f"📥 Réponse reçue: {str(data)[:300]}")
                
                # Gradio retourne {"data": [result]}
                if isinstance(data, dict):
                    outputs = data.get("data")
                    if isinstance(outputs, list) and outputs:
                        result = outputs[0]
                        if isinstance(result, str) and result.strip():
                            print(f"✅ Réponse valide de Mme T ({len(result)} caractères)")
                            return result.strip()
                
                print(f"⚠️ Format de réponse inattendu: {type(data)}")
                
            except requests.exceptions.HTTPError as http_err:
                print(f"✗ HTTP Error sur {endpoint}: {http_err}")
                if response.status_code != 404:
                    raise
            except Exception as exc:
                print(f"✗ Erreur sur {endpoint}: {type(exc).__name__}: {exc}")
                if endpoint == endpoints[-1]:  # Dernier essai
                    raise
        
        raise RuntimeError(f"Aucun endpoint Gradio valide trouvé sur {base_url}")
    
    def _extract_space_id(self, url: str) -> str:
        """Extrait l'ID du Space depuis l'URL (ex: Loupy222/mme_t)"""
        if not url:
            return ""
        
        # Format: https://loupy222-mme-t.hf.space -> Loupy222/mme_t
        if ".hf.space" in url:
            domain = url.split("//")[-1].split(".hf.space")[0]
            parts = domain.split("-", 1)
            if len(parts) >= 2:
                owner = parts[0].capitalize()
                space = parts[1].replace("-", "_")
                return f"{owner}/{space}"
        
        # Format direct: Loupy222/mme_t
        if "/" in url and "http" not in url:
            return url.strip()
        
        return ""

    def on_dismiss(self, *_args):
        if self.typewriter_event:
            self.typewriter_event.cancel()
            self.typewriter_event = None
        self._active_bubble = None
        self._typewriter_on_complete = None
        self.chat_bubbles.clear()
        if self._close_reason == "completed" and self.on_session_complete:
            Clock.schedule_once(lambda _dt: self.on_session_complete(), 0)
        self._close_reason = None


class ResponseScreen(Screen):
    """Écran de réponse avec image cliquable"""
    
    def __init__(self, **kwargs):
        super(ResponseScreen, self).__init__(**kwargs)
        
        self.current_card_name = ""
        self.current_card_state = ""
        self.current_card_image_path = "tarot_img/Back.jpg"
        
        self.typewriter_event = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.chat_popup = None

        from kivy.uix.scrollview import ScrollView

        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(15), dp(20), dp(15)],
            spacing=dp(6),
        )
        
        # Background
        with main_layout.canvas.before:
            Color(0.2, 0.1, 0.3, 1)
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
            if os.path.exists("tarot_img/bg.jpg"):
                self.bg.source = "tarot_img/bg.jpg"
                print("Background chargé")
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Nom de la carte
        self.card_name_label = Label(
            text=tr("your_card"),
            font_size="19sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=None,
            height=dp(26),
            bold=True,
            halign='center',
            valign='middle',
        )
        self.card_name_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.card_name_label)
        
        # État
        self.card_state_label = Label(
            text="",
            font_size="15sp",
            color=[0.8, 0.6, 0.4, 1],
            size_hint_y=None,
            height=dp(20),
            bold=True,
            halign='center',
            valign='middle',
        )
        self.card_state_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.card_state_label)
        
        # Mots-clés
        self.keywords_label = Label(
            text="",
            font_size="12sp",
            color=[0.7, 0.7, 0.9, 1],
            size_hint_y=None,
            height=dp(18),
            italic=True,
            halign='center',
            valign='middle',
        )
        self.keywords_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.keywords_label)
        
        # Container image CLIQUABLE (remettre taille originale)
        image_container = FloatLayout(size_hint_y=None, height=dp(160))
        
        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Bouton invisible sur l'image
        self.image_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.8, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.image_button.bind(on_press=self.show_fullscreen_card)
        
        # Indication
        overlay_label = Label(
            text=tr("touch_to_enlarge"),
            font_size="11sp",
            color=[1, 1, 1, 0.7],
            size_hint=(0.8, None),
            height=dp(18),
            pos_hint={'center_x': 0.5, 'bottom': 1},
            halign='center',
            valign='middle',
        )
        overlay_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        
        image_container.add_widget(self.card_image)
        image_container.add_widget(self.image_button)
        image_container.add_widget(overlay_label)
        main_layout.add_widget(image_container)
        
        # Signification avec scroll (occupe l'espace restant)
        scroll = ScrollView(size_hint_y=1)
        self.signification_label = Label(
            text=tr("loading"),
            font_size="15sp",
            color=[1, 1, 1, 1],
            halign='left',
            valign='top',
            size_hint_y=None,
            padding=[dp(10), dp(5)],
        )
        self.signification_label.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val * 0.92, None))
        )
        self.signification_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1] + dp(10))
        )
        scroll.add_widget(self.signification_label)
        main_layout.add_widget(scroll)

        # Conteneur bas pour les boutons (collé en bas)
        bottom_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[0, dp(6), 0, 0],
            spacing=dp(6),
        )
        bottom_container.bind(minimum_height=bottom_container.setter('height'))

        # Bouton premium - achat intégré
        self.premium_btn = Button(
            text=tr("premium_button_base").replace(" Premium", ""),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="12sp",
            bold=True,
            disabled=True,
        )
        with self.premium_btn.canvas.before:
            self.premium_btn_color = Color(0.35, 0.15, 0.55, 1)
            self.premium_btn_bg = RoundedRectangle(
                pos=self.premium_btn.pos,
                size=self.premium_btn.size,
                radius=[20, 20, 20, 20]
            )
        self.premium_btn.opacity = 0.5
        self.premium_btn.bind(on_press=self.purchase_chat_luna)
        self.premium_btn.bind(pos=self.update_premium_btn_canvas, size=self.update_premium_btn_canvas)
        bottom_container.add_widget(self.premium_btn)

        self.premium_status_label = Label(
            text=tr("store_preparing"),
            font_size="9sp",
            color=[0.9, 0.8, 0.95, 1],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            valign='middle',
        )
        self.premium_status_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        bottom_container.add_widget(self.premium_status_label)
        
        # Bouton retour (directement après, encore plus compact)
        self.back_btn = Button(
            text=tr("new_reading"),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="14sp",
            bold=True
        )
        
        with self.back_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.back_btn_bg = RoundedRectangle(
                pos=self.back_btn.pos,
                size=self.back_btn.size,
                radius=[20, 20, 20, 20]
            )
        
        self.back_btn.bind(pos=self.update_back_btn_canvas, size=self.update_back_btn_canvas)
        self.back_btn.bind(on_press=self.go_back)
        bottom_container.add_widget(self.back_btn)

        # Ajouter le conteneur bas en toute fin pour qu'il reste en bas
        main_layout.add_widget(bottom_container)
        
        # Bannière pub (cachée par défaut)
        self.ad_banner = Label(
            text=tr("crystals_ad"),  # ou une autre pub de ton choix
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        main_layout.add_widget(self.ad_banner)
        
        self.add_widget(main_layout)
    
    def show_fullscreen_card(self, instance):
        """NOUVELLE FONCTIONNALITÉ: Affiche la carte en plein écran"""
        print(f"Affichage plein écran: {self.current_card_name}")
        
        # Animation click
        click_anim = Animation(opacity=0.7, duration=0.1)
        click_anim += Animation(opacity=1, duration=0.1)
        click_anim.start(self.card_image)
        
        # Popup plein écran
        fullscreen_popup = FullScreenCardPopup(
            card_image_source=self.current_card_image_path or self.card_image.source,
            card_name=self.current_card_name,
            card_state=self.card_state_label.text
        )
        fullscreen_popup.open()
    
    def setup_card(self, card_name, state):
        print(f"=== SETUP CARTE: {card_name} - {state} ===")
        
        # Sauvegarder pour le plein écran
        self.current_card_name = card_name
        self.current_card_state = state
        
        # Convertir le nom selon la langue détectée
        display_card_name = get_card_name_for_lang(card_name, CURRENT_LANG)
        print(f"Nom affiché: {display_card_name}")
        
        # Nom affiché
        self.card_name_label.text = display_card_name
        
        # État traduit avec conversion pour l'anglais
        if state == "a l'envers":
            self.card_state_label.text = tr("reversed")
            lookup_state = "reversed"
        else:
            self.card_state_label.text = tr("upright") 
            lookup_state = "upright"
        
        # Image (garder le nom français pour les fichiers)
        try:
            image_path = get_card_image_path(card_name, state)
            self.current_card_image_path = image_path
            self.card_image.source = image_path
            self.card_image.reload()
            if os.path.exists(image_path):
                print(f"✓ Image chargée: {image_path}")
            else:
                print(f"✗ Image non trouvée (fallback utilisé): {image_path}")
        except Exception as e:
            print(f"✗ Erreur image: {e}")
            self.current_card_image_path = "tarot_img/Back.jpg"
            self.card_image.source = self.current_card_image_path
            self.card_image.reload()
        
        # Signification avec le bon nom de carte selon la langue
        try:
            cards_signification = get_cards_signification()
            lookup_name = display_card_name if CURRENT_LANG == "en" else card_name
            print(f"Recherche signification pour: {lookup_name}")
            
            if lookup_name in cards_signification:
                card_data = cards_signification[lookup_name]
                print(f"Clés disponibles: {list(card_data.keys())}")
                
                key_bundle = SIGNIFICATION_KEY_MAP.get(
                    CURRENT_LANG, SIGNIFICATION_KEY_MAP["en"]
                )
                keyword_key = key_bundle["keywords"].get(lookup_state)
                detail_key = key_bundle["detail"].get(lookup_state)

                if keyword_key and keyword_key in card_data:
                    self.keywords_label.text = f"💫 {card_data[keyword_key].upper()} 💫"

                if detail_key and detail_key in card_data:
                    signification = str(card_data[detail_key])
                    self.start_typewriter(signification)
                    print(f"✓ Signification trouvée avec clé: {detail_key}")
                elif keyword_key and keyword_key in card_data:
                    self.start_typewriter(card_data[keyword_key])
                else:
                    self.start_typewriter("No description available")
                
                Clock.schedule_once(self.setup_text_wrapping, 0.1)
            else:
                self.signification_label.text = f"Card '{lookup_name}' not found"
                print(f"✗ Carte '{lookup_name}' non trouvée dans: {list(cards_signification.keys())[:5]}...")
                
        except Exception as e:
            print(f"✗ Erreur signification: {e}")
            self.signification_label.text = tr("signification_error")
    
    def setup_text_wrapping(self, dt):
        if self.signification_label and self.parent:
            self.signification_label.text_size = (self.width * 0.9, None)
            self.signification_label.height = self.signification_label.texture_size[1]
    
    def update_back_btn_canvas(self, instance, value):
        if hasattr(self, "back_btn_bg"):
            self.back_btn_bg.pos = instance.pos
            self.back_btn_bg.size = instance.size

    def update_premium_btn_canvas(self, instance, value):
        if hasattr(self, "premium_btn_bg"):
            self.premium_btn_bg.pos = instance.pos
            self.premium_btn_bg.size = instance.size
    
    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def go_back(self, instance):
        if self.manager:
            self.manager.current = "main_screen"

    def purchase_chat_luna(self, *_args):
        app = App.get_running_app()
        billing = getattr(app, "billing", None)
        if not billing:
            self.show_purchase_error(tr("store_unavailable_platform"))
            return
        if not billing.is_ready():
            self.show_purchase_error(tr("store_preparing_retry"))
            return
        billing.start_premium_purchase()

    def update_premium_button(self, available, price_text, mode):
        provider_key_map = {
            "google": "provider_google",
            "amazon": "provider_amazon",
            "simulation": "provider_simulation",
            "disabled": "provider_disabled",
        }
        provider_key = provider_key_map.get(mode)
        provider_label = tr(provider_key) if provider_key else ""

        # Texte court pour éviter le débordement
        button_text = tr("chat_mme_t")
        if price_text:
            button_text += f" ({price_text})"

        self.premium_btn.text = button_text
        self.premium_btn.disabled = not available
        self.premium_btn.opacity = 1 if available else 0.5
        if hasattr(self, "premium_btn_color"):
            active_color = (0.45, 0.25, 0.65, 1)
            inactive_color = (0.25, 0.15, 0.35, 1)
            self.premium_btn_color.rgba = active_color if available else inactive_color

        if available:
            self.premium_status_label.text = ""
            self.premium_status_label.opacity = 0
            self.premium_status_label.height = 0
        else:
            self.premium_status_label.opacity = 1
            self.premium_status_label.height = dp(20)
            if mode in ("disabled", "simulation") and platform != "android":
                self.premium_status_label.text = tr("store_mobile_only")
            else:
                self.premium_status_label.text = tr("store_preparing")

    def show_purchase_success(self, provider="google", price_text=None):
        if not MME_T_BACKEND_URL:
            provider_label = tr("provider_google") if provider == "google" else tr("provider_amazon") if provider == "amazon" else ""
            message = tr("thanks_for_support")
            if provider_label:
                message = tr("thanks_for_support_via", provider=provider_label)
            message += "\n" + tr("configure_backend_hint")
            self._open_purchase_popup(tr("thanks_title"), message)
            return

        self.open_mme_t_chat(provider=provider, price_text=price_text)

    def show_purchase_error(self, message):
        self._open_purchase_popup(tr("purchase_error_title"), message)

    def open_mme_t_chat(self, provider="google", price_text=None):
        if self.chat_popup and self.chat_popup.parent:
            self.chat_popup.dismiss()
        self.chat_popup = MmeTChatPopup(
            language=CURRENT_LANG,
            provider=provider,
            price_text=price_text,
            context_text=self._build_mme_t_context(),
            on_session_complete=self._on_chat_complete,
        )
        self.chat_popup.bind(on_dismiss=lambda *_: setattr(self, "chat_popup", None))
        self.chat_popup.open()

    def _build_mme_t_context(self):
        parts = []
        card_title = (self.card_name_label.text or "").strip()
        if card_title:
            parts.append(f"Carte principale: {card_title}")
        card_state = (self.card_state_label.text or "").strip()
        if card_state:
            parts.append(f"Position: {card_state}")
        keywords = (self.keywords_label.text or "").strip()
        if keywords:
            clean_keywords = keywords.replace("💫", "").strip()
            if clean_keywords:
                parts.append(f"Mots-cles: {clean_keywords}")
        return " | ".join(parts)

    def _on_chat_complete(self):
        if not self.manager:
            return
        def _switch(_dt):
            self.manager.current = "main_screen"
        Clock.schedule_once(_switch, 0)

    def _open_purchase_popup(self, title, message):
        popup_layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        popup_label = Label(
            text=message,
            color=[1, 1, 1, 1],
            halign="center",
            valign="middle",
        )
        popup_label.bind(
            size=lambda inst, val: setattr(inst, "text_size", val)
        )
        close_btn = Button(
            text="Fermer",
            size_hint_y=None,
            height=40,
            background_normal='',
            background_color=[0.6, 0.3, 0.3, 1],
            color=[1, 1, 1, 1],
        )
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_btn.bind(on_release=popup.dismiss)
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_btn)
        popup.open()
    
    def show_ad_banner(self):
        self.ad_banner.opacity = 1

    def hide_ad_banner(self):
        self.ad_banner.opacity = 0
    
    def on_enter(self, *args):
        """Afficher la bannière AdMob quand on entre sur cet écran"""
        super().on_enter(*args)
        print("📱 ResponseScreen: on_enter - Affichage bannière AdMob")
        
        app = App.get_running_app()
        if hasattr(app, 'ads') and hasattr(app.ads, 'show_banner'):
            app.ads.show_banner()
    
    def on_leave(self, *args):
        """Masquer la bannière AdMob quand on quitte cet écran"""
        super().on_leave(*args)
        print("📱 ResponseScreen: on_leave - Masquage bannière AdMob")
        
        app = App.get_running_app()
        if hasattr(app, 'ads') and hasattr(app.ads, 'hide_banner'):
            app.ads.hide_banner()

    def start_typewriter(self, text, speed=0.02):
        """Affiche le texte lettre par lettre (effet machine à écrire)"""
        if self.typewriter_event:
            self.typewriter_event.cancel()
        self.typewriter_full_text = text
        self.typewriter_index = 0
        self.signification_label.text = ""
        self.typewriter_event = Clock.schedule_interval(lambda dt: self.typewriter_step(speed), speed)

    def typewriter_step(self, speed):
        if self.typewriter_index < len(self.typewriter_full_text):
            self.signification_label.text += self.typewriter_full_text[self.typewriter_index]
            self.typewriter_index += 1
            # Scroll automatique si besoin
            if self.signification_label.parent:
                self.signification_label.parent.scroll_y = 1
        else:
            if self.typewriter_event:
                self.typewriter_event.cancel()
            return False  # Stop le schedule


class AdsPopup(Popup):
    def __init__(self, on_close_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.size_hint = (1, 1)  # Plein écran
        self.auto_dismiss = False
        self.separator_height = 0
        self.on_close_callback = on_close_callback

        layout = BoxLayout(orientation="vertical", spacing=dp(20), padding=dp(30))
        
        # Fond sombre pour publicité
        with layout.canvas.before:
            Color(0.12, 0.08, 0.18, 0.98)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda i, v: setattr(self.bg_rect, 'pos', v), size=lambda i, v: setattr(self.bg_rect, 'size', v))

        # Bandeau promotion traduit
        ad_choices = [
            tr("crystals_ad"),
            tr("love_ad"),
            tr("tarot_course_ad"),
        ]
        chosen_ad = random.choice(ad_choices)

        promo = Label(
            text=chosen_ad,
            font_size="22sp",
            color=[1, 0.88, 0.4, 1],
            halign="center",
            valign="middle",
            size_hint=(1, 0.5),
            bold=True,
        )
        promo.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val * 0.85, None))
        )
        layout.add_widget(promo)

        self.countdown_seconds = 30
        btn_text = tr("new_reading_countdown", seconds=self.countdown_seconds)
        self.next_btn = Button(
            text=btn_text,
            size_hint=(0.75, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="17sp",
            bold=True,
            disabled=True
        )
        with self.next_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.btn_bg = RoundedRectangle(
                pos=self.next_btn.pos,
                size=self.next_btn.size,
                radius=[25, 25, 25, 25]
            )
        self.next_btn.bind(pos=self.update_btn_canvas, size=self.update_btn_canvas)
        self.next_btn.bind(on_press=self.close_popup)
        layout.add_widget(self.next_btn)

        self.content = layout
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

    def update_btn_canvas(self, instance, value):
        self.btn_bg.pos = instance.pos
        self.btn_bg.size = instance.size

    def update_countdown(self, dt):
        self.countdown_seconds -= 1
        if self.countdown_seconds > 0:
            self.next_btn.text = tr("new_reading_countdown", seconds=self.countdown_seconds)
        else:
            self.next_btn.text = tr("new_reading")
            self.next_btn.disabled = False
            if self.countdown_event:
                self.countdown_event.cancel()

    def close_popup(self, instance):
        self.dismiss()
        if self.on_close_callback:
            self.on_close_callback()


class TarotApp(App):
    def build(self):
        print("=== CONSTRUCTION APP TAROT ===")
        self.title = tr("app_title")
        
        # Initialisation AdMob avec configuration JSON
        print("📱 Chargement configuration AdMob...")
        self.cfg = load_config()
        print(f"   → Mode test: {self.cfg.get('ads_test_mode')}")
        print(f"   → Pubs activées: {self.cfg.get('ads_enabled')}")
        print(f"   → Fréquence: {self.cfg.get('ads_frequency')} tirages")
        
        # Optionnel : récupérer config à distance
        maybe_fetch_remote_config(self.cfg)
        
        # Initialiser le gestionnaire de publicités
        self.ads = AdsManager(self.cfg)
        print("✅ AdMob initialisé")
        
        sm = RootScreen()
        sm.add_widget(CardScreen(name="main_screen"))
        sm.add_widget(ResponseScreen(name="response_screen"))
        sm.current = "main_screen"
        self.screen_manager = sm

        self.billing = InAppPurchaseManager(
            on_success=self.on_purchase_success,
            on_error=self.on_purchase_error,
        )
        self.billing.add_state_listener(self.on_billing_state_change)
        self.billing.initialize()
        
        return sm
    
    def on_start(self):
        print("=== APP TAROT DÉMARRÉE ===")

    def _get_response_screen(self):
        if hasattr(self, "screen_manager") and self.screen_manager and self.screen_manager.has_screen("response_screen"):
            return self.screen_manager.get_screen("response_screen")
        return None

    def on_billing_state_change(self, is_ready, price_text, mode):
        screen = self._get_response_screen()
        if screen:
            screen.update_premium_button(is_ready, price_text, mode)

    def on_purchase_success(self, provider="google"):
        screen = self._get_response_screen()
        if screen:
            screen.show_purchase_success(provider)

    def on_purchase_error(self, message, provider="google"):
        screen = self._get_response_screen()
        if screen:
            screen.show_purchase_error(message)


if __name__ == "__main__":
    TarotApp().run()