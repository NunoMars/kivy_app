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

version = 1.7

requirements = python3,kivy==2.3.0,pillow==10.0.0

icon.filename = %(source.dir)s/tarot_img/icon.png
orientation = portrait

fullscreen = 0

author = © Nuno Marcelino Copyright Info

## Android spécificités
# (gérées automatiquement par le workflow, doublons supprimés)
android.minapi = 21
android.ndk_api = 21
android.api = 34
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

## Format d'export (géré par le workflow)

## Dépendances gradle avec versions récentes (Play Store compliance)
android.gradle_dependencies = androidx.annotation:annotation:1.6.0, androidx.fragment:fragment:1.5.7


[buildozer]
log_level = 2
warn_on_root = 1
