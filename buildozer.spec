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

version = 1.4

requirements = python3,kivy==2.2.0,pillow

icon.filename = %(source.dir)s/tarot_img/icon.png
orientation = portrait

fullscreen = 0

author = © Nuno Marcelino Copyright Info

# Android spécificités
android.api = 33
android.minapi = 21
android.ndk = 25c
android.ndk_api = 21
android.skip_update = False
android.accept_sdk_license = True
android.enable_androidx = True
android.allow_backup = True
android.copy_libs = 1
android.logcat_filters = *:S python:D

# Format d’export
android.release_artifact = aab
android.debug_artifact = apk

# Dépendance gradle simple (nécessaire pour certaines compatibilités internes)
android.gradle_dependencies = com.android.support:support-v4:28.0.0

# Signature CI/CD — injectée dynamiquement via GitHub Actions (ne pas décommenter ici)
# android.release_keystore = %(source.dir)s/signing.keystore
# android.release_keystore_passwd = VOTRE_MOT_DE_PASSE_KEYSTORE
# android.release_key = upload
# android.release_key_passwd = VOTRE_MOT_DE_PASSE_CLE

# Signature locale pour builds Windows (décommentez après création du keystore)
android.release_keystore = %(source.dir)s/release.keystore
android.release_keystore_passwd = VOTRE_MOT_DE_PASSE_KEYSTORE
android.release_key = upload
android.release_key_passwd = VOTRE_MOT_DE_PASSE_CLE


[buildozer]
log_level = 2
warn_on_root = 1