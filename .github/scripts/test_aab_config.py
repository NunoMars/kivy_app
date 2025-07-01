#!/usr/bin/env python3
"""
Script pour tester la configuration AAB/APK avec buildozer.
Vérifie les paramètres qui déterminent le format de sortie.
"""
import os


def check_buildozer_artifacts():
    """Vérifie la configuration des artefacts buildozer"""
    
    print("🔍 Vérification Configuration Artefacts Buildozer")
    print("=" * 55)
    
    if not os.path.exists("buildozer.spec"):
        print("❌ buildozer.spec non trouvé")
        return False
    
    with open("buildozer.spec", "r") as f:
        content = f.read()
    
    # Rechercher les configurations d'artefacts
    debug_artifact = None
    release_artifact = None
    
    for line in content.split('\n'):
        if line.strip().startswith('android.debug_artifact'):
            debug_artifact = line.split('=')[1].strip()
        elif line.strip().startswith('android.release_artifact'):
            release_artifact = line.split('=')[1].strip()
    
    print("📱 Configuration des artefacts:")
    print(f"   Debug: {debug_artifact or 'NON DÉFINI'}")
    print(f"   Release: {release_artifact or 'NON DÉFINI'}")
    
    # Vérifications
    if debug_artifact == "apk":
        print("   ✅ Debug APK - Correct")
    else:
        print(f"   ⚠️  Debug {debug_artifact} - Devrait être 'apk'")
    
    if release_artifact == "aab":
        print("   ✅ Release AAB - Correct")
    else:
        print(f"   ❌ Release {release_artifact} - Devrait être 'aab'")
    
    # Rechercher les configurations de signature
    print("\n🔑 Configuration de signature:")
    signature_configs = []
    
    for line_num, line in enumerate(content.split('\n'), 1):
        if any(keyword in line for keyword in [
            'android.release_keystore', 'android.debug_keystore',
            'android.release_key', 'android.debug_key'
        ]):
            if not line.strip().startswith('#'):
                signature_configs.append(f"   {line_num:3d}: {line.strip()}")
    
    if signature_configs:
        print("   Configurations trouvées:")
        for config in signature_configs:
            print(config)
    else:
        print("   ❌ Aucune configuration de signature trouvée")
    
    # Conseils pour forcer AAB
    print("\n💡 Pour forcer la génération d'AAB:")
    print("   1. Vérifier android.release_artifact = aab")
    print("   2. Utiliser 'buildozer android release' (pas debug)")
    print("   3. S'assurer que les secrets de signature sont configurés")
    print("   4. Vérifier les logs pour 'Building AAB' vs 'Building APK'")
    
    return True


def suggest_buildozer_commands():
    """Suggère les commandes buildozer appropriées"""
    
    print("\n🛠️  Commandes Buildozer Recommandées")
    print("=" * 40)
    
    print("📱 Pour générer un APK debug:")
    print("   buildozer android debug")
    print("   → bin/[app]-debug.apk")
    
    print("\n📱 Pour générer un AAB release:")
    print("   buildozer android release")
    print("   → bin/[app]-release.aab (si android.release_artifact = aab)")
    
    print("\n🔍 Pour vérifier la configuration:")
    print("   buildozer android debug --verbose")
    print("   → Logs détaillés du processus de build")
    
    print("\n🧹 Pour nettoyer avant rebuild:")
    print("   buildozer android clean")
    print("   → Supprime le cache et force rebuild complet")


def main():
    """Point d'entrée principal"""
    print("🔧 Test Configuration AAB/APK Buildozer")
    print("=" * 50)
    
    check_buildozer_artifacts()
    suggest_buildozer_commands()
    
    print("\n" + "=" * 50)
    print("✅ Vérification terminée")
    print("\n💡 Rappel: AAB uniquement disponible en mode release !")


if __name__ == '__main__':
    main()
