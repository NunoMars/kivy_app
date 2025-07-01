#!/usr/bin/env python3
"""
Script de validation du workflow AAB avant push GitHub.
Vérifie que tous les composants nécessaires sont en place.
"""
import os
import sys


def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} manquant: {filepath}")
        return False


def check_buildozer_config():
    """Vérifie la configuration buildozer.spec"""
    print("\n🔍 Vérification buildozer.spec...")
    
    if not os.path.exists("buildozer.spec"):
        print("❌ buildozer.spec non trouvé")
        return False
    
    with open("buildozer.spec", "r") as f:
        content = f.read()
    
    checks = [
        ("android.release_artifact = aab", "Configuration AAB en release"),
        ("android.debug_artifact = apk", "Configuration APK en debug"),
        ("android.ndk = 25c", "Version NDK 25c"),
        ("android.api = 33", "API Level 33"),
        ("requirements = python3,kivy", "Requirements Kivy"),
    ]
    
    all_good = True
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ {description}: OK")
        else:
            print(f"❌ {description}: MANQUANT")
            print(f"   Recherché: {pattern}")
            all_good = False
    
    return all_good


def check_workflow_files():
    """Vérifie les fichiers workflow GitHub Actions"""
    print("\n🔍 Vérification workflows GitHub Actions...")
    
    workflows = [
        (".github/workflows/publish-android.yml", "Workflow publication Android"),
        (".github/workflows/build-android.yml", "Workflow build Android"),
    ]
    
    all_good = True
    for filepath, description in workflows:
        if check_file_exists(filepath, description):
            # Vérifier le contenu
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(filepath, "r", encoding="latin-1") as f:
                        content = f.read()
                except Exception as e:
                    print(f"   ❌ Impossible de lire le fichier: {e}")
                    all_good = False
                    continue
            
            # Vérifications spécifiques pour publish-android.yml
            if "publish-android.yml" in filepath:
                required_steps = [
                    "buildozer android release",
                    "keytool -genkey",
                    "macartedetarot-production.aab",
                    "Sign Release AAB",
                ]
                
                for step in required_steps:
                    if step in content:
                        print(f"   ✅ Contient: {step}")
                    else:
                        print(f"   ❌ Manque: {step}")
                        all_good = False
        else:
            all_good = False
    
    return all_good


def check_scripts():
    """Vérifie les scripts de support"""
    print("\n🔍 Vérification scripts de support...")
    
    scripts = [
        (".github/scripts/configure_buildozer_sdk.py", "Configuration SDK/NDK"),
        (".github/scripts/fix_sdk_paths.py", "Diagnostic SDK"),
        (".github/scripts/test_aab_config.py", "Test configuration AAB"),
    ]
    
    all_good = True
    for filepath, description in scripts:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good


def check_kivy_files():
    """Vérifie les fichiers Kivy de base"""
    print("\n🔍 Vérification fichiers Kivy...")
    
    files = [
        ("main.py", "Point d'entrée application"),
        ("macartedetarotapp.kv", "Interface Kivy"),
        ("signification.py", "Module signification"),
        ("requirements.txt", "Requirements Python"),
    ]
    
    all_good = True
    for filepath, description in files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good


def check_images():
    """Vérifie les ressources images"""
    print("\n🔍 Vérification ressources images...")
    
    if os.path.exists("tarot_img"):
        images = len([f for f in os.listdir("tarot_img") if f.endswith(('.jpg', '.png', '.gif'))])
        print(f"✅ Dossier tarot_img: {images} images trouvées")
        
        # Vérifier l'icône
        if os.path.exists("tarot_img/tapis.ico"):
            print("✅ Icône application: tarot_img/tapis.ico")
        else:
            print("❌ Icône application manquante: tarot_img/tapis.ico")
            return False
        
        return True
    else:
        print("❌ Dossier tarot_img manquant")
        return False


def generate_summary():
    """Génère un résumé de la configuration"""
    print("\n📋 RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 50)
    print("🎯 Objectif: Générer AAB pour Google Play Store")
    print("🛠️  Mode build:")
    print("   - Debug: APK (buildozer android debug)")
    print("   - Release: AAB (buildozer android release)")
    print("🔧 Configuration:")
    print("   - Ubuntu 22.04 dans GitHub Actions")
    print("   - Java 17, Android NDK 25c, API 33")
    print("   - Kivy 2.2.0, python-for-android 2023.5.21")
    print("🔑 Signature:")
    print("   - Clé temporaire si pas de secrets configurés")
    print("   - Clé production si secrets GitHub configurés")
    print("📦 Artefacts:")
    print("   - AAB uploadé vers GitHub Releases")
    print("   - AAB publié sur Google Play Console")
    print("")


def main():
    """Point d'entrée principal"""
    print("🔧 Validation Workflow AAB pour Ma Carte de Tarot")
    print("=" * 60)
    
    checks = [
        ("Fichiers Kivy", check_kivy_files),
        ("Images et ressources", check_images),
        ("Configuration buildozer", check_buildozer_config),
        ("Workflows GitHub Actions", check_workflow_files),
        ("Scripts de support", check_scripts),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Erreur lors de {name}: {e}")
            all_passed = False
    
    generate_summary()
    
    print("=" * 60)
    if all_passed:
        print("✅ VALIDATION RÉUSSIE!")
        print("🚀 Le workflow est prêt pour générer des AAB")
        print("")
        print("📋 Prochaines étapes:")
        print("   1. git add .")
        print("   2. git commit -m 'feat: workflow AAB prêt pour Google Play'")
        print("   3. git push origin main")
        print("   4. Créer un tag pour déclencher la publication:")
        print("      git tag v1.0.0")
        print("      git push origin v1.0.0")
        print("")
        print("🔑 Pour la signature de production:")
        print("   - Configurer les secrets GitHub (ANDROID_KEYSTORE_BASE64, etc.)")
        print("   - Configurer GOOGLE_PLAY_SERVICE_ACCOUNT pour auto-publication")
        return 0
    else:
        print("❌ VALIDATION ÉCHOUÉE!")
        print("🔧 Corrigez les problèmes ci-dessus avant de continuer")
        return 1


if __name__ == '__main__':
    sys.exit(main())
