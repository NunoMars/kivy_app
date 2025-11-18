package org.tarot.consent;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import org.tarot.ads.AdManager; // pour appliquer le choix immédiatement

/**
 * Gestion simple du consentement publicitaire (avant intégration complète UMP).
 * Affiche un dialogue explicatif au premier lancement permettant à l'utilisateur
 * de choisir entre publicités personnalisées (soutien maximal) ou non personnalisées.
 * Le choix est persisté dans SharedPreferences et réutilisé pour les requêtes AdMob.
 *
 * Python usage via pyjnius:
 * ConsentManager.showConsentIfNeeded(activity)
 * boolean personalized = ConsentManager.isPersonalized();
 */
public final class ConsentManager {
    private static final String TAG = "ConsentManager";
    private static final String PREF_NAME = "tarot_consent";
    private static final String KEY_SET = "consent_set";
    private static final String KEY_PERSONALIZED = "personalized";

    private ConsentManager() {}

    private static SharedPreferences prefs(Context ctx) {
        return ctx.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static boolean isConsentSet(Context ctx) {
        return prefs(ctx).getBoolean(KEY_SET, false);
    }

    public static boolean isPersonalized(Context ctx) {
        return prefs(ctx).getBoolean(KEY_PERSONALIZED, false); // défaut false -> NPA
    }

    public static void showConsentIfNeeded(Activity activity) {
        if (activity == null) return;
        if (isConsentSet(activity)) {
            // Appliquer choix existant à AdManager
            AdManager.setPersonalizedAds(isPersonalized(activity));
            Log.d(TAG, "Consent déjà défini (personalized=" + isPersonalized(activity) + ")");
            return;
        }
        showDialog(activity);
    }

    private static void showDialog(Activity activity) {
        try {
            String message = "Pour soutenir l'application, vous pouvez autoriser des publicités personnalisées. " +
                    "Elles peuvent être plus pertinentes. Si vous refusez, vous verrez tout de même des publicités basiques.";
            AlertDialog.Builder b = new AlertDialog.Builder(activity)
                    .setTitle("Consentement publicités")
                    .setMessage(message)
                    .setCancelable(false)
                    .setPositiveButton("Autoriser personnalisées", (dialog, which) -> {
                        saveChoice(activity, true);
                    })
                    .setNegativeButton("Publicités basiques", (dialog, which) -> {
                        saveChoice(activity, false);
                    });
            b.show();
        } catch (Throwable t) {
            Log.e(TAG, "showDialog failed: " + t.getMessage(), t);
            // Fallback: si le dialogue échoue on garde mode basique (NPA)
            saveChoice(activity, false);
        }
    }

    private static void saveChoice(Activity activity, boolean personalized) {
        try {
            prefs(activity).edit()
                    .putBoolean(KEY_SET, true)
                    .putBoolean(KEY_PERSONALIZED, personalized)
                    .apply();
            AdManager.setPersonalizedAds(personalized);
            Log.d(TAG, "Consent sauvegardé personalized=" + personalized);
        } catch (Throwable t) {
            Log.e(TAG, "saveChoice failed: " + t.getMessage(), t);
        }
    }
}
