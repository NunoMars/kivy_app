package org.tarot.billing;

import android.app.Activity;
import android.util.Log;

import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.ConsumeParams;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.PurchasesUpdatedListener;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import com.android.billingclient.api.ProductDetails;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Google Play Billing v8 manager for Kivy (non-consumable products).
 * Python usage via pyjnius:
 * BillingManager.init(activity)
 * BillingManager.purchase(activity, "remove_ads")
 * BillingManager.hasPurchased("remove_ads")
 */
public final class BillingManager {
    private static final String TAG = "BillingManager";

    private static BillingClient billingClient = null;
    private static boolean billingReady = false;
    private static final Map<String, Purchase> purchasesMap = new HashMap<>();

    private BillingManager() {}

    public static void init(Activity activity) {
        try {
            if (billingClient != null && billingClient.isReady()) {
                Log.d(TAG, "init(): already ready");
                billingReady = true;
                queryPurchasesAsync();
                return;
            }
        billingClient = BillingClient.newBuilder(activity)
            .enablePendingPurchases(
                com.android.billingclient.api.PendingPurchasesParams
                    .newBuilder()
                    .enableOneTimeProducts()
                    .build()
            )
            .setListener(BillingManager::onPurchasesUpdated)
            .build();

            billingClient.startConnection(new BillingClientStateListener() {
                @Override
                public void onBillingSetupFinished(BillingResult billingResult) {
                    if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                        Log.d(TAG, "Billing setup finished OK");
                        billingReady = true;
                        queryPurchasesAsync();
                    } else {
                        Log.w(TAG, "Billing setup finished code=" + billingResult.getResponseCode() + " msg=" + billingResult.getDebugMessage());
                        billingReady = false;
                    }
                }

                @Override
                public void onBillingServiceDisconnected() {
                    Log.w(TAG, "Billing service disconnected");
                    billingReady = false;
                }
            });
        } catch (Throwable t) {
            Log.e(TAG, "init failed: " + t.getMessage(), t);
        }
    }

    public static boolean isBillingReady() {
        return billingReady;
    }

    public static void purchase(Activity activity, String productId) {
        if (!billingReady) {
            Log.w(TAG, "purchase() called but billing not ready");
            return;
        }
        try {
            QueryProductDetailsParams params = QueryProductDetailsParams.newBuilder()
                    .setProductList(
                            java.util.Collections.singletonList(
                                    QueryProductDetailsParams.Product.newBuilder()
                                            .setProductId(productId)
                                            .setProductType(BillingClient.ProductType.INAPP)
                                            .build()
                            )
                    )
                    .build();

            billingClient.queryProductDetailsAsync(params, (billingResult, productDetailsResult) -> {
                java.util.List<ProductDetails> productDetailsList = (productDetailsResult != null)
                        ? productDetailsResult.getProductDetailsList()
                        : null;
                if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK && productDetailsList != null && !productDetailsList.isEmpty()) {
                    ProductDetails pd = productDetailsList.get(0);
                    BillingFlowParams.ProductDetailsParams detailsParams = BillingFlowParams.ProductDetailsParams.newBuilder()
                            .setProductDetails(pd)
                            .build();
                    BillingFlowParams flowParams = BillingFlowParams.newBuilder()
                            .setProductDetailsParamsList(java.util.Collections.singletonList(detailsParams))
                            .build();
                    BillingResult launchRes = billingClient.launchBillingFlow(activity, flowParams);
                    Log.d(TAG, "launchBillingFlow response=" + launchRes.getResponseCode() + " msg=" + launchRes.getDebugMessage());
                } else {
                    Log.e(TAG, "queryProductDetailsAsync failed: " + billingResult.getDebugMessage());
                }
            });
        } catch (Throwable t) {
            Log.e(TAG, "purchase failed: " + t.getMessage(), t);
        }
    }

    public static void onPurchasesUpdated(BillingResult billingResult, List<Purchase> purchases) {
        int code = billingResult.getResponseCode();
        if (code == BillingClient.BillingResponseCode.OK) {
            if (purchases != null) handlePurchases(purchases);
        } else if (code == BillingClient.BillingResponseCode.USER_CANCELED) {
            Log.d(TAG, "User canceled purchase");
        } else {
            Log.e(TAG, "Purchase failed code=" + code + " msg=" + billingResult.getDebugMessage());
        }
    }

    private static void handlePurchases(List<Purchase> purchases) {
        try {
            for (Purchase p : purchases) {
                for (String pid : p.getProducts()) {
                    purchasesMap.put(pid, p);
                }
                if (p.getPurchaseState() == Purchase.PurchaseState.PURCHASED && !p.isAcknowledged()) {
                    AcknowledgePurchaseParams ack = AcknowledgePurchaseParams.newBuilder()
                            .setPurchaseToken(p.getPurchaseToken())
                            .build();
                    billingClient.acknowledgePurchase(ack, result ->
                            Log.d(TAG, "Acknowledge result code=" + result.getResponseCode() + " msg=" + result.getDebugMessage())
                    );
                }
            }
        } catch (Throwable t) {
            Log.e(TAG, "handlePurchases failed: " + t.getMessage(), t);
        }
    }

    private static void queryPurchasesAsync() {
        try {
            QueryPurchasesParams params = QueryPurchasesParams.newBuilder()
                    .setProductType(BillingClient.ProductType.INAPP)
                    .build();
            billingClient.queryPurchasesAsync(params, (billingResult, purchaseList) -> {
                if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    purchasesMap.clear();
                    if (purchaseList != null) {
                        for (Purchase p : purchaseList) {
                            for (String pid : p.getProducts()) purchasesMap.put(pid, p);
                        }
                    }
                    Log.d(TAG, "queryPurchasesAsync loaded=" + purchasesMap.size());
                } else {
                    Log.w(TAG, "queryPurchasesAsync failed: " + billingResult.getDebugMessage());
                }
            });
        } catch (Throwable t) {
            Log.e(TAG, "queryPurchasesAsync failed: " + t.getMessage(), t);
        }
    }

    public static boolean hasPurchased(String productId) {
        Purchase p = purchasesMap.get(productId);
        return p != null && p.getPurchaseState() == Purchase.PurchaseState.PURCHASED;
    }

    public static void consume(String productId) {
        try {
            Purchase p = purchasesMap.get(productId);
            if (p == null) {
                Log.w(TAG, "consume: no purchase for " + productId);
                return;
            }
            ConsumeParams params = ConsumeParams.newBuilder().setPurchaseToken(p.getPurchaseToken()).build();
            billingClient.consumeAsync(params, (billingResult, outToken) -> {
                Log.d(TAG, "consumeAsync code=" + billingResult.getResponseCode() + " msg=" + billingResult.getDebugMessage());
                if (billingResult.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    purchasesMap.remove(productId);
                }
            });
        } catch (Throwable t) {
            Log.e(TAG, "consume failed: " + t.getMessage(), t);
        }
    }
}
