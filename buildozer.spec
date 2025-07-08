[app]

title = Ma Carte De Tarot
package.name = macartedetarot
package.domain = org.tarot
source.dir = .

# Architecture Android ciblée
android.archs = arm64-v8a

# Inclusions
source.include_exts = py,png,jpg,gif,kv,atlas
source.exclude_exts = spec,md,txt
source.exclude_dirs = tests, bin, venv, .github, __pycache__, .git, .vscode, guides

version = 1.7.1

requirements = python3,kivy==2.2.0,pillow

icon.filename = %(source.dir)s/tarot_img/icon.png
orientation = portrait

fullscreen = 0

author = © Nuno Marcelino Copyright Info

# Android spécificités - API level configuré automatiquement par CI/CD
android.api = 34
android.minapi = 21
android.ndk = 25.2.9519653
android.ndk_api = 21
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

# Format d’export
android.release_artifact = aab
android.debug_artifact = apk

# Dépendances gradle avec versions récentes (Play Store compliance)
android.gradle_dependencies = androidx.annotation:annotation:1.6.0, androidx.fragment:fragment:1.5.7

# Signature pour CI/CD - configurée automatiquement via secrets GitHub
# Les valeurs ci-dessous sont des placeholders et seront remplacées par le workflow
#android.release_keystore = %(source.dir)s/signing.keystore
#android.release_key = KEY_ALIAS_FROM_SECRETS
#android.release_key_passwd = KEY_PASSWORD_FROM_SECRETS
#android.release_keystore_passwd = KEYSTORE_PASSWORD_FROM_SECRETS



[buildozer]
log_level = 2
warn_on_root = 1