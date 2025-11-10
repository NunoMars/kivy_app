package org.tarot;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import java.util.Calendar;

public class AlarmScheduler {
  private static PendingIntent pi(Context ctx){
    Intent i = new Intent(ctx, DailyReminderReceiver.class);
    int f = PendingIntent.FLAG_UPDATE_CURRENT;
    if (Build.VERSION.SDK_INT >= 23) f |= PendingIntent.FLAG_IMMUTABLE;
    return PendingIntent.getBroadcast(ctx, 1001, i, f);
  }
  public static void scheduleDaily(Context ctx){
    AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
    if (am == null) return;
    Calendar c = Calendar.getInstance();
    c.set(Calendar.SECOND,0); c.set(Calendar.MILLISECOND,0);
    c.set(Calendar.HOUR_OF_DAY,11); c.set(Calendar.MINUTE,0);
    if (c.getTimeInMillis() <= System.currentTimeMillis()) c.add(Calendar.DATE,1);
    long t = c.getTimeInMillis();
    if (Build.VERSION.SDK_INT >= 23) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi(ctx));
    else if (Build.VERSION.SDK_INT >= 19) am.setExact(AlarmManager.RTC_WAKEUP, t, pi(ctx));
    else am.set(AlarmManager.RTC_WAKEUP, t, pi(ctx));
  }
  public static void cancelDaily(Context ctx){
    AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
    if (am == null) return;
    am.cancel(pi(ctx));
  }
}
