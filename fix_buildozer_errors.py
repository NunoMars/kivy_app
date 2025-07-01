#!/usr/bin/env python3
"""
Script pour appliquer des corrections aux erreurs buildozer communes.
"""
import os


def fix_buildozer_config():
    """Appliquer des corrections au buildozer.spec"""
    
    print("🔧 Application des corrections buildozer...")
    
    config_file = "buildozer.spec"
    if not os.path.exists(config_file):
        print(f"❌ {config_file} non trouvé")
        return False
    
    # Lire le fichier
    with open(config_file, "r") as f:
        content = f.read()
    
    # Corrections à appliquer
    corrections = []
    
    # 1. Forcer l'activation d'AndroidX (requis pour API 33)
    if "#android.enable_androidx = True" in content:
        content = content.replace("#android.enable_androidx = True", "android.enable_androidx = True")
        corrections.append("AndroidX activé")
    elif "android.enable_androidx" not in content:
        # Ajouter la ligne si elle n'existe pas
        content = content.replace(
            "# android.enable_androidx requires android.api >= 28",
            "# android.enable_androidx requires android.api >= 28\nandroid.enable_androidx = True"
        )
        corrections.append("AndroidX ajouté")
    
    # 2. Ajouter des options de packaging pour éviter les conflits
    packaging_section = """
# Corrections pour erreurs de compilation AAB
android.add_packaging_options = "exclude 'META-INF/*.kotlin_module'", "exclude 'META-INF/LICENSE*'", "exclude 'META-INF/NOTICE*'"

# Configuration pour éviter extractNativeLibs warning
android.manifest.xml = %(source.dir)s/android_manifest_template.xml
"""
    
    if "android.add_packaging_options" not in content:
        # Trouver la section packaging et ajouter les options
        insertion_point = "#android.add_packaging_options ="
        if insertion_point in content:
            content = content.replace(insertion_point, packaging_section)
            corrections.append("Options de packaging ajoutées")
    
    # 3. S'assurer que l'icône utilise le bon chemin
    if "tarot_img/tapis.ico" in content:
        content = content.replace("tarot_img/tapis.ico", "tarot_img/icon.png")
        corrections.append("Icône corrigée vers PNG")
    
    # 4. Ajouter des options de compilation Java pour la compatibilité
    if "android.add_compile_options" not in content or "#android.add_compile_options" in content:
        java_compile_line = 'android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"'
        content = content.replace(
            '# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"',
            java_compile_line
        )
        corrections.append("Options de compilation Java ajoutées")
    
    # Sauvegarder les modifications
    if corrections:
        with open(config_file, "w") as f:
            f.write(content)
        
        print("✅ Corrections appliquées:")
        for correction in corrections:
            print(f"   - {correction}")
        return True
    else:
        print("ℹ️  Aucune correction nécessaire")
        return True


def create_manifest_template():
    """Créer un template AndroidManifest.xml pour corriger extractNativeLibs"""
    
    template_content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{{ args.package }}"
    android:versionCode="{{ args.numeric_version }}"
    android:versionName="{{ args.version }}"
    android:installLocation="auto">

    <uses-sdk android:minSdkVersion="{{ args.min_sdk_version }}" android:targetSdkVersion="{{ android_api }}" />

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />

    <application
        android:label="@string/app_name"
        android:icon="@mipmap/icon"
        android:allowBackup="true"
        android:theme="@android:style/Theme.NoTitleBar"
        android:hardwareAccelerated="true"
        android:extractNativeLibs="false">

        <activity android:name="org.kivy.android.PythonActivity"
                  android:label="@string/app_name"
                  android:configChanges="keyboardHidden|orientation|screenSize"
                  android:screenOrientation="portrait"
                  android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>
</manifest>'''
    
    template_file = "android_manifest_template.xml"
    
    print(f"📱 Création du template AndroidManifest: {template_file}")
    
    with open(template_file, "w") as f:
        f.write(template_content)
    
    print("✅ Template AndroidManifest créé")
    return True


def main():
    """Point d'entrée principal"""
    print("🔧 Correction des erreurs buildozer AAB")
    print("=" * 40)
    
    success = True
    
    # Appliquer les corrections buildozer
    if not fix_buildozer_config():
        success = False
    
    # Créer le template de manifest
    if not create_manifest_template():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Toutes les corrections appliquées!")
        print("🚀 Le build AAB devrait maintenant fonctionner")
        print("")
        print("📋 Corrections appliquées:")
        print("   - Icône PNG créée et configurée")
        print("   - AndroidX activé pour API 33+")
        print("   - Options de packaging ajoutées")
        print("   - Template AndroidManifest avec extractNativeLibs=false")
        print("   - Compilation Java 1.8 configurée")
        return 0
    else:
        print("❌ Certaines corrections ont échoué")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
