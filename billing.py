# -*- coding: utf-8 -*-
"""
billing.py — Gestion in-app pour Kivy (Google Play v8 + option Amazon IAP)

✔ Google Play Billing v8:
   - queryProductDetailsAsync avec ArrayList Java
   - launchBillingFlow via setProductDetailsParamsList([...])
   - Ack automatique + restauration des achats
✔ Fallback desktop (PyJNIUS absent) : mode simulé
✔ Appel automatique App.on_purchase_success(product_id, provider)

ATTENTES CÔTÉ APP:
- Définis un produit INAPP "premium_features" dans la Play Console.
- Dans ton App, implémente:
    def on_purchase_success(self, product_id, provider):
        if product_id == "premium_features":
            self.enable_premium = True
            # persiste le statut si nécessaire
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# JNI / Android (pyjnius) — optional with robust fallback
# ──────────────────────────────────────────────────────────────────────────────
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
    autoclass = None  # type: ignore

    def cast(cls, obj):  # type: ignore
        return obj

    JavaException = Exception  # type: ignore

    class PythonJavaClass:  # type: ignore
        pass

    def java_method(signature):  # type: ignore
        def decorator(func):
            return func
        return decorator

    def run_on_ui_thread(func):  # type: ignore
        return func

    activity = None  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
# LISTENERS GOOGLE
# ──────────────────────────────────────────────────────────────────────────────
class GooglePurchasesUpdatedListener(PythonJavaClass):  # pragma: no cover - Android only
    """Gestion des retours d'achats Google Play Billing."""
    __javacontext__ = "app"
    __javainterfaces__ = ["com/android/billingclient/api/PurchasesUpdatedListener"]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V")
    def onPurchasesUpdated(self, billing_result, purchases):
        try:
            response_code = billing_result.getResponseCode()
            OK = self.manager.google_client_class.BillingResponseCode.OK
            USER_CANCELED = self.manager.google_client_class.BillingResponseCode.USER_CANCELED

            if response_code == OK and purchases and purchases.size() > 0:
                all_product_ids = []
                for i in range(purchases.size()):
                    p = purchases.get(i)
                    product_ids = self.manager._extract_purchase_ids(p)
                    print(f"✅ Achat Google confirmé pour {product_ids}")
                    all_product_ids.extend(product_ids)
                    self.manager._ack_purchase_if_needed(p, context="purchase")
                self.manager._notify_success("google", all_product_ids)

            elif response_code == USER_CANCELED:
                print("ℹ️ Achat Google annulé par l'utilisateur")
                self.manager._notify_error(
                    "Achat annulé", provider="google", warn_only=True
                )
            else:
                print(f"⚠️ Achat Google échoué - code: {response_code}")
                self.manager._notify_error(
                    f"Erreur achat (code {response_code})", provider="google"
                )

        except Exception as exc:  # pragma: no cover
            print(f"✗ Exception traitement achat Google: {exc}")
            self.manager._notify_error(
                "Erreur inattendue lors de l'achat", provider="google"
            )


class GoogleBillingStateListener(PythonJavaClass):  # pragma: no cover
    """Réception de l'état de connexion au service de facturation Google."""
    __javacontext__ = "app"
    __javainterfaces__ = ["com/android/billingclient/api/BillingClientStateListener"]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/android/billingclient/api/BillingResult;)V")
    def onBillingSetupFinished(self, billing_result):
        try:
            rc = billing_result.getResponseCode()
            OK = self.manager.google_client_class.BillingResponseCode.OK
            if rc == OK:
                print("✅ Connexion Billing Google établie")
                self.manager._on_google_billing_ready()
            else:
                print(f"⚠️ Connexion Billing Google interrompue (code {rc})")
                self.manager._notify_error(
                    "Service de paiement indisponible", provider="google"
                )
        except Exception as exc:
            print(f"✗ Exception connexion Billing Google: {exc}")
            self.manager._notify_error("Erreur Billing Google", provider="google")

    @java_method("()V")
    def onBillingServiceDisconnected(self):
        print("⚠️ Service Billing Google déconnecté")
        self.manager.billing_ready = False
        self.manager._dispatch_state_change()
        # Tentative de reconnexion avec backoff exponentiel (limité)
        try:
            self.manager._schedule_google_reconnect()
        except Exception:
            pass


