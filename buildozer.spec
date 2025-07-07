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

version = 1.6

requirements = python3,kivy==2.2.0,pillow

icon.filename = %(source.dir)s/tarot_img/icon.png
orientation = all

fullscreen = 0

author = © Nuno Marcelino Copyright Info

# Android spécificités
android.api = 34
android.minapi = 21
android.ndk = 25c
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
android.gradle_dependencies = androidx.annotation:annotation:1.7.1, androidx.fragment:fragment:1.6.2, com.android.support:support-v4:28.0.0

# Signature locale pour Windows (configurée avec le keystore googleplay.keystore)
# ATTENTION: Ces lignes contiennent des mots de passe en clair - à utiliser uniquement en local
# Pour CI/CD, ces valeurs sont injectées automatiquement via les secrets GitHub
android.release_keystore = %(source.dir)s/googleplay.keystore
android.release_keystore_passwd = nunotheboss
android.release_key = upload
android.release_key_passwd = nunotheboss



[buildozer]
log_level = 2
warn_on_root = 1