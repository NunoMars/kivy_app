#!/usr/bin/env python3
"""
Script de vérification rapide de la compatibilité NDK pour SDL2.
Vérifie si la version NDK configurée est compatible avec SDL2/Kivy.
"""
import os
import sys


def check_ndk_compatibility():
    """Vérifie la compatibilité NDK avec SDL2"""
    
    print("🔍 Vérification de la compatibilité NDK avec SDL2")
    print("=" * 50)
    
    # Variables d'environnement
    android_ndk = os.environ.get('ANDROID_NDK_HOME')
    
    if not android_ndk:
        print("❌ ANDROID_NDK_HOME non défini")
        return False
    
    print(f"📱 NDK Path: {android_ndk}")
    
    # Vérifier l'existence du NDK
    if not os.path.exists(android_ndk):
        print(f"❌ NDK non trouvé: {android_ndk}")
        return False
    
    # Extraire la version NDK du chemin
    ndk_version = None
    if "25.2.9519653" in android_ndk:
        ndk_version = "25c"
        print("✅ NDK 25c détecté (compatible SDL2)")
    elif "27.2.12479018" in android_ndk:
        ndk_version = "27"
        print("⚠️  NDK 27 détecté (incompatible SDL2 - erreurs ALooper_pollAll)")
    else:
        print("❓ Version NDK inconnue")
    
    # Vérifier les fichiers source NDK critiques
    source_props = os.path.join(android_ndk, "source.properties")
    if os.path.exists(source_props):
        print("📄 Lecture source.properties...")
        try:
            with open(source_props, 'r') as f:
                for line in f:
                    if line.startswith('Pkg.Revision'):
                        revision = line.split('=')[1].strip()
                        print(f"   Révision: {revision}")
                        break
        except Exception as e:
            print(f"❌ Erreur lecture source.properties: {e}")
    
    # Vérifier les toolchains
    toolchain_path = os.path.join(android_ndk, "toolchains", "llvm", "prebuilt")
    if os.path.exists(toolchain_path):
        print("✅ Toolchain LLVM trouvé")
        toolchain_dirs = os.listdir(toolchain_path)
        if toolchain_dirs:
            print(f"   Architectures: {toolchain_dirs}")
    else:
        print("❌ Toolchain LLVM non trouvé")
    
    # Recommandations basées sur la version
    print("\n🎯 Recommandations:")
    if ndk_version == "25c":
        print("✅ Configuration optimale pour SDL2/Kivy")
        print("   - Pas de problèmes ALooper_pollAll attendus")
        print("   - Compatible avec python-for-android")
        return True
    elif ndk_version == "27":
        print("❌ Configuration problématique pour SDL2/Kivy")
        print("   - Erreurs ALooper_pollAll probables")
        print("   - Recommandation: downgrade vers NDK 25c")
        print("   - Commande: sdkmanager 'ndk;25.2.9519653'")
        return False
    else:
        print("❓ Compatibilité inconnue - tester avec précaution")
        return False


def check_buildozer_config():
    """Vérifie la configuration buildozer.spec"""
    
    print("\n📋 Vérification buildozer.spec")
    print("=" * 30)
    
    if not os.path.exists("buildozer.spec"):
        print("❌ buildozer.spec non trouvé")
        return False
    
    ndk_configs = []
    with open("buildozer.spec", 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if any(keyword in line for keyword in ['android.ndk', 'android.ndk_path']):
                ndk_configs.append(f"   {line_num:3d}: {line}")
    
    if ndk_configs:
        print("📱 Configuration NDK dans buildozer.spec:")
        for config in ndk_configs:
            print(config)
            if "25" in config:
                print("       ✅ NDK 25c configuré")
            elif "27" in config:
                print("       ⚠️  NDK 27 configuré (problématique)")
    else:
        print("❌ Aucune configuration NDK trouvée dans buildozer.spec")
    
    return len(ndk_configs) > 0


def main():
    """Point d'entrée principal"""
    print("🔧 Vérification compatibilité NDK pour SDL2/Kivy")
    print("=" * 60)
    
    ndk_ok = check_ndk_compatibility()
    config_ok = check_buildozer_config()
    
    print("\n" + "=" * 60)
    
    if ndk_ok and config_ok:
        print("✅ Configuration NDK optimale pour SDL2/Kivy")
        print("   Le build Android devrait fonctionner sans erreurs SDL2")
        return 0
    else:
        print("❌ Problèmes de configuration NDK détectés")
        print("   Risque d'erreurs SDL2 pendant le build")
        print("\n🔧 Actions recommandées:")
        if not ndk_ok:
            print("   1. Installer NDK 25c: sdkmanager 'ndk;25.2.9519653'")
            print("   2. Mettre à jour ANDROID_NDK_HOME")
        if not config_ok:
            print("   3. Mettre à jour buildozer.spec avec NDK 25c")
            print("   4. Exécuter configure_buildozer_sdk.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())
