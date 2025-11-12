package org.tarot;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.os.Build;
import android.content.SharedPreferences;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import androidx.core.app.NotificationCompat; // AndroidX support lib
// NOTE: R reference requires resource merging; if p4a doesn't generate R, fallback to system icon.
// We guard with try/catch; if R not resolved at runtime, system icon used.

/**
 * DailyReminderReceiver
 * Déclenché par AlarmManager pour rappeler à l'utilisateur de faire son tirage quotidien.
 */
public class DailyReminderReceiver extends BroadcastReceiver {
    public static final String CHANNEL_ID = "tarot_daily_channel";
    public static final int NOTIF_ID = 11101;

    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            // Ne pas notifier si déjà tiré aujourd'hui (préférence partagée par l'app Python)
            SharedPreferences prefs = context.getSharedPreferences("tarot_prefs", Context.MODE_PRIVATE);
            String last = prefs != null ? prefs.getString("last_draw_date", "") : "";
            String today = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());
            if (today.equals(last)) {
                return; // déjà fait aujourd'hui
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
        } catch (Exception ignored) {
        }
    }
}
