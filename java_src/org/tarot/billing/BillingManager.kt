package org.tarot.billing

import android.app.Activity
import android.util.Log
import com.android.billingclient.api.*

object BillingManager : PurchasesUpdatedListener {
    private const val TAG = "BillingManager"

    private var billingClient: BillingClient? = null
    private var billingReady: Boolean = false
    private val purchasesMap: MutableMap<String, Purchase> = mutableMapOf()

    @JvmStatic
    fun init(activity: Activity) {
        try {
            if (billingClient != null && billingClient?.isReady == true) {
                Log.d(TAG, "init() called but billingClient already ready")
                billingReady = true
                queryPurchasesAsync()
                return
            }

            billingClient = BillingClient.newBuilder(activity)
                .enablePendingPurchases()
                .setListener(this)
                .build()

            billingClient?.startConnection(object : BillingClientStateListener {
                override fun onBillingSetupFinished(billingResult: BillingResult) {
                    if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                        Log.d(TAG, "Billing setup finished OK")
                        billingReady = true
                        queryPurchasesAsync()
                    } else {
                        Log.w(TAG, "Billing setup finished with code: ${billingResult.responseCode} message=${billingResult.debugMessage}")
                        billingReady = false
                    }
                }

                override fun onBillingServiceDisconnected() {
                    Log.w(TAG, "Billing service disconnected")
                    billingReady = false
                }
            })
        } catch (t: Throwable) {
            Log.e(TAG, "init failed: ${t.message}", t)
        }
    }

    @JvmStatic
    fun isBillingReady(): Boolean = billingReady

    @JvmStatic
    fun purchase(activity: Activity, productId: String) {
        if (!billingReady) {
            Log.w(TAG, "purchase() called but billing not ready")
            return
        }

        try {
            val product = BillingClient.Product.newBuilder()
                .setProductId(productId)
                .setProductType(BillingClient.ProductType.INAPP)
                .build()

            val params = QueryProductDetailsParams.newBuilder()
                .setProductList(listOf(product))
                .build()

            billingClient?.queryProductDetailsAsync(params) { billingResult, productDetailsList ->
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && !productDetailsList.isNullOrEmpty()) {
                    val productDetails = productDetailsList[0]

                    // Prepare flow params
                    val productDetailsParams = BillingFlowParams.ProductDetailsParams.newBuilder()
                        .setProductDetails(productDetails)
                        .build()

                    val flowParams = BillingFlowParams.newBuilder()
                        .setProductDetailsParamsList(listOf(productDetailsParams))
                        .build()

                    billingClient?.launchBillingFlow(activity, flowParams)?.let { result ->
                        Log.d(TAG, "launchBillingFlow result: ${result.responseCode} ${result.debugMessage}")
                    }
                } else {
                    Log.e(TAG, "ProductDetails not found or error: ${billingResult.debugMessage}")
                }
            }
        } catch (t: Throwable) {
            Log.e(TAG, "purchase failed: ${t.message}", t)
        }
    }

    override fun onPurchasesUpdated(billingResult: BillingResult, purchases: MutableList<Purchase>?) {
        when (billingResult.responseCode) {
            BillingClient.BillingResponseCode.OK -> {
                if (purchases != null) {
                    handlePurchases(purchases)
                }
            }
            BillingClient.BillingResponseCode.USER_CANCELED -> {
                Log.d(TAG, "User cancelled purchase")
            }
            else -> {
                Log.e(TAG, "Purchase failed: ${billingResult.debugMessage}")
            }
        }
    }

    private fun handlePurchases(purchases: List<Purchase>) {
        try {
            for (purchase in purchases) {
                // store
                for (productId in purchase.products) {
                    purchasesMap[productId] = purchase
                }

                if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED && !purchase.isAcknowledged) {
                    val ackParams = AcknowledgePurchaseParams.newBuilder()
                        .setPurchaseToken(purchase.purchaseToken)
                        .build()
                    billingClient?.acknowledgePurchase(ackParams) { ackResult ->
                        Log.d(TAG, "Acknowledge result: ${ackResult.responseCode} ${ackResult.debugMessage}")
                    }
                }
            }
        } catch (t: Throwable) {
            Log.e(TAG, "handlePurchases failed: ${t.message}", t)
        }
    }

    private fun queryPurchasesAsync() {
        try {
            val params = QueryPurchasesParams.newBuilder()
                .setProductType(BillingClient.ProductType.INAPP)
                .build()

            billingClient?.queryPurchasesAsync(params) { billingResult, purchaseList ->
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    purchasesMap.clear()
                    purchaseList?.forEach { p ->
                        for (productId in p.products) purchasesMap[productId] = p
                    }
                    Log.d(TAG, "queryPurchasesAsync: loaded ${purchasesMap.size} purchases")
                } else {
                    Log.w(TAG, "queryPurchasesAsync failed: ${billingResult.debugMessage}")
                }
            }
        } catch (t: Throwable) {
            Log.e(TAG, "queryPurchasesAsync failed: ${t.message}", t)
        }
    }

    @JvmStatic
    fun hasPurchased(productId: String): Boolean {
        val p = purchasesMap[productId] ?: return false
        return p.purchaseState == Purchase.PurchaseState.PURCHASED
    }

    @JvmStatic
    fun consume(productId: String) {
        try {
            val purchase = purchasesMap[productId] ?: run {
                Log.w(TAG, "consume: no purchase found for $productId")
                return
            }
            val token = purchase.purchaseToken
            val consumeParams = ConsumeParams.newBuilder().setPurchaseToken(token).build()
            billingClient?.consumeAsync(consumeParams) { billingResult, outToken ->
                Log.d(TAG, "consumeAsync: ${billingResult.responseCode} ${billingResult.debugMessage}")
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    purchasesMap.remove(productId)
                }
            }
        } catch (t: Throwable) {
            Log.e(TAG, "consume failed: ${t.message}", t)
        }
    }
}
