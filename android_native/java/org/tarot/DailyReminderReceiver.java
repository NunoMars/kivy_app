package org.tarot;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.core.app.NotificationCompat;

public class DailyReminderReceiver extends BroadcastReceiver {
  public static final String CHANNEL_ID = "tarot_daily_channel";
  public static final int NOTIF_ID = 11101;

  @Override public void onReceive(Context context, Intent intent) {
    try {
      NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
      if (nm == null) return;
      if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        NotificationChannel ch = new NotificationChannel(CHANNEL_ID, "Rappel tirage quotidien", NotificationManager.IMPORTANCE_DEFAULT);
        ch.setDescription("Notification pour tirer la carte du jour");
        nm.createNotificationChannel(ch);
      }
      Intent launch = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
      PendingIntent contentPi = null;
      if (launch != null){
        int f = PendingIntent.FLAG_UPDATE_CURRENT; if (Build.VERSION.SDK_INT >= 23) f |= PendingIntent.FLAG_IMMUTABLE;
        contentPi = PendingIntent.getActivity(context, 0, launch, f);
      }
      int icon;
      try {
        icon = context.getResources().getIdentifier("ic_tarot_notification","drawable",context.getPackageName());
        if (icon == 0) icon = android.R.drawable.ic_popup_reminder;
      } catch (Exception e){ icon = android.R.drawable.ic_popup_reminder; }
      NotificationCompat.Builder b = new NotificationCompat.Builder(context,CHANNEL_ID)
        .setSmallIcon(icon)
        .setContentTitle("Ma Carte de Tarot")
        .setContentText("Votre carte du jour vous attend ✨")
        .setAutoCancel(true)
        .setPriority(NotificationCompat.PRIORITY_DEFAULT);
      if (contentPi != null) b.setContentIntent(contentPi);
      nm.notify(NOTIF_ID, b.build());
    } catch (Exception ignored) {}
    try { AlarmScheduler.scheduleDaily(context); } catch (Exception ignored) {}
  }
}