class GoogleProductDetailsListener(PythonJavaClass):
    """Réception asynchrone des ProductDetails (Google Play Billing v8+)."""
    __javacontext__ = "app"
    __javainterfaces__ = [
        "com/android/billingclient/api/ProductDetailsResponseListener"
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V")
    def onProductDetailsResponse(self, billing_result, product_details_list):
        try:
            rc = billing_result.getResponseCode()
            OK = self.manager.google_client_class.BillingResponseCode.OK
            if rc == OK and product_details_list and product_details_list.size() > 0:
                details = product_details_list.get(0)
                self.manager.google_product_details = details

                # Prix formaté si INAPP (one-time)
                try:
                    otp = details.getOneTimePurchaseOfferDetails()
                    if otp:
                        self.manager.display_price = otp.getFormattedPrice()
                except Exception:
                    pass

                print("✅ ProductDetails Google récupérés:", getattr(self.manager, "display_price", ""))
                self.manager._dispatch_state_change()
            else:
                print(f"⚠️ ProductDetails indisponibles (code {rc})")
                self.manager.google_product_details = None
                self.manager._notify_error(
                    "Produit indisponible sur Play Store", provider="google"
                )
        except Exception as exc:
            print(f"✗ Exception lecture ProductDetails Google: {exc}")
            self.manager._notify_error(
                "Erreur produit sur Play Store", provider="google"
            )


class GooglePurchasesResponseListener(PythonJavaClass):  # pragma: no cover
    """Listener pour queryPurchasesAsync (restauration)."""
    __javacontext__ = "app"
    __javainterfaces__ = [
        "com/android/billingclient/api/PurchasesResponseListener"
    ]

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @java_method("(Lcom/android/billingclient/api/BillingResult;Ljava/util/List;)V")
    def onQueryPurchasesResponse(self, billing_result, purchases_list):
        try:
            rc = billing_result.getResponseCode()
            OK = self.manager.google_client_class.BillingResponseCode.OK
            if rc == OK and purchases_list and purchases_list.size() > 0:
                restored_ids = []
                for i in range(purchases_list.size()):
                    p = purchases_list.get(i)
                    product_ids = self.manager._extract_purchase_ids(p)
                    self.manager._ack_purchase_if_needed(p, context="restore")
                    restored_ids.extend(product_ids)

                if restored_ids:
                    print(f"♻️ Restaurations détectées: {restored_ids}")
                    self.manager._notify_success("google", restored_ids)
            else:
                print("ℹ️ Pas d’achats à restaurer")
        except Exception as exc:
            print(f"✗ Exception restore purchases: {exc}")


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


# ──────────────────────────────────────────────────────────────────────────────
# LISTENER AMAZON (optionnel)
# ──────────────────────────────────────────────────────────────────────────────
class AmazonPurchasingListener(PythonJavaClass):  # pragma: no cover
    """Gestionnaire des callbacks Amazon IAP."""
    __javacontext__ = "app"
    __javainterfaces__ = ["com/amazon/device/iap/PurchasingListener"]

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

                    try:
                        if (
                            receipt.getProductType()
                            == self.manager.amazon_service.getProductType().CONSUMABLE
                        ):
                            self.manager.amazon_service.notifyFulfillment(
                                receipt.getReceiptId(),
                                self.manager.amazon_service.getFulfillmentResult().FULFILLED,
                            )
                    except Exception as exc:
                        print(f"⚠️ Erreur traitement achat Amazon: {exc}")

                    self.manager._notify_success("amazon", [product_id])
                else:
                    print("⚠️ Achat Amazon sans receipt")
                    self.manager._notify_error(
                        "Achat Amazon invalide", provider="amazon"
                    )
            else:
                print(f"⚠️ Achat Amazon échoué - status: {response_status}")
                self.manager._notify_error(
                    f"Erreur achat Amazon (status {response_status})",
                    provider="amazon",
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
                    product = product_data.values().iterator().next()
                    if product:
                        price = product.getPrice()
                        self.manager.amazon_product_data = product
                        if price:
                            self.manager.display_price = price
                        print("✅ ProductData Amazon récupérés:", getattr(self.manager, "display_price", ""))
                        self.manager._dispatch_state_change()
                else:
                    print("⚠️ ProductData Amazon vides")
                    self.manager.amazon_product_data = None
                    self.manager._notify_error(
                        "Produit indisponible sur Amazon", provider="amazon"
                    )
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


# ──────────────────────────────────────────────────────────────────────────────
# MANAGER CENTRAL
# ──────────────────────────────────────────────────────────────────────────────
class InAppPurchaseManager:
    """Gestionnaire centralisé des achats in-app (Google Play et Amazon)."""

    GOOGLE_INAPP_PRODUCT_ID = "premium_features"  # ← adapte si nécessaire

    def __init__(self):
        self.billing_ready = False
        self.google_billing_client = None
        self.google_client_class = None
        self.google_product_details = None
        # Garder des références fortes sur les listeners Java ↔ Python pour éviter le GC
        self._google_purchase_listener = None
        self._google_billing_state_listener = None
        self._google_product_details_listener = None
        self._google_purchases_response_listener = None
        self.amazon_service = None
        self.amazon_product_data = None
        self.amazon_user_data = None
        self.request_status_class = None
        self.display_price = None
        self.activity = None
        self.listeners = []
        # Reconnexion Billing
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5

        # Lance l'initialisation des services Billing (Google / Amazon)
        self._init_billing_services()

    # ── INIT
    def _init_billing_services(self):
        if not PYJNIUS_AVAILABLE:
            print("ℹ️ PyJNIUS non disponible - mode desktop simulé")
            self.billing_ready = True
            self._dispatch_state_change()
            return

        try:
            Build = autoclass("android.os.Build")
            manufacturer = Build.MANUFACTURER.lower()

            if "amazon" in manufacturer:
                self._init_amazon_billing()
            else:
                self._init_google_billing()

        except Exception as exc:
            print(f"⚠️ Erreur initialisation billing: {exc}")

    def _init_google_billing(self):
        """Initialise Google Play Billing v8."""
        try:
            # Activity/Context
            try:
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                ctx = getattr(PythonActivity, "mActivity", None)
            except Exception:
                ctx = None
            if ctx is None:
                try:
                    from android import activity as _activity_module  # type: ignore
                    # Certains environnements exposent .getApplicationContext()
                    ctx = getattr(_activity_module, "getApplicationContext", lambda: None)() or _activity_module
                except Exception:
                    ctx = None
            if ctx is None:
                raise RuntimeError("No Android Context for Billing init")

            self.activity = ctx
            self.google_client_class = autoclass("com.android.billingclient.api.BillingClient")

            # Builder + listener
            builder = self.google_client_class.newBuilder(ctx)
            self._google_purchase_listener = GooglePurchasesUpdatedListener(self)
            builder.setListener(self._google_purchase_listener)
            builder.enablePendingPurchases()  # obligatoire
            self.google_billing_client = builder.build()

            # Connexion
            self._google_billing_state_listener = GoogleBillingStateListener(self)
            self.google_billing_client.startConnection(self._google_billing_state_listener)

        except Exception as exc:
            print(f"✗ Erreur initialisation Google Billing: {exc}")

    def _connect_google_billing(self):
        """(Re)connecte BillingClient proprement (v8)."""
        if not self.google_billing_client or not self.google_client_class or not self.activity:
            # Contexte incomplet -> réinitialiser complètement
            self._init_google_billing()
            return
        try:
            self._google_billing_state_listener = GoogleBillingStateListener(self)
            self.google_billing_client.startConnection(self._google_billing_state_listener)
        except Exception as exc:
            print(f"✗ Erreur startConnection Billing: {exc}")

    def _schedule_google_reconnect(self):
        """Planifie une reconnexion avec backoff exponentiel jusqu’à 5 tentatives."""
        try:
            import threading, math
            if self._reconnect_attempts >= self._max_reconnect_attempts:
                print("⚠️ Abandon reconnexions Billing (max atteint)")
                return
            delay = min(30, 2 ** self._reconnect_attempts)
            self._reconnect_attempts += 1
            print(f"⏳ Reconnexion Billing dans {delay}s (tentative {self._reconnect_attempts})")
            def _do():
                try:
                    self._connect_google_billing()
                finally:
                    # Si ça réussit, on reset dans onBillingSetupFinished
                    pass
            t = threading.Timer(delay, _do)
            t.daemon = True
            t.start()
        except Exception as exc:
            print(f"✗ Erreur planification reconnexion Billing: {exc}")

    def _init_amazon_billing(self):
        """Initialise Amazon In-App Purchasing."""
        try:
            self.amazon_service = autoclass("com.amazon.device.iap.PurchasingService")
            self.request_status_class = autoclass(
                "com.amazon.device.iap.model.PurchaseResponse$RequestStatus"
            )
            listener = AmazonPurchasingListener(self)
            self.amazon_service.registerListener(activity.getApplicationContext(), listener)
            self.listeners.append(listener)
            self.billing_ready = True
            self._dispatch_state_change()
            print("✅ Amazon IAP initialisé et prêt")
        except Exception as exc:
            print(f"✗ Erreur initialisation Amazon IAP: {exc}")

    # ── UTILITAIRES ACHATS
    def _extract_purchase_ids(self, purchase):
        """Retourne la liste des productIds d'un achat (v6+: getProducts, fallback getSkus)."""
        product_ids = []
        try:
            plist = purchase.getProducts()
            for j in range(plist.size()):
                product_ids.append(plist.get(j))
        except Exception:
            try:
                sl = purchase.getSkus()
                for j in range(sl.size()):
                    product_ids.append(sl.get(j))
            except Exception:
                pass
        return product_ids

    def _ack_purchase_if_needed(self, purchase, context="purchase"):
        """Reconnaît (acknowledge) l'achat si PURCHASED et pas encore acknowledged."""
        try:
            PURCHASED = autoclass(
                "com.android.billingclient.api.Purchase$PurchaseState"
            ).PURCHASED
            if purchase.getPurchaseState() == PURCHASED and not purchase.isAcknowledged():
                AcknowledgePurchaseParams_Builder = autoclass(
                    "com.android.billingclient.api.AcknowledgePurchaseParams$Builder"
                )
                ack_params = (
                    AcknowledgePurchaseParams_Builder()
                    .setPurchaseToken(purchase.getPurchaseToken())
                    .build()
                )

                class AckListener(PythonJavaClass):
                    __javainterfaces__ = [
                        "com/android/billingclient/api/AcknowledgePurchaseResponseListener"
                    ]
                    __javacontext__ = "app"

                    @java_method("(Lcom/android/billingclient/api/BillingResult;)V")
                    def onAcknowledgePurchaseResponse(self_, br):
                        try:
                            rc = br.getResponseCode()
                            print(f"🔔 Acknowledge response ({context}): {rc}")
                        except Exception:
                            pass

                try:
                    self.google_billing_client.acknowledgePurchase(
                        ack_params, AckListener()
                    )
                except Exception as exc:
                    print(f"✗ Erreur ack ({context}): {exc}")
        except Exception as exc:
            print(f"⚠️ Erreur traitement purchase state ({context}): {exc}")

    # ── READY → FETCH PRODUCT DETAILS + RESTORE
    def _on_google_billing_ready(self):
        self.billing_ready = True
        self._reconnect_attempts = 0  # reset backoff
        self._dispatch_state_change()
        self._fetch_google_product_details()
        self.restore_google_purchases()

    def _fetch_google_product_details(self):
        """Interroge les ProductDetails via ArrayList Java (v8)."""
        try:
            QueryProductDetailsParams_Builder = autoclass(
                "com.android.billingclient.api.QueryProductDetailsParams$Builder"
            )
            Product_Builder = autoclass(
                "com.android.billingclient.api.QueryProductDetailsParams$Product$Builder"
            )
            ArrayList = autoclass("java.util.ArrayList")

            product = (
                Product_Builder()
                .setProductId(self.GOOGLE_INAPP_PRODUCT_ID)
                .setProductType(self.google_client_class.ProductType.INAPP)
                .build()
            )
            product_list = ArrayList()
            product_list.add(product)

            params = QueryProductDetailsParams_Builder()\
                .setProductList(product_list)\
                .build()

            self._google_product_details_listener = GoogleProductDetailsListener(self)
            self.google_billing_client.queryProductDetailsAsync(
                params, self._google_product_details_listener
            )
        except Exception as exc:
            print(f"⚠️ Erreur requête ProductDetails: {exc}")

    # ── PUBLIC
    def is_ready(self):
        return self.billing_ready

    def get_product_price(self):
        return self.display_price or "Prix non disponible"

    def add_listener(self, listener_obj_or_callable):
        """Optionnel: enregistre un listener UI local pour être notifié des changements."""
        self.listeners.append(listener_obj_or_callable)

    # ── EVENTS
    def _dispatch_state_change(self):
        try:
            for listener in getattr(self, "listeners", []):
                try:
                    if hasattr(listener, "on_billing_state_change"):
                        listener.on_billing_state_change()
                    elif callable(listener):
                        listener()
                except Exception:
                    continue
        except Exception:
            pass

    def _notify_success(self, provider, product_ids=None):
        print(f"✅ Achat {provider} réussi")
        if product_ids:
            try:
                # Import retardé pour éviter problèmes d'analyse hors Android
                from kivy.app import App  # type: ignore
                app = App.get_running_app()
                if app:
                    for product_id in product_ids:
                        try:
                            app.on_purchase_success(product_id, provider)
                        except Exception as e:
                            print(f"❌ Erreur on_purchase_success({product_id}): {e}")
            except Exception as e:
                print(f"❌ Erreur appel on_purchase_success: {e}")
        else:
            print("⚠️ Aucun product_id fourni pour la notification de succès")

    def _notify_error(self, message, provider, warn_only=False):
        level = "⚠️" if warn_only else "❌"
        print(f"{level} Erreur {provider}: {message}")

    # ── PURCHASE
    def purchase_product(self, product_id: str | None = None):
        """Lance l'achat Google/Amazon pour product_id (par défaut premium_features)."""
        if not self.billing_ready:
            self._notify_error("Service de paiement non prêt", "system")
            return

        target_id = product_id or self.GOOGLE_INAPP_PRODUCT_ID

        try:
            if self.google_billing_client:
                self._launch_google_purchase(target_id)
            elif self.amazon_service:
                self._launch_amazon_purchase(target_id)
            else:
                self._notify_error("Aucun service de paiement disponible", "system")
        except Exception as exc:
            print(f"✗ Exception lancement achat: {exc}")
            self._notify_error("Erreur lancement achat", "system")

    def _launch_google_purchase(self, product_id):
        try:
            if not self.google_product_details:
                self._notify_error("Détails produit non disponibles", "google")
                return

            # Billing v8: ProductDetailsParams list
            BillingFlowParams_Builder = autoclass(
                "com.android.billingclient.api.BillingFlowParams$Builder"
            )
            ProductDetailsParams_Builder = autoclass(
                "com.android.billingclient.api.BillingFlowParams$ProductDetailsParams$Builder"
            )
            ArrayList = autoclass("java.util.ArrayList")

            pdp = ProductDetailsParams_Builder()\
                .setProductDetails(self.google_product_details)\
                .build()

            pdp_list = ArrayList()
            pdp_list.add(pdp)

            params = BillingFlowParams_Builder()\
                .setProductDetailsParamsList(pdp_list)\
                .build()

            runnable = LaunchBillingRunnable(self, params)
            run_on_ui_thread(runnable.run)()  # type: ignore

        except Exception as exc:
            print(f"✗ Exception achat Google: {exc}")
            self._notify_error("Erreur achat Google", "google")

    def _launch_amazon_purchase(self, product_id):
        try:
            self.amazon_service.purchase(product_id)
        except Exception as exc:
            print(f"✗ Exception achat Amazon: {exc}")
            self._notify_error("Erreur achat Amazon", "amazon")

    # ── RESTORE
    def restore_google_purchases(self):
        """Restaure les achats INAPP déjà effectués (et ack si besoin)."""
        try:
            QueryPurchasesParams_Builder = autoclass(
                "com.android.billingclient.api.QueryPurchasesParams$Builder"
            )
            params = (
                QueryPurchasesParams_Builder()
                .setProductType(self.google_client_class.ProductType.INAPP)
                .build()
            )
            self._google_purchases_response_listener = GooglePurchasesResponseListener(self)
            self.google_billing_client.queryPurchasesAsync(
                params, self._google_purchases_response_listener
            )
        except Exception as e:
            print(f"⚠️ restore_google_purchases failed: {e}")
