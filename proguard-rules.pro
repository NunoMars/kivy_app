# ═══════════════════════════════════════════════════════════════
# ProGuard/R8 Rules - Ma Carte De Tarot
# ═══════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────
# 📱 Google Mobile Ads (AdMob)
# ───────────────────────────────────────────────────────────────
-keep class com.google.android.gms.ads.** { *; }
-keep class com.google.ads.mediation.** { *; }
-keep interface com.google.android.gms.ads.** { *; }
-dontwarn com.google.android.gms.ads.**

# ───────────────────────────────────────────────────────────────
# 💳 Google Play Billing
# ───────────────────────────────────────────────────────────────
-keep class com.android.billingclient.api.** { *; }
-keep interface com.android.billingclient.api.** { *; }
-dontwarn com.android.billingclient.**

# ───────────────────────────────────────────────────────────────
# 🔐 User Messaging Platform (Consentement RGPD)
# ───────────────────────────────────────────────────────────────
-keep class com.google.android.ump.** { *; }
-keep interface com.google.android.ump.** { *; }
-dontwarn com.google.android.ump.**

# ───────────────────────────────────────────────────────────────
# 📺 Médiation - AppLovin
# ───────────────────────────────────────────────────────────────
-keep class com.applovin.** { *; }
-keep interface com.applovin.** { *; }
-dontwarn com.applovin.**
-dontwarn com.google.android.exoplayer2.**

# ───────────────────────────────────────────────────────────────
# 📺 Médiation - ironSource
# ───────────────────────────────────────────────────────────────
-keep class com.ironsource.** { *; }
-keep interface com.ironsource.** { *; }
-dontwarn com.ironsource.**

# ───────────────────────────────────────────────────────────────
# 🎯 Google Play Services - Base
# ───────────────────────────────────────────────────────────────
-keep class com.google.android.gms.common.** { *; }
-keep class com.google.android.gms.tasks.** { *; }
-dontwarn com.google.android.gms.**

# ───────────────────────────────────────────────────────────────
# 🐍 Python/Kivy - Conserver pour JNI
# ───────────────────────────────────────────────────────────────
-keep class org.kivy.** { *; }
-keep class org.renpy.** { *; }
-keep class org.tarot.** { *; }

# ───────────────────────────────────────────────────────────────
# 🔍 Débogage - Conserver infos pour stack traces
# ───────────────────────────────────────────────────────────────
-keepattributes SourceFile,LineNumberTable
-keepattributes *Annotation*
-keepattributes Signature
-keepattributes Exceptions

# ───────────────────────────────────────────────────────────────
# ⚡ Optimisations R8
# ───────────────────────────────────────────────────────────────
-optimizationpasses 5
-dontusemixedcaseclassnames
-dontskipnonpubliclibraryclasses
-verbose

# Conserver les méthodes natives (JNI)
-keepclasseswithmembernames class * {
    native <methods>;
}

# Conserver les enums
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Conserver les Parcelables
-keepclassmembers class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Conserver les Serializable
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}
