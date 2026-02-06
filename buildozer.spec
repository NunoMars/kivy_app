[app]
# ───────────────────────────────
# 🔮 Infos générales
title = Ma Carte De Tarot
package.name = macartedetarot
package.domain = org.tarot
source.dir = .

version = 2.41
android.numeric_version = 2941000
author = © Nuno Marcelino

# ───────────────────────────────
# 🗂️ Fichiers inclus / exclus
source.include_exts = py,kv,png,jpg,ttf,otf,mp3,mp4,json,ini
source.exclude_exts = spec,md
source.exclude_dirs = tests, bin, venv, .github, __pycache__, .git, .vscode, guides, backend, docs, play_store_screenshots, tarot_img/MajorArcanaCards_backup, scripts
source.include_patterns = libs/*.py, fonts/*.ttf, fonts/*.otf, i18n/lang/*.json, tarot_img/*, main.py, app.py, ads_manager.py
android.add_assets = i18n/lang:i18n/lang,tarot_img:tarot_img,fonts:fonts

# ───────────────────────────────
# 🐍 Dépendances Python
# Python 3.11.x = combo stable avec Kivy 2.3.1
requirements = python3==3.11.5, kivy==2.3.1, requests==2.32.3, certifi, pyjnius, plyer

# ───────────────────────────────
# 🖼️ UI
icon.filename = %(source.dir)s/tarot_img/icon.png
presplash.filename = %(source.dir)s/tarot_img/MajorArcanaCards/La Mort.jpg
fullscreen = 0

# ───────────────────────────────
# 📱 Android SDK / Build
android.api = 35
android.minapi = 21
android.ndk = 26c
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1

# 👉 IMPORTANT : une seule arch pour simplifier
android.archs = arm64-v8a

# p4a
p4a.branch = master
p4a.local_recipes = p4a_recipes

# Fix Google Play 16KB page-size + harfbuzz strict cast
# Flags 16KB injectés automatiquement via le hook p4a (voir p4a_hooks/manifest_receivers.py)
# Le hook modifie Application.mk, LDFLAGS, CFLAGS et CXXFLAGS pour TOUTES les recettes
p4a.extra_args = 

# ───────────────────────────────
# 🪄 Logs
android.logcat_filters = *:E PythonActivity:V python:I libc:E AndroidRuntime:E linker:E SDL:E
log_level = 2

# ───────────────────────────────
# 🔐 Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, com.google.android.gms.permission.AD_ID, WAKE_LOCK, VIBRATE, RECEIVE_BOOT_COMPLETED, POST_NOTIFICATIONS

# ───────────────────────────────
# 💰 Ads + In-App + Médiation
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5749803259882370~1482612480

# Repositories Gradle
android.add_gradle_repositories = 
    google()
    mavenCentral()
    maven { url 'https://android-sdk.is.com/' }
    maven { url 'https://artifacts.applovin.com/android' }

# Dépendances (Ads + Médiation uniquement, plus d'achats in-app)
android.gradle_dependencies = com.google.android.gms:play-services-ads:23.0.0, com.google.android.ump:user-messaging-platform:2.2.0, androidx.fragment:fragment:1.8.5

# ───────────────────────────────
# 🧱 Formats de build
android.release_artifact = aab
android.debug_artifact = aab

# ───────────────────────────────
# ⚙️ Packaging
android.add_aapt_options = -0 arsc -0 json
android.extra_args = --release
android.exclude_patterns = *.bak,*.tmp,*.log,__pycache__/,*.spec

# ───────────────────────────────
# 🔏 Signature (⚠ tu assumes les mdp en clair)
android.release_keystore = googleplay.keystore
android.release_keystore_password = nunotheboss
android.release_keyalias = upload
android.release_keyalias_password = nunotheboss

# ───────────────────────────────
# 🧩 ProGuard / R8 - Optimisation + Symboles de débogage
# (External rules file to avoid parser issues)
android.add_proguard_rules = proguard-rules.pro

# Enable R8 minification and resource shrinking for release builds
android.gradle_app_settings = 
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            ndk {
                debugSymbolLevel 'FULL'
            }
        }
    }

# ───────────────────────────────
# Manifest XML — receivers (injectés dans <application>)
android.add_manifest_xml = """
    <receiver android:name=\"org.tarot.DailyReminderReceiver\" android:exported=\"false\" />
    <receiver android:name=\"org.tarot.BootCompletedReceiver\" android:enabled=\"true\" android:exported=\"true\">
        <intent-filter>
            <action android:name=\"android.intent.action.BOOT_COMPLETED\" />
            <action android:name=\"android.intent.action.LOCKED_BOOT_COMPLETED\" />
        </intent-filter>
    </receiver>
"""

# Inclure sources Java custom
android.add_src = java_src
android.add_resources = res
p4a.hook = p4a_hooks/manifest_receivers.py

[buildozer]
warn_on_root = 1
log_level = 2
