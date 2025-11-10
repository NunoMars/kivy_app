package org.tarot;

import android.app.Activity;
import android.content.Context;
import com.google.android.ump.ConsentInformation;
import com.google.android.ump.ConsentRequestParameters;
import com.google.android.ump.UserMessagingPlatform;
import com.google.android.ump.FormError;
import com.google.android.ump.ConsentForm;

/**
 * ConsentBridge - pont simple UMP. Fournit une variable de résultat accessible en polling depuis Python.
 * personalized = Boolean (null = inconnu / en cours)
 */
public class ConsentBridge {
    private static Boolean personalized = null;
    private static boolean started = false;

    public static void request(Activity activity) {
        if (activity == null) return;
        if (started) return;
        started = true;
        try {
            ConsentRequestParameters params = new ConsentRequestParameters.Builder().build();
            ConsentInformation ci = UserMessagingPlatform.getConsentInformation(activity);
            ci.requestConsentInfoUpdate(activity, params,
                    () -> {
                        if (ci.isConsentFormAvailable()) {
                            loadForm(activity, ci);
                        } else {
                            // Pas de formulaire nécessaire => consent non requis => pubs standard autorisées
                            personalized = Boolean.TRUE;
                        }
                    },
                    formError -> {
                        // Echec = fallback non personnalisé
                        personalized = Boolean.FALSE;
                    });
        } catch (Exception e) {
            personalized = Boolean.FALSE;
        }
    }

    private static void loadForm(Activity activity, ConsentInformation ci) {
        try {
            UserMessagingPlatform.loadConsentForm(activity,
                    consentForm -> {
                        try {
                            if (ci.getConsentStatus() == ConsentInformation.ConsentStatus.REQUIRED) {
                                consentForm.show(activity, formError -> {
                                    // Après fermeture du formulaire
                                    if (ci.getConsentStatus() == ConsentInformation.ConsentStatus.OBTAINED) {
                                        personalized = Boolean.TRUE;
                                    } else {
                                        personalized = Boolean.FALSE;
                                    }
                                });
                            } else {
                                // Non requis
                                personalized = Boolean.TRUE;
                            }
                        } catch (Exception e) {
                            personalized = Boolean.FALSE;
                        }
                    },
                    formError -> personalized = Boolean.FALSE);
        } catch (Exception e) {
            personalized = Boolean.FALSE;
        }
    }

    public static Boolean getResult() {
        return personalized;
    }
}
