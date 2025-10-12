
[app]

title = Ma Carte De Tarot
package.name = macartedetarot
package.domain = org.tarot
source.dir = .

# Architecture Android ciblée
# (gérée automatiquement par le workflow, doublons supprimés)

# Inclusions
source.include_exts = py,png,jpg,gif,kv,atlas
source.exclude_exts = spec,md,txt
source.exclude_dirs = tests, bin, venv, .github, __pycache__, .git, .vscode, guides
source.include_patterns = libs/*.py

version = 1.11
android.numeric_version = 1110000

# Note: kivmob doit être inclus manuellement via libs/ car non disponible sur PyPI
requirements = python3==3.9.18,kivy==2.3.1,pillow==10.0.0,requests==2.32.3,gradio_client>=1.13.0,fsspec,httpx,huggingface-hub,websockets,typing-extensions

icon.filename = %(source.dir)s/tarot_img/icon.png
orientation = portrait

fullscreen = 0

author = © Nuno Marcelino Copyright Info

## Android spécificités
# (gérées automatiquement par le workflow, doublons supprimés)
android.minapi = 21
android.ndk_api = 21
android.api = 35
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1
android.logcat_filters = *:S python:D

# Autorisations pour Play Store compliance + AdMob + stabilité Android + achats in-app
android.permissions = INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID,WAKE_LOCK,VIBRATE,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE

# AdMob App ID metadata (production)
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-5749803259882370~1482612480

## Format d'export (géré par le workflow)
# Format de build par défaut pour Play Store
android.release_artifact = aab
android.debug_artifact = apk
android.release_keystore = %(source.dir)s/googleplay.keystore
android.release_keystore_passwd = nunotheboss
android.release_keyalias = upload
android.release_keyalias_passwd = nunotheboss

# Configuration pour améliorer la qualité de l'app Play Store
# Activation de R8/ProGuard pour réduire la taille de l'app et des symboles de débogage
# + Google Play Services Ads pour AdMob (version compatible avec androidx)
# Google Play Billing KTX (modern API) + AdMob
android.gradle_dependencies = com.google.android.gms:play-services-ads:21.5.0, implementation "com.android.billingclient:billing-ktx:8.0.0"

# Utiliser la branche master de python-for-android pour récupérer corrections récentes
# (corrige notamment des échecs de compilation OpenSSL avec toolchains récents)
p4a.branch = master

## Dépendances gradle avec versions récentes (Play Store compliance)
# Suppression des dépendances androidx pour éviter les conflits Kotlin
# android.gradle_dependencies = androidx.annotation:annotation:1.6.0, androidx.fragment:fragment:1.5.7

# Configuration pour résoudre les conflits Kotlin - DÉSACTIVÉ TEMPORAIREMENT
# android.add_gradle_configuration = 
#     configurations.all {
#         resolutionStrategy.eachDependency { details ->
#             if (details.requested.group == 'org.jetbrains.kotlin') {
#                 details.useVersion '1.8.22'
#             }
#         }
#     }


[buildozer]
log_level = 2
warn_on_root = 1