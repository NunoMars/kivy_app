[app]
title = Ma Carte De Tarot
package.name = macartedetarot
package.domain = org.tarot
source.dir = .

# Fichiers à embarquer
source.include_exts = py,kv,png,jpg,ttf,otf,mp3,mp4,json,ini
source.exclude_exts = spec,md
source.exclude_dirs = tests, bin, venv, .github, __pycache__, .git, .vscode, guides, backend, docs, play_store_screenshots, tarot_img/MajorArcanaCards_backup, scripts
source.include_patterns = libs/*.py, fonts/*.ttf, fonts/*.otf, i18n/lang/*.json
# Si tu préfères forcer un dossier "fonts" entier dans assets :
# android.add_assets = fonts:fonts

version = 1.13
android.numeric_version = 1130000

# Dépendances Python 
requirements = python3==3.11.5, kivy==2.3.1, filetype==1.2.0, requests==2.32.3, certifi

# Visuels
icon.filename = %(source.dir)s/tarot_img/icon.png
presplash.filename = %(source.dir)s/tarot_img/MajorArcanaCards/La Mort.jpg
orientation = portrait
fullscreen = 0
author = © Nuno Marcelino

# Android SDK (aligné 2025)
android.api = 35
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1

# Logs utiles au debug sur device
android.logcat_filters = *:E PythonActivity:V python:I libc:E AndroidRuntime:E linker:E SDL:E

# Permissions minimales (on retire celles inutiles/bruyantes)
android.permissions = INTERNET, ACCESS_NETWORK_STATE, com.google.android.gms.permission.AD_ID, WAKE_LOCK, VIBRATE, POST_NOTIFICATIONS

# AdMob App ID (production)
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5749803259882370~1482612480

# Formats de build
android.release_artifact = apk
android.debug_artifact = apk
android.archs = arm64-v8a
# Si tu veux supporter aussi les vieux devices 32 bits :
# android.archs = arm64-v8a, armeabi-v7a

# Dépendances Gradle (versions qui existent)
android.add_gradle_repositories = mavenCentral()
android.gradle_dependencies = com.google.android.gms:play-services-ads:23.6.0, com.android.billingclient:billing-ktx:8.0.0

# python-for-android
p4a.branch = master

# Signature release (garde tes secrets hors du repo)
android.release_keystore = googleplay.keystore
android.release_keystore_passwd = nunotheboss
android.release_keyalias = upload
android.release_keyalias_passwd = nunotheboss

[buildozer]
log_level = 2
warn_on_root = 1
