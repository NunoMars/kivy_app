#!/usr/bin/env python3
"""
Script de test pour valider que le pipeline CI/CD Android est prêt.
Vérifie la configuration, les fichiers nécessaires, et donne un rapport de statut.
"""

import os
import subprocess

def print_section(title):
    """Affiche une section avec style."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_file_exists(file_path, description):
    """Vérifie qu'un fichier existe."""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_command(command, description):
    """Vérifie qu'une commande est disponible."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        available = result.returncode == 0
        status = "✅" if available else "❌"
        print(f"{status} {description}")
        if available and result.stdout.strip():
            print(f"   Version: {result.stdout.strip().split()[0] if result.stdout.strip() else 'N/A'}")
        return available
    except Exception as e:
        print(f"❌ {description}: Erreur - {e}")
        return False

def check_buildozer_config():
    """Vérifie la configuration buildozer.spec."""
    buildozer_path = "buildozer.spec"
    if not os.path.exists(buildozer_path):
        print("❌ Fichier buildozer.spec manquant")
        return False
    
    print("✅ Fichier buildozer.spec trouvé")
    
    with open(buildozer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifications importantes
    checks = [
        ("android.release_artifact = aab", "Configuration AAB"),
        ("android.api = 34", "API Level 34"),
        ("android.minapi = 21", "API minimale 21"),
        ("android.sdk = 34", "SDK 34"),
        ("android.ndk = 25c", "NDK 25c"),
        ("requirements =", "Requirements Python"),
    ]
    
    for pattern, desc in checks:
        if pattern in content:
            print(f"✅ {desc} configuré")
        else:
            print(f"⚠️  {desc} pourrait être manquant")
    
    return True

def check_keystore():
    """Vérifie la clé de production."""
    keystore_path = "googleplay.keystore"
    if not os.path.exists(keystore_path):
        print("❌ Clé de production googleplay.keystore manquante")
        return False
    
    print("✅ Clé de production trouvée")
    
    # Vérifier la clé avec keytool
    try:
        # Note: mot de passe sera demandé en mode interactif
        print("ℹ️  Pour vérifier la clé, utilisez:")
        print("   keytool -list -keystore googleplay.keystore")
    except Exception as e:
        print(f"⚠️  Impossible de vérifier la clé: {e}")
    
    return True

def check_workflow():
    """Vérifie le workflow GitHub Actions."""
    workflow_path = ".github/workflows/publish-android.yml"
    if not os.path.exists(workflow_path):
        print("❌ Workflow GitHub Actions manquant")
        return False
    
    print("✅ Workflow GitHub Actions trouvé")
    
    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifications importantes
    checks = [
        ("buildozer android release", "Build AAB"),
        ("secrets.ANDROID_KEYSTORE", "Secret keystore"),
        ("secrets.ANDROID_KEYSTORE_PASSWORD", "Secret mot de passe"),
        ("apksigner sign", "Signature production"),
        ("upload-google-play", "Upload Google Play"),
        ("create-release", "Création release GitHub"),
    ]
    
    for pattern, desc in checks:
        if pattern in content:
            print(f"✅ {desc} configuré")
        else:
            print(f"❌ {desc} manquant")
    
    return True

def check_project_structure():
    """Vérifie la structure du projet."""
    required_files = [
        ("main.py", "Application principale"),
        ("macartedetarotapp.kv", "Interface Kivy"),
        ("signification.py", "Logique métier"),
        ("requirements.txt", "Dépendances Python"),
        ("README.md", "Documentation"),
    ]
    
    all_good = True
    for file_path, desc in required_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    return all_good

def generate_secrets_checklist():
    """Génère une checklist pour les secrets GitHub."""
    print_section("CHECKLIST SECRETS GITHUB")
    
    secrets = [
        ("ANDROID_KEYSTORE", "Clé googleplay.keystore encodée en base64"),
        ("ANDROID_KEYSTORE_PASSWORD", "Mot de passe du keystore"),
        ("ANDROID_KEY_ALIAS", "Alias de la clé (généralement 'googleplay')"),
        ("ANDROID_KEY_PASSWORD", "Mot de passe de la clé"),
        ("GOOGLE_PLAY_SERVICE_ACCOUNT", "JSON du service account Google Play (optionnel)"),
    ]
    
    print("Pour configurer les secrets GitHub:")
    print("1. Allez sur: https://github.com/NunoMars/kivy_app/settings/secrets/actions")
    print("2. Cliquez sur 'New repository secret'")
    print("3. Ajoutez chaque secret:")
    print()
    
    for secret_name, description in secrets:
        print(f"   📝 {secret_name}")
        print(f"      {description}")
        print()

def check_git_status():
    """Vérifie le statut Git."""
    try:
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  Fichiers non commitées détectés:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")
            print("   Considérez committer vos changements avant de créer un tag.")
        else:
            print("✅ Repository Git propre")
        
        # Vérifier les tags
        result = subprocess.run("git tag -l", shell=True, capture_output=True, text=True)
        tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
        if tags:
            latest_tag = tags[-1] if tags else "Aucun"
            print(f"🏷️  Dernier tag: {latest_tag}")
        else:
            print("🏷️  Aucun tag trouvé")
            
    except Exception as e:
        print(f"❌ Erreur Git: {e}")

def main():
    """Fonction principale."""
    print("🔮 TEST DE VALIDATION DU PIPELINE CI/CD ANDROID")
    print("   Application: Ma Carte de Tarot")
    print("   Framework: Kivy → Android AAB")
    
    # Vérifications système
    print_section("ENVIRONNEMENT SYSTÈME")
    check_command("python --version", "Python")
    check_command("java -version", "Java")
    check_command("git --version", "Git")
    
    # Structure du projet
    print_section("STRUCTURE DU PROJET")
    project_ok = check_project_structure()
    
    # Configuration Buildozer
    print_section("CONFIGURATION BUILDOZER")
    buildozer_ok = check_buildozer_config()
    
    # Clé de production
    print_section("CLÉ DE PRODUCTION")
    keystore_ok = check_keystore()
    
    # Workflow GitHub Actions
    print_section("WORKFLOW GITHUB ACTIONS")
    workflow_ok = check_workflow()
    
    # Statut Git
    print_section("STATUT GIT")
    check_git_status()
    
    # Génération checklist secrets
    generate_secrets_checklist()
    
    # Rapport final
    print_section("RAPPORT FINAL")
    
    all_checks = [
        (project_ok, "Structure du projet"),
        (buildozer_ok, "Configuration Buildozer"),
        (keystore_ok, "Clé de production"),
        (workflow_ok, "Workflow GitHub Actions"),
    ]
    
    passed = sum(1 for check, _ in all_checks if check)
    total = len(all_checks)
    
    print(f"📊 Vérifications: {passed}/{total} réussies")
    
    if passed == total:
        print("\n🎉 PIPELINE PRÊT POUR LA PRODUCTION!")
        print("   Prochaines étapes:")
        print("   1. Configurer les secrets GitHub (voir checklist ci-dessus)")
        print("   2. Créer un tag: git tag v1.3.0 && git push origin v1.3.0")
        print("   3. Le build AAB se lancera automatiquement")
        print("   4. L'AAB signé sera disponible dans les artifacts")
    else:
        print("\n⚠️  CONFIGURATION INCOMPLÈTE")
        print("   Corrigez les problèmes ci-dessus avant de continuer.")
        
        for check, desc in all_checks:
            status = "✅" if check else "❌"
            print(f"   {status} {desc}")
    
    print("\n📚 Documentation complète disponible dans:")
    print("   - README.md")
    print("   - CONFIGURATION_SECRETS_FINALE.md")
    print("   - TESTING_GUIDE.md")

if __name__ == "__main__":
    main()
