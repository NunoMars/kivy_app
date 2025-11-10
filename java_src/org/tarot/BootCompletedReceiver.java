package org.tarot;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Redéclenche la planification après redémarrage du device
 */
public class BootCompletedReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        try {
            AlarmScheduler.scheduleDaily(context);
        } catch (Exception ignored) {
        }
    }
}
