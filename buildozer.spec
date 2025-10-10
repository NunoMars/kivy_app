
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

version = 1.9

# Note: kivmob doit être inclus manuellement via libs/ car non disponible sur PyPI
requirements = python3,kivy==2.3.0,pillow==10.0.0,requests

icon.filename = %(source.dir)s/tarot_img/icon.png
orientation = portrait

fullscreen = 0

author = © Nuno Marcelino Copyright Info

## Android spécificités
# (gérées automatiquement par le workflow, doublons supprimés)
android.minapi = 21
android.ndk_api = 21
android.api = 35
android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1
android.logcat_filters = *:S python:D

# Support des écrans larges et appareils pliables (Android 16+)
# Permettre redimensionnement libre pour tablettes et pliables
android.allow_resize = True
android.resizeableActivity = True

# Autorisations pour Play Store compliance + AdMob
android.permissions = INTERNET,ACCESS_NETWORK_STATE,com.google.android.gms.permission.AD_ID

# AdMob App ID metadata
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=@string/admob_app_id

# Ressources Android pour AdMob
android.add_resources = resources/

## Format d'export (géré par le workflow)
# Format de build par défaut pour Play Store
android.release_artifact = aab
android.debug_artifact = aab

# Configuration de signature pour Play Store
android.keystore = %(source.dir)s/googleplay.keystore
android.keyalias = upload
android.keystorepw = nunotheboss
android.keyaliaspw = nunotheboss

# Configuration pour améliorer la qualité de l'app Play Store
# Activation de R8/ProGuard pour réduire la taille de l'app et des symboles de débogage
# + Google Play Services Ads pour AdMob (version compatible avec androidx)
android.gradle_dependencies = com.android.tools.build:gradle:8.1.1,com.google.android.gms:play-services-ads:21.5.0
android.add_gradle_configuration = 
    android {
        buildTypes {
            release {
                minifyEnabled true
                shrinkResources true
                proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
                ndk {
                    debugSymbolLevel 'SYMBOL_TABLE'
                }
            }
        }
    }

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