#!/usr/bin/env python3
"""
Validation finale - Vérifier que le problème de signature est résolu.
"""
import os
import sys


def check_gitignore():
    """Vérifier que .gitignore protège les clés"""
    print("🔍 Vérification .gitignore...")
    
    if not os.path.exists(".gitignore"):
        print("❌ .gitignore manquant")
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
    
    required_entries = ["*.keystore", "keystore.base64", "production.keystore"]
    
    for entry in required_entries:
        if entry in content:
            print(f"✅ {entry} ignoré")
        else:
            print(f"❌ {entry} non ignoré - RISQUE DE SÉCURITÉ")
            return False
    
    return True


def check_workflow_signature():
    """Vérifier que le workflow gère la signature"""
    print("\n🔍 Vérification workflow signature...")
    
    workflow_file = ".github/workflows/publish-android.yml"
    if not os.path.exists(workflow_file):
        print(f"❌ {workflow_file} manquant")
        return False
    
    with open(workflow_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ("ANDROID_KEYSTORE_BASE64", "Secret clé keystore"),
        ("jarsigner -verify", "Vérification signature"),
        ("keytool -list", "Validation clé"),
        ("production.keystore", "Clé de production"),
    ]
    
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ {description}: OK")
        else:
            print(f"❌ {description}: MANQUANT")
            return False
    
    return True


def check_guides():
    """Vérifier que les guides sont présents"""
    print("\n🔍 Vérification guides...")
    
    guides = [
        ("SIGNING_KEY_SOLUTION.md", "Solution signature"),
        ("MANUAL_SIGNING_GUIDE.md", "Guide manuel"),
        ("generate_signing_key.py", "Générateur de clé"),
    ]
    
    for file, description in guides:
        if os.path.exists(file):
            print(f"✅ {description}: {file}")
        else:
            print(f"❌ {description}: {file} manquant")
            return False
    
    return True


def check_secrets_instructions():
    """Afficher les instructions pour les secrets GitHub"""
    print("\n🔑 SECRETS GITHUB REQUIS")
    print("=" * 50)
    print("Pour résoudre l'erreur 'AAB doit être signé', configurez :")
    print()
    print("1. ANDROID_KEYSTORE_BASE64")
    print("   → Clé .keystore encodée en base64")
    print()
    print("2. KEYSTORE_PASSWORD") 
    print("   → Mot de passe du keystore")
    print()
    print("3. KEY_ALIAS")
    print("   → Alias de la clé (ex: macartedetarot)")
    print()
    print("4. KEY_PASSWORD")
    print("   → Mot de passe de la clé")
    print()
    print("📋 Étapes :")
    print("   1. Générer clé : python generate_signing_key.py")
    print("   2. Configurer secrets dans GitHub Settings")
    print("   3. Créer tag : git tag v1.0.1 && git push origin v1.0.1")
    print("   4. L'AAB sera correctement signé !")


def main():
    """Point d'entrée principal"""
    print("🔐 Validation Solution Signature AAB")
    print("=" * 50)
    
    checks = [
        ("Protection .gitignore", check_gitignore),
        ("Workflow signature", check_workflow_signature), 
        ("Guides disponibles", check_guides),
    ]
    
    all_good = True
    for name, check_func in checks:
        if not check_func():
            all_good = False
    
    check_secrets_instructions()
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ CONFIGURATION SIGNATURE PRÊTE !")
        print("🔑 Il ne reste qu'à configurer les secrets GitHub")
        print("📋 Suivez MANUAL_SIGNING_GUIDE.md pour les étapes")
        print()
        print("🎯 Une fois configuré :")
        print("   → Plus d'erreur 'AAB doit être signé'")  
        print("   → Upload Google Play Console réussi")
        print("   → Publication automatique fonctionnelle")
        return 0
    else:
        print("❌ CONFIGURATION INCOMPLÈTE")
        print("🔧 Corrigez les problèmes ci-dessus")
        return 1


if __name__ == '__main__':
    sys.exit(main())
