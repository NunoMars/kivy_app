package org.tarot.ads;

import android.app.Activity;
import android.util.Log;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.FrameLayout;

import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdListener;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.ads.mediation.admob.AdMobAdapter;

import android.os.Bundle;

public final class AdManager {

    private static final String TAG = "AdManager";

    // 🔥 IDs 100 % fixes – aucune entrée Python possible
    private static final String APP_ID = "ca-app-pub-5749803259882370~1482612480";
    private static final String BANNER_ID = "ca-app-pub-5749803259882370/8646786637";
    private static final String INTERSTITIAL_ID = "ca-app-pub-5749803259882370/4840878344";

    private static boolean initialized = false;
    private static boolean nonPersonalizedAds = true;

    private static FrameLayout bannerContainer = null;
    private static AdView bannerAdView = null;

    private static InterstitialAd interstitialAd = null;

    private AdManager() {}

    // -------------------------------------------------------
    // INIT
    // -------------------------------------------------------
    public static void init(Activity activity) {
        if (activity == null) return;

        try {
            if (initialized) return;

            MobileAds.initialize(activity, status ->
                    Log.d(TAG, "MobileAds initialized: " + status)
            );

            Log.d(TAG, "AdManager initialized with APP_ID=" + APP_ID);
            initialized = true;

        } catch (Throwable t) {
            Log.e(TAG, "init() failed: " + t.getMessage(), t);
        }
    }

    // -------------------------------------------------------
    // REQUEST BUILDER (NPA / GDPR)
    // -------------------------------------------------------
    private static AdRequest buildAdRequest() {
        try {
            AdRequest.Builder builder = new AdRequest.Builder();
            if (nonPersonalizedAds) {
                Bundle extras = new Bundle();
                extras.putString("npa", "1");
                builder.addNetworkExtrasBundle(AdMobAdapter.class, extras);
            }
            return builder.build();
        } catch (Throwable t) {
            Log.w(TAG, "buildAdRequest fallback simple");
            return new AdRequest.Builder().build();
        }
    }

    public static void setPersonalizedAds(boolean personalized) {
        nonPersonalizedAds = !personalized;
    }

    // -------------------------------------------------------
    // BANNER
    // -------------------------------------------------------
    public static void loadBanner(Activity activity) {
        if (activity == null) return;

        activity.runOnUiThread(() -> {
            try {
                if (bannerContainer == null) {
                    ViewGroup root = activity.getWindow().getDecorView().findViewById(android.R.id.content);
                    bannerContainer = new FrameLayout(activity);

                    FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                            FrameLayout.LayoutParams.MATCH_PARENT,
                            FrameLayout.LayoutParams.WRAP_CONTENT
                    );
                    params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                    bannerContainer.setLayoutParams(params);

                    root.addView(bannerContainer);
                }

                if (bannerAdView != null) {
                    try { bannerContainer.removeView(bannerAdView); } catch (Exception ignored) {}
                }

                bannerAdView = new AdView(activity);
                bannerAdView.setAdUnitId(BANNER_ID);
                bannerAdView.setAdSize(AdSize.BANNER);

                bannerAdView.setAdListener(new AdListener() {
                    @Override public void onAdLoaded() {
                        Log.d(TAG, "Banner loaded");
                    }
                    @Override public void onAdFailedToLoad(LoadAdError error) {
                        Log.w(TAG, "Banner failed: " + error.getMessage());
                    }
                });

                bannerContainer.addView(bannerAdView);
                bannerAdView.loadAd(buildAdRequest());

                Log.d(TAG, "Banner requested");

            } catch (Throwable t) {
                Log.e(TAG, "loadBanner failed: " + t.getMessage(), t);
            }
        });
    }

    public static void showBanner(Activity activity) {
        if (activity == null) return;
        activity.runOnUiThread(() -> {
            if (bannerContainer != null) bannerContainer.setVisibility(FrameLayout.VISIBLE);
        });
    }

    public static void hideBanner(Activity activity) {
        if (activity == null) return;
        activity.runOnUiThread(() -> {
            if (bannerContainer != null) bannerContainer.setVisibility(FrameLayout.GONE);
        });
    }

    // -------------------------------------------------------
    // INTERSTITIEL
    // -------------------------------------------------------
    public static void loadInterstitial(Activity activity) {
        if (activity == null) return;

        activity.runOnUiThread(() -> {
            try {
                InterstitialAd.load(activity, INTERSTITIAL_ID, buildAdRequest(), new InterstitialAdLoadCallback() {
                    @Override
                    public void onAdLoaded(InterstitialAd ad) {
                        interstitialAd = ad;

                        interstitialAd.setFullScreenContentCallback(new FullScreenContentCallback() {
                            @Override
                            public void onAdDismissedFullScreenContent() {
                                interstitialAd = null;
                                loadInterstitial(activity);
                            }

                            @Override
                            public void onAdFailedToShowFullScreenContent(AdError error) {
                                interstitialAd = null;
                            }
                        });

                        Log.d(TAG, "Interstitial loaded");
                    }

                    @Override
                    public void onAdFailedToLoad(LoadAdError error) {
                        interstitialAd = null;
                        Log.w(TAG, "Interstitial failed: " + error.getMessage());
                    }
                });

                Log.d(TAG, "Interstitial requested");

            } catch (Throwable t) {
                Log.e(TAG, "loadInterstitial failed: " + t.getMessage(), t);
            }
        });
    }

    public static boolean isInterstitialReady() {
        return interstitialAd != null;
    }

    public static void showInterstitial(Activity activity) {
        if (activity == null) return;

        activity.runOnUiThread(() -> {
            try {
                if (interstitialAd != null) {
                    interstitialAd.show(activity);
                    Log.d(TAG, "Interstitial displayed");
                } else {
                    Log.w(TAG, "Interstitial not ready");
                }
            } catch (Throwable t) {
                Log.e(TAG, "showInterstitial failed: " + t.getMessage(), t);
            }
        });
    }
}
