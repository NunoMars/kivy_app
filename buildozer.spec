[app]
# ───────────────────────────────
# 🔮 Informations générales
title = Ma Carte De Tarot
package.name = macartedetarot
package.domain = org.tarot
source.dir = .

version = 1.16
android.numeric_version = 1160000
author = © Nuno Marcelino

# ───────────────────────────────
# 🗂️ Fichiers inclus / exclus
source.include_exts = py,kv,png,jpg,ttf,otf,mp3,mp4,json,ini
source.exclude_exts = spec,md
source.exclude_dirs = tests, bin, venv, .github, __pycache__, .git, .vscode, guides, backend, docs, play_store_screenshots, tarot_img/MajorArcanaCards_backup, scripts
# Patterns d'inclusion très spécifiques (Robustesse)
source.include_patterns = libs/*.py, fonts/*.ttf, fonts/*.otf, i18n/lang/*.json, tarot_img/*, main.py, app.py, billing.py, ads_manager.py


# Inclure les dossiers de ressources dans l’APK (NÉCESSAIRE pour resource_open)
android.add_assets = i18n/lang:i18n/lang,tarot_img:tarot_img,fonts:fonts

# ───────────────────────────────
# 🐍 Dépendances Python
requirements = python3==3.11.5, kivy==2.3.1, filetype==1.2.0, requests==2.32.3, certifi, pyjnius, plyer, kivmob

# ───────────────────────────────
# 🖼️ Visuels & UI
icon.filename = %(source.dir)s/tarot_img/icon.png
presplash.filename = %(source.dir)s/tarot_img/MajorArcanaCards/La Mort.jpg
orientation = portrait
fullscreen = 0

# ───────────────────────────────
# 📱 Android SDK / Build config
android.api = 35
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1
# Utiliser 'develop' pour la branche P4A la plus stable et mise à jour
p4a.branch = develop 

# ───────────────────────────────
# 🪄 Logs & debug
android.logcat_filters = *:E PythonActivity:V python:I libc:E AndroidRuntime:E linker:E SDL:E
log_level = 2

# ───────────────────────────────
# 🔐 Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, com.google.android.gms.permission.AD_ID, WAKE_LOCK, VIBRATE, POST_NOTIFICATIONS

# ───────────────────────────────
# 💰 AdMob / Billing
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5749803259882370~1482612480
android.add_gradle_repositories = "mavenCentral()"
# Vos dépendances Gradle sont bien définies pour les fonctionnalités avancées
android.gradle_dependencies = com.google.android.gms:play-services-ads:23.6.0, com.android.billingclient:billing-ktx:8.0.0

# ───────────────────────────────
# 🧱 Formats de build
android.release_artifact = apk
android.debug_artifact = apk
android.archs = arm64-v8a, armeabi-v7a

# ───────────────────────────────
# ⚙️ Optimisation du packaging
android.add_aapt_options = -0 arsc -0 json
android.extra_args = --release
android.exclude_patterns = *.bak,*.tmp,*.log,__pycache__/,*.spec

# ───────────────────────────────
# 🔏 Signature release
android.release_keystore = googleplay.keystore
# Buildozer/P4A attend les clés suffixées par _password (et non _passwd)
android.release_keystore_password = nunotheboss
android.release_keyalias = upload
android.release_keyalias_password = nunotheboss

# ───────────────────────────────
# 🧩 Options générales Buildozer
[buildozer]
warn_on_root = 1
log_level = 2

# ───────────────────────
# Manifest injections
android.add_manifest_xml = """
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          xmlns:tools="http://schemas.android.com/tools">
    <uses-permission android:name="com.android.vending.BILLING" tools:node="remove" />
    <queries tools:node="merge">
        <intent tools:node="remove">
            <action android:name="android.intent.action.DIAL" />
            <data android:path="tel:" />
        </intent>
        <intent>
            <action android:name="android.intent.action.DIAL" />
            <data android:scheme="tel" />
        </intent>
    </queries>
</manifest>
"""