# -*- coding: utf-8 -*-
"""
Module de facturation pour l'application Kivy.
Contient les classes de gestion des achats Google Play et Amazon IAP.
"""

from __future__ import annotations

# JNI / Android (pyjnius) — optional with robust fallback
PYJNIUS_AVAILABLE = True
try:
    from jnius import (
        autoclass,
        cast,
        JavaException,
        PythonJavaClass,
        java_method,
    )
    try:
        from android.runnable import run_on_ui_thread  # type: ignore
        from android import activity
    except Exception:
        def run_on_ui_thread(func):
            return func
        activity = None
except Exception:
    PYJNIUS_AVAILABLE = False
    autoclass = None
    def cast(cls, obj):
        return obj
    JavaException = Exception

    class PythonJavaClass:
        pass

    def java_method(signature):
        def decorator(func):
            return func

        return decorator

    def run_on_ui_thread(func):
        return func
    activity = None


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
                # parcourir toutes les purchases
                for idx in range(purchases.size()):
                    p = purchases.get(idx)
                    # nouvel API : getProducts() sinon fallback getSkus()
                    product_ids = []
                    try:
                        plist = p.getProducts()
                        for j in range(plist.size()):
                            product_ids.append(plist.get(j))
                    except Exception:
                        try:
                            sl = p.getSkus()
                            for j in range(sl.size()):
                                product_ids.append(sl.get(j))
                        except Exception:
                            pass

                    print(f"✅ Achat Google confirmé pour {product_ids}")

                    # Vérifier l'état et ack si nécessaire
                    try:
                        PURCHASED = autoclass('com.android.billingclient.api.Purchase$PurchaseState').PURCHASED
                        if p.getPurchaseState() == PURCHASED:
                            if not p.isAcknowledged():
                                AcknowledgePurchaseParams_Builder = autoclass('com.android.billingclient.api.AcknowledgePurchaseParams$Builder')
                                ack_params = AcknowledgePurchaseParams_Builder()\
                                    .setPurchaseToken(p.getPurchaseToken())\
                                    .build()

                                class AckListener(PythonJavaClass):
                                    __javainterfaces__ = ['com/android/billingclient/api/AcknowledgePurchaseResponseListener']
                                    __javacontext__ = 'app'

                                    @java_method('(Lcom/android/billingclient/api/BillingResult;)V')
                                    def onAcknowledgePurchaseResponse(self, br):
                                        try:
                                            rc = br.getResponseCode()
                                            print(f"🔔 Acknowledge response: {rc}")
                                        except Exception:
                                            pass

                                try:
                                    self.manager.google_billing_client.acknowledgePurchase(ack_params, AckListener())
                                except Exception as exc:
                                    print(f"✗ Erreur ack purchase: {exc}")
                    except Exception as exc:
                        print(f"⚠️ Erreur traitement purchase state: {exc}")

                # notifier succès global
                # Collecter tous les product_ids des achats réussis
                all_product_ids = []
                for idx in range(purchases.size()):
                    p = purchases.get(idx)
                    try:
                        plist = p.getProducts()
                        for j in range(plist.size()):
                            all_product_ids.append(plist.get(j))
                    except Exception:
                        try:
                            sl = p.getSkus()
                            for j in range(sl.size()):
                                all_product_ids.append(sl.get(j))
                        except Exception:
                            pass
                
                self.manager._notify_success("google", all_product_ids)
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
                print(f"⚠️ Achat Google échoué - code: {response_code}")
                self.manager._notify_error(
                    f"Erreur achat (code {response_code})", provider="google"
                )
        except Exception as exc:  # pragma: no cover - Android only
            print(f"✗ Exception traitement achat Google: {exc}")
            self.manager._notify_error(
                "Erreur inattendue lors de l'achat", provider="google"
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


class GoogleProductDetailsListener(PythonJavaClass):
    """Réception asynchrone des ProductDetails (Google Play Billing v8+)."""

    __javacontext__ = "app"
    __javainterfaces__ = [
        "com/android/billingclient/api/ProductDetailsResponseListener",
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V")
    def onProductDetailsResponse(self, billing_result, product_details_list):
        try:
            response_code = billing_result.getResponseCode()
            if (
                self.manager.google_client_class
                and response_code
                == self.manager.google_client_class.BillingResponseCode.OK
                and product_details_list
                and product_details_list.size() > 0
            ):
                details = product_details_list.get(0)
                # Pour produits one-time (INAPP), récupère le prix formaté si disponible
                price_text = None
                try:
                    otp = details.getOneTimePurchaseOfferDetails()
                    if otp:
                        price_text = otp.getFormattedPrice()
                except Exception:
                    price_text = None

                self.manager.google_product_details = details
                if price_text:
                    self.manager.display_price = price_text
                print("✅ ProductDetails Google récupérés: %s" % getattr(self.manager, 'display_price', ''))
                self.manager._dispatch_state_change()
            else:
                print(f"⚠️ ProductDetails indisponibles (code {response_code})")
                self.manager.google_product_details = None
                self.manager._notify_error("Produit indisponible sur Play Store", provider="google")
        except Exception as exc:
            print(f"✗ Exception lecture ProductDetails Google: {exc}")
            self.manager._notify_error("Erreur produit sur Play Store", provider="google")


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
    __javainterfaces__ = [
        "com/amazon/device/iap/PurchasingListener",
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/amazon/device/iap/model/PurchaseResponse;)V")
    def onPurchaseResponse(self, purchase_response):
        try:
            response_status = purchase_response.getRequestStatus()
            if (
                self.manager.amazon_service
                and response_status
                == self.manager.request_status_class.SUCCESSFUL
            ):
                receipt = purchase_response.getReceipt()
                if receipt:
                    product_id = receipt.getSku()
                    print(f"✅ Achat Amazon confirmé pour {product_id}")

                    # Traiter l'achat Amazon
                    try:
                        # Vérifier si c'est un achat consommable
                        if receipt.getProductType() == self.manager.amazon_service.getProductType().CONSUMABLE:
                            # Consommer l'achat
                            self.manager.amazon_service.notifyFulfillment(
                                receipt.getReceiptId(),
                                self.manager.amazon_service.getFulfillmentResult().FULFILLED
                            )
                    except Exception as exc:
                        print(f"⚠️ Erreur traitement achat Amazon: {exc}")

                    self.manager._notify_success("amazon", [product_id])
                else:
                    print("⚠️ Achat Amazon sans receipt")
                    self.manager._notify_error("Achat Amazon invalide", provider="amazon")
            elif (
                self.manager.amazon_service
                and response_status
                == self.manager.service.getRequestStatus().ALREADY_PURCHASED
            ):
                print("ℹ️ Produit Amazon déjà acheté")
                self.manager._notify_error(
                    "Produit déjà acheté", provider="amazon", warn_only=True
                )
            else:
                print(f"⚠️ Achat Amazon échoué - status: {response_status}")
                self.manager._notify_error(
                    f"Erreur achat Amazon (status {response_status})", provider="amazon"
                )
        except Exception as exc:
            print(f"✗ Exception traitement achat Amazon: {exc}")
            self.manager._notify_error(
                "Erreur inattendue lors de l'achat Amazon", provider="amazon"
            )

    @java_method("(Lcom/amazon/device/iap/model/ProductDataResponse;)V")
    def onProductDataResponse(self, product_data_response):
        try:
            response_status = product_data_response.getRequestStatus()
            if (
                self.manager.amazon_service
                and response_status
                == self.manager.request_status_class.SUCCESSFUL
            ):
                product_data = product_data_response.getProductData()
                if product_data and product_data.size() > 0:
                    # Prendre le premier produit
                    product = product_data.values().iterator().next()
                    if product:
                        price = product.getPrice()
                        self.manager.amazon_product_data = product
                        if price:
                            self.manager.display_price = price
                        print("✅ ProductData Amazon récupérés: %s" % getattr(self.manager, 'display_price', ''))
                        self.manager._dispatch_state_change()
                else:
                    print("⚠️ ProductData Amazon vides")
                    self.manager.amazon_product_data = None
                    self.manager._notify_error("Produit indisponible sur Amazon", provider="amazon")
            else:
                print(f"⚠️ ProductData Amazon indisponibles (status {response_status})")
                self.manager.amazon_product_data = None
                self.manager._notify_error("Erreur produit Amazon", provider="amazon")
        except Exception as exc:
            print(f"✗ Exception lecture ProductData Amazon: {exc}")
            self.manager._notify_error("Erreur produit Amazon", provider="amazon")

    @java_method("(Lcom/amazon/device/iap/model/UserDataResponse;)V")
    def onUserDataResponse(self, user_data_response):
        try:
            response_status = user_data_response.getRequestStatus()
            if (
                self.manager.amazon_service
                and response_status
                == self.manager.request_status_class.SUCCESSFUL
            ):
                user_data = user_data_response.getUserData()
                if user_data:
                    user_id = user_data.getUserId()
                    marketplace = user_data.getMarketplace()
                    print(f"✅ UserData Amazon: user_id={user_id}, marketplace={marketplace}")
                    self.manager.amazon_user_data = user_data
                    self.manager._dispatch_state_change()
                else:
                    print("⚠️ UserData Amazon vides")
                    self.manager.amazon_user_data = None
            else:
                print(f"⚠️ UserData Amazon indisponibles (status {response_status})")
                self.manager.amazon_user_data = None
        except Exception as exc:
            print(f"✗ Exception lecture UserData Amazon: {exc}")


class InAppPurchaseManager:
    """Gestionnaire centralisé des achats in-app (Google Play et Amazon)."""

    def __init__(self):
        self.billing_ready = False
        self.google_billing_client = None
        self.google_client_class = None
        self.google_product_details = None
        self.amazon_service = None
        self.amazon_product_data = None
        self.amazon_user_data = None
        self.request_status_class = None
        self.display_price = None
        self.activity = None
        self.listeners = []

        # Initialiser les services selon la plateforme
        self._init_billing_services()

    def _init_billing_services(self):
        """Initialise les services de facturation selon la plateforme détectée."""
        if not PYJNIUS_AVAILABLE:
            print("ℹ️ PyJNIUS non disponible - mode desktop simulé")
            # En mode desktop, considérer comme prêt immédiatement avec simulation
            self.billing_ready = True
            self._dispatch_state_change()
            return

        try:
            # Détection de la plateforme
            from jnius import autoclass as jnius_autoclass
            Build = jnius_autoclass('android.os.Build')
            manufacturer = Build.MANUFACTURER.lower()

            if 'amazon' in manufacturer:
                # Amazon Fire TV/Tablets
                self._init_amazon_billing()
            else:
                # Google Play (Android standard)
                self._init_google_billing()

        except Exception as exc:
            print(f"⚠️ Erreur initialisation billing: {exc}")

    def _init_google_billing(self):
        """Initialise Google Play Billing."""
        try:
            from jnius import autoclass
            # Use PythonActivity.mActivity as the Android Context (safer than passing the android.activity module)
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                ctx = getattr(PythonActivity, 'mActivity', None)
            except Exception:
                ctx = None

            # Fallback: try to import android.activity if ctx not available
            if ctx is None:
                try:
                    from android import activity as _activity_module
                    ctx = _activity_module
                except Exception:
                    ctx = None

            if ctx is None:
                raise RuntimeError('No Android Context available for Billing initialization')

            self.activity = ctx
            self.google_client_class = autoclass('com.android.billingclient.api.BillingClient')
            self.google_billing_client = None

            # Créer le client de facturation
            # Some BillingClient versions provide enablePendingPurchases as a
            # static/class method that must be called on the BillingClient class
            # (not on the builder instance). Call the class method if present
            # to avoid Java signature mismatch errors.
            builder = self.google_client_class.newBuilder(ctx)
            builder.setListener(GooglePurchasesUpdatedListener(self))


            # Appel obligatoire sur l’instance builder pour BillingClient v8
            builder.enablePendingPurchases()
            self.google_billing_client = builder.build()

            # Se connecter au service
            self.google_billing_client.startConnection(GoogleBillingStateListener(self))

        except Exception as exc:
            print(f"✗ Erreur initialisation Google Billing: {exc}")

    def _init_amazon_billing(self):
        """Initialise Amazon In-App Purchasing."""
        try:
            from jnius import autoclass

            self.amazon_service = autoclass('com.amazon.device.iap.PurchasingService')
            self.request_status_class = autoclass(
                "com.amazon.device.iap.model.PurchaseResponse$RequestStatus"
            )

            # Enregistrer le listener
            listener = AmazonPurchasingListener(self)
            self.amazon_service.registerListener(activity.getApplicationContext(), listener)
            self.listeners.append(listener)

            # Amazon IAP est prêt immédiatement après l'enregistrement
            self.billing_ready = True
            self._dispatch_state_change()
            print("✅ Amazon IAP initialisé et prêt")

        except Exception as exc:
            print(f"✗ Erreur initialisation Amazon IAP: {exc}")

    def _on_google_billing_ready(self):
        """Appelé quand Google Billing est prêt."""
        self.billing_ready = True
        self._dispatch_state_change()

        # Récupérer les détails du produit
        try:
            from jnius import autoclass
            QueryProductDetailsParams_Builder = autoclass('com.android.billingclient.api.QueryProductDetailsParams$Builder')

            # Créer la liste des produits à interroger
            product_list = []
            product_builder = autoclass('com.android.billingclient.api.QueryProductDetailsParams$Product$Builder')
            product = product_builder.newBuilder()\
                .setProductId("premium_features")\
                .setProductType(self.google_client_class.ProductType.INAPP)\
                .build()
            product_list.append(product)

            params = QueryProductDetailsParams_Builder.newBuilder()\
                .setProductList(product_list)\
                .build()

            self.google_billing_client.queryProductDetailsAsync(
                params,
                GoogleProductDetailsListener(self)
            )

        except Exception as exc:
            print(f"⚠️ Erreur requête ProductDetails: {exc}")

    def is_ready(self):
        """Retourne True si le système de facturation est prêt."""
        return self.billing_ready

    def _dispatch_state_change(self):
        """Dispatch a safe state-change notification to any registered listeners.

        Many parts of the app call this method; on desktop we simply notify
        listener objects if they expose a callback. This avoids AttributeError
        when the Android billing stack is not present.
        """
        try:
            for listener in getattr(self, "listeners", []):
                try:
                    # Preferred hook name (if UI register this)
                    if hasattr(listener, "on_billing_state_change"):
                        listener.on_billing_state_change()
                    # Generic callable listener support
                    elif callable(listener):
                        listener()
                except Exception:
                    # Do not fail the whole flow for one bad listener
                    continue
        except Exception:
            pass

    def _notify_success(self, provider, product_ids=None):
        """Notifie un achat réussi."""
        print(f"✅ Achat {provider} réussi")
        
        # Appeler le callback de succès de l'app pour chaque produit acheté
        if product_ids:
            try:
                from kivy.app import App
                app = App.get_running_app()
                if app:
                    for product_id in product_ids:
                        app.on_purchase_success(product_id, provider)
            except Exception as e:
                print(f"❌ Erreur appel on_purchase_success: {e}")
        else:
            print("⚠️ Aucun product_id fourni pour la notification de succès")

    def _notify_error(self, message, provider, warn_only=False):
        """Notifie une erreur d'achat."""
        level = "⚠️" if warn_only else "❌"
        print(f"{level} Erreur {provider}: {message}")

    def purchase_product(self, product_id):
        """Lance le processus d'achat pour un produit."""
        if not self.billing_ready:
            self._notify_error("Service de paiement non prêt", "system")
            return

        try:
            if self.google_billing_client:
                # Google Play
                self._launch_google_purchase(product_id)
            elif self.amazon_service:
                # Amazon
                self._launch_amazon_purchase(product_id)
            else:
                self._notify_error("Aucun service de paiement disponible", "system")

        except Exception as exc:
            print(f"✗ Exception lancement achat: {exc}")
            self._notify_error("Erreur lancement achat", "system")

    def _launch_google_purchase(self, product_id):
        """Lance un achat Google Play."""
        try:
            from jnius import autoclass

            if not self.google_product_details:
                self._notify_error("Détails produit non disponibles", "google")
                return

            # Créer les paramètres d'achat
            BillingFlowParams_Builder = autoclass('com.android.billingclient.api.BillingFlowParams$Builder')
            params = BillingFlowParams_Builder.newBuilder()\
                .setProductDetails(self.google_product_details)\
                .build()

            # Lancer sur le thread UI
            runnable = LaunchBillingRunnable(self, params)
            from android.runnable import run_on_ui_thread
            run_on_ui_thread(runnable.run)()

        except Exception as exc:
            print(f"✗ Exception achat Google: {exc}")
            self._notify_error("Erreur achat Google", "google")

    def _launch_amazon_purchase(self, product_id):
        """Lance un achat Amazon."""
        try:
            # Demander l'achat
            self.amazon_service.purchase(product_id)
        except Exception as exc:
            print(f"✗ Exception achat Amazon: {exc}")
            self._notify_error("Erreur achat Amazon", "amazon")

    def get_product_price(self):
        """Retourne le prix formaté du produit."""
        return self.display_price or "Prix non disponible"