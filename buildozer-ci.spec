[app]

# (str) Title of your application
title = Ma Carte De Tarot

# (str) Package name
package.name = macartedetarot

# (str) Package domain (needed for android/ios packaging)
package.domain = org.tarot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,gif,kv,atlas

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,md,txt

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .github, __pycache__, .git, .vscode, guides

# (str) Application versioning (method 1)
version = 1.4

# (list) Application requirements - Version optimisée pour CI
requirements = python3,kivy==2.2.0,pillow

# (str) Icon of the application
icon.filename = %(source.dir)s/tarot_img/tapis.ico

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# OSX Specific
#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (list) Android application meta-data to set (key=value format)
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713

# (int) Target Android API - Utiliser 33 pour éviter les problèmes NDK 27
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use - Version stable avec SDL2
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (str) Bootstrap to use for android builds
android.bootstrap = sdl2

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filter in your main activity
#android.manifest.intent_filters = 

# (str) launchMode to set for the main activity
android.manifest.launch_mode = standard

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# (str) Path to a custom whitelist file
#android.whitelist = 

# (str) Path to a custom blacklist file
#android.blacklist = 

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
#android.uses_library = 

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# android.enable_androidx requires android.api >= 28
android.enable_androidx = False

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk or aar).
# 'aab' files can be uploaded directly to the Play Store.
# 'apk' files can be installed directly on Android devices.
android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (list) python-for-android whitelist
#p4a.whitelist =

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android fork to use in case if you have custom fork
# p4a.fork = kivy

# (str) python-for-android URL to use for cloning
#p4a.url = https://github.com/kivy/python-for-android.git


#    -----------------------------------------------------------------------------
#    BUILDOZER CI CONFIGURATION
#    -----------------------------------------------------------------------------

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, for the Python-for-android project
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
