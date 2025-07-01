#!/usr/bin/env python3
"""
Script de diagnostic et correction des chemins SDK Android pour buildozer.
Créé pour résoudre les problèmes de chemin sdkmanager sur GitHub Actions.
"""
import os
import sys
import subprocess


def check_and_fix_sdk_paths():
    """Vérifie et corrige les chemins SDK Android"""
    
    print("🔍 Diagnostic des chemins SDK Android...")
    
    # Variables d'environnement
    android_home = os.environ.get('ANDROID_HOME')
    android_ndk = os.environ.get('ANDROID_NDK_HOME')
    
    print(f"ANDROID_HOME: {android_home}")
    print(f"ANDROID_NDK_HOME: {android_ndk}")
    print(f"PATH: {os.environ.get('PATH', '')[:200]}...")
    
    if not android_home:
        print("❌ ANDROID_HOME non défini")
        return False
    
    # Vérifier l'existence des répertoires
    paths_to_check = [
        (android_home, "SDK Android"),
        (android_ndk, "NDK Android (25c compatible SDL2)"),
        (f"{android_home}/cmdline-tools/latest/bin", "Command Line Tools"),
        (f"{android_home}/platform-tools", "Platform Tools"),
    ]
    
    for path, description in paths_to_check:
        if path and os.path.exists(path):
            print(f"✅ {description}: {path}")
        else:
            print(f"❌ {description}: {path} (non trouvé)")
    
    # Vérifier sdkmanager
    sdkmanager_paths = [
        f"{android_home}/cmdline-tools/latest/bin/sdkmanager",
        f"{android_home}/tools/bin/sdkmanager",
        "sdkmanager"  # Dans le PATH
    ]
    
    working_sdkmanager = None
    for path in sdkmanager_paths:
        if os.path.exists(path) or path == "sdkmanager":
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ sdkmanager fonctionnel: {path}")
                    working_sdkmanager = path
                    break
            except Exception as e:
                print(f"❌ sdkmanager échoué ({path}): {e}")
    
    if not working_sdkmanager:
        print("❌ Aucun sdkmanager fonctionnel trouvé")
        return False
    
    # Créer le lien symbolique pour l'ancien chemin (compatibilité buildozer)
    legacy_path = f"{android_home}/tools/bin/sdkmanager"
    modern_path = f"{android_home}/cmdline-tools/latest/bin/sdkmanager"
    
    if not os.path.exists(legacy_path) and os.path.exists(modern_path):
        print(f"🔗 Création du lien symbolique: {legacy_path} -> {modern_path}")
        os.makedirs(f"{android_home}/tools/bin", exist_ok=True)
        try:
            os.symlink(modern_path, legacy_path)
            print("✅ Lien symbolique créé avec succès")
        except Exception as e:
            print(f"❌ Échec création lien symbolique: {e}")
            # Essayer avec sudo si nécessaire
            try:
                subprocess.run(["sudo", "ln", "-sf", modern_path, legacy_path], check=True)
                print("✅ Lien symbolique créé avec sudo")
            except Exception as e2:
                print(f"❌ Échec avec sudo: {e2}")
                return False
    
    # Vérifier les licences Android
    print("\n📋 Vérification des licences Android...")
    try:
        license_dir = f"{android_home}/licenses"
        if os.path.exists(license_dir):
            licenses = os.listdir(license_dir)
            print(f"✅ Licences trouvées: {licenses}")
        else:
            print("❌ Répertoire des licences non trouvé")
            print("🔧 Tentative d'acceptation des licences...")
            result = subprocess.run(
                ["yes", "|", working_sdkmanager, "--licenses"],
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ Licences acceptées")
            else:
                print(f"❌ Échec acceptation licences: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur vérification licences: {e}")
    
    # Afficher la configuration buildozer
    print("\n📋 Configuration buildozer.spec actuelle:")
    try:
        with open("buildozer.spec", "r") as f:
            for line_num, line in enumerate(f, 1):
                if any(keyword in line for keyword in [
                    'android.sdk_path', 'android.ndk_path', 'android.ndk =', 
                    'android.api', 'requirements ='
                ]):
                    print(f"   {line_num:3d}: {line.strip()}")
    except FileNotFoundError:
        print("❌ buildozer.spec non trouvé")
    
    return True


def main():
    """Point d'entrée principal"""
    print("🔧 Diagnostic et correction des chemins SDK Android")
    print("=" * 60)
    
    success = check_and_fix_sdk_paths()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Diagnostic terminé avec succès")
        return 0
    else:
        print("❌ Des problèmes ont été détectés")
        return 1


if __name__ == '__main__':
    sys.exit(main())
