package org.tarot;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.os.Build;
import android.content.SharedPreferences;
import android.util.Log;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;
import androidx.core.app.NotificationCompat; // AndroidX support lib
// NOTE: R reference requires resource merging; if p4a doesn't generate R, fallback to system icon.
// We guard with try/catch; if R not resolved at runtime, system icon used.

/**
 * DailyReminderReceiver
 * Déclenché par AlarmManager à 11h pour rappeler à l'utilisateur de faire son tirage quotidien.
 * 
 * Logique:
 * - Ne notifie PAS si l'app a été ouverte avant 11h aujourd'hui
 * - Ne notifie PAS si le tirage a déjà été fait aujourd'hui
 * - Ne notifie PAS si une notification a déjà été envoyée aujourd'hui (anti-spam)
 */
public class DailyReminderReceiver extends BroadcastReceiver {
    private static final String TAG = "TAROT_NOTIF";
    public static final String CHANNEL_ID = "tarot_daily_channel";
    public static final int NOTIF_ID = 11101;

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d(TAG, "DailyReminderReceiver.onReceive() déclenché à 11h");
        
        try {
            SharedPreferences prefs = context.getSharedPreferences("tarot_prefs", Context.MODE_PRIVATE);
            String today = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());
            
            // 1. Vérifier si tirage déjà fait aujourd'hui
            String lastDrawDate = prefs != null ? prefs.getString("last_draw_date", "") : "";
            if (today.equals(lastDrawDate)) {
                Log.d(TAG, "✅ Tirage déjà fait aujourd'hui → pas de notification");
                return;
            }
            
            // 2. Vérifier si app ouverte avant 11h aujourd'hui
            if (wasAppOpenedBeforeElevenToday(prefs)) {
                Log.d(TAG, "✅ App ouverte avant 11h aujourd'hui → pas de notification");
                return;
            }
            
            // 3. Vérifier si notification déjà envoyée aujourd'hui (anti-spam)
            String lastNotifiedDate = prefs != null ? prefs.getString("last_notified_date", "") : "";
            if (today.equals(lastNotifiedDate)) {
                Log.d(TAG, "✅ Notification déjà envoyée aujourd'hui → pas de notification");
                return;
            }

            NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm == null) return;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                NotificationChannel ch = new NotificationChannel(
                        CHANNEL_ID,
                        "Rappel tirage quotidien",
                        NotificationManager.IMPORTANCE_DEFAULT
                );
                ch.setDescription("Notification pour inciter à tirer la carte du jour");
                nm.createNotificationChannel(ch);
            }

            Intent launchIntent = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
            PendingIntent pi = null;
            if (launchIntent != null) {
                int flags = PendingIntent.FLAG_UPDATE_CURRENT;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    flags |= PendingIntent.FLAG_IMMUTABLE;
                }
                pi = PendingIntent.getActivity(context, 0, launchIntent, flags);
            }

            int smallIconId;
            try {
                // Attempt to resolve packaged vector resource
                smallIconId = context.getResources().getIdentifier("ic_tarot_notification", "drawable", context.getPackageName());
                if (smallIconId == 0) {
                    smallIconId = android.R.drawable.ic_popup_reminder; // fallback
                }
            } catch (Exception e) {
                smallIconId = android.R.drawable.ic_popup_reminder;
            }
            NotificationCompat.Builder b = new NotificationCompat.Builder(context, CHANNEL_ID)
                    .setSmallIcon(smallIconId)
                    .setContentTitle("Ma Carte de Tarot")
                    .setContentText("Votre carte du jour vous attend ✨")
                    .setAutoCancel(true)
                    .setPriority(NotificationCompat.PRIORITY_DEFAULT);
            if (pi != null) {
                b.setContentIntent(pi);
            }
            nm.notify(NOTIF_ID, b.build());
            Log.d(TAG, "🔔 Notification envoyée avec succès");
            
            // Enregistrer qu'on a notifié aujourd'hui (anti-spam)
            if (prefs != null) {
                SharedPreferences.Editor editor = prefs.edit();
                editor.putString("last_notified_date", today);
                editor.apply();
                Log.d(TAG, "📝 last_notified_date enregistré: " + today);
            }
        } catch (Exception e) {
            Log.e(TAG, "❌ Erreur lors de l'envoi de la notification: " + e.getMessage());
        }
    }
    
    /**
     * Vérifie si l'app a été ouverte avant 11h aujourd'hui.
     * 
     * @param prefs SharedPreferences contenant last_open_timestamp
     * @return true si l'app a été ouverte aujourd'hui avant 11h, false sinon
     */
    private boolean wasAppOpenedBeforeElevenToday(SharedPreferences prefs) {
        if (prefs == null) {
            Log.d(TAG, "⚠️ SharedPreferences null, assume pas d'ouverture");
            return false;
        }
        
        try {
            long lastOpenTimestamp = prefs.getLong("last_open_timestamp", 0L);
            
            if (lastOpenTimestamp == 0L) {
                Log.d(TAG, "ℹ️ Aucun last_open_timestamp trouvé");
                return false;
            }
            
            // Calculer le timestamp de aujourd'hui à 00:00:00
            Calendar todayMidnight = Calendar.getInstance();
            todayMidnight.set(Calendar.HOUR_OF_DAY, 0);
            todayMidnight.set(Calendar.MINUTE, 0);
            todayMidnight.set(Calendar.SECOND, 0);
            todayMidnight.set(Calendar.MILLISECOND, 0);
            long todayMidnightMs = todayMidnight.getTimeInMillis();
            
            // Calculer le timestamp de aujourd'hui à 11:00:00
            Calendar todayEleven = Calendar.getInstance();
            todayEleven.set(Calendar.HOUR_OF_DAY, 11);
            todayEleven.set(Calendar.MINUTE, 0);
            todayEleven.set(Calendar.SECOND, 0);
            todayEleven.set(Calendar.MILLISECOND, 0);
            long todayElevenMs = todayEleven.getTimeInMillis();
            
            // Vérifier si last_open est aujourd'hui ET avant 11h
            boolean isToday = lastOpenTimestamp >= todayMidnightMs;
            boolean isBefore11 = lastOpenTimestamp < todayElevenMs;
            
            Log.d(TAG, String.format("🔍 last_open=%d, today_midnight=%d, today_11h=%d",
                    lastOpenTimestamp, todayMidnightMs, todayElevenMs));
            Log.d(TAG, String.format("🔍 isToday=%b, isBefore11=%b", isToday, isBefore11));
            
            return isToday && isBefore11;
            
        } catch (Exception e) {
            Log.e(TAG, "❌ Erreur vérification last_open_timestamp: " + e.getMessage());
            return false;
        }
    }
}
