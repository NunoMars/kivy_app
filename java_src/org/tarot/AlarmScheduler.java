package org.tarot;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import java.util.Calendar;

/**
 * AlarmScheduler
 * Planifie une alarme quotidienne à 11h locale qui déclenche DailyReminderReceiver
 */
public class AlarmScheduler {
    private static final int REQUEST_CODE = 1001;

    public static void scheduleDaily(Context context) {
        try {
            AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            if (am == null) return;
            Intent intent = new Intent(context, DailyReminderReceiver.class);
            int flags = PendingIntent.FLAG_CANCEL_CURRENT;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                flags |= PendingIntent.FLAG_IMMUTABLE;
            }
            PendingIntent pi = PendingIntent.getBroadcast(context, REQUEST_CODE, intent, flags);

            Calendar cal = Calendar.getInstance();
            cal.set(Calendar.SECOND, 0);
            cal.set(Calendar.MILLISECOND, 0);
            cal.set(Calendar.HOUR_OF_DAY, 11);
            cal.set(Calendar.MINUTE, 0);
            long trigger = cal.getTimeInMillis();
            long now = System.currentTimeMillis();
            if (trigger <= now) {
                // demain
                cal.add(Calendar.DATE, 1);
                trigger = cal.getTimeInMillis();
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pi);
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                am.setExact(AlarmManager.RTC_WAKEUP, trigger, pi);
            } else {
                am.set(AlarmManager.RTC_WAKEUP, trigger, pi);
            }
        } catch (Exception ignored) {
        }
    }

    /**
     * Annule l'alarme quotidienne si elle existe.
     */
    public static void cancelDaily(Context context) {
        try {
            AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            if (am == null) return;
            Intent intent = new Intent(context, DailyReminderReceiver.class);
            int flags = 0;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                flags |= PendingIntent.FLAG_IMMUTABLE;
            }
            PendingIntent pi = PendingIntent.getBroadcast(context, REQUEST_CODE, intent, flags);
            if (pi != null) {
                am.cancel(pi);
            }
        } catch (Exception ignored) {
        }
    }
}
