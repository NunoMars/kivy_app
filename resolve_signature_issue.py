#!/usr/bin/env python3
"""
Script final pour résoudre le problème de signature et déployer une version corrigée
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande avec gestion d'erreur"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - Succès")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None

def check_prerequisites():
    """Vérifie que tous les prérequis sont disponibles"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier que gh CLI est installé
    if not run_command("gh --version", "Vérification de GitHub CLI"):
        print("❌ GitHub CLI n'est pas installé. Installez-le depuis https://cli.github.com/")
        return False
    
    # Vérifier que l'utilisateur est connecté
    if not run_command("gh auth status", "Vérification de l'authentification GitHub"):
        print("❌ Vous n'êtes pas connecté à GitHub. Exécutez 'gh auth login'")
        return False
    
    # Vérifier que nous sommes dans un repo git
    if not run_command("git status", "Vérification du repository Git"):
        print("❌ Vous n'êtes pas dans un repository Git")
        return False
    
    return True

def configure_secrets(keystore_password, key_alias, key_password):
    """Configure les secrets GitHub"""
    print("🔐 Configuration des secrets GitHub...")
    
    # Lire le keystore encodé
    keystore_path = Path("keystore_base64.txt")
    if not keystore_path.exists():
        print("❌ Fichier keystore_base64.txt manquant. Exécutez d'abord configure_keystore_secrets.py")
        return False
    
    with open(keystore_path, "r") as f:
        keystore_base64 = f.read().strip()
    
    # Configurer chaque secret
    secrets = [
        ("ANDROID_KEYSTORE", keystore_base64),
        ("ANDROID_KEYSTORE_PASSWORD", keystore_password),
        ("ANDROID_KEY_ALIAS", key_alias),
        ("ANDROID_KEY_PASSWORD", key_password)
    ]
    
    for secret_name, secret_value in secrets:
        if not run_command(f'gh secret set {secret_name} --body "{secret_value}"', f"Configuration du secret {secret_name}"):
            return False
    
    return True

def create_and_push_tag(tag_name):
    """Crée et pousse un nouveau tag"""
    print(f"🏷️  Création du tag {tag_name}...")
    
    # Vérifier que le tag n'existe pas déjà
    existing_tags = run_command("git tag --list", "Vérification des tags existants")
    if existing_tags and tag_name in existing_tags:
        print(f"⚠️  Le tag {tag_name} existe déjà. Suppression...")
        run_command(f"git tag -d {tag_name}", f"Suppression du tag local {tag_name}")
        run_command(f"git push origin :refs/tags/{tag_name}", f"Suppression du tag distant {tag_name}")
    
    # Créer et pousser le nouveau tag
    if not run_command(f"git tag {tag_name}", f"Création du tag {tag_name}"):
        return False
    
    if not run_command(f"git push origin {tag_name}", f"Push du tag {tag_name}"):
        return False
    
    return True

def monitor_workflow():
    """Surveille l'exécution du workflow"""
    print("👀 Surveillance du workflow...")
    
    # Attendre un peu que le workflow se lance
    import time
    time.sleep(5)
    
    # Afficher les dernières exécutions
    run_command("gh run list --workflow=publish-android.yml --limit=3", "Affichage des dernières exécutions")
    
    print("\n🔍 Pour surveiller l'exécution en temps réel :")
    print("   gh run watch $(gh run list --workflow=publish-android.yml --limit=1 --json databaseId --jq '.[0].databaseId')")

def main():
    """Fonction principale"""
    print("🚀 Résolution finale du problème de signature Android")
    print("=" * 60)
    
    if not check_prerequisites():
        print("❌ Prérequis manquants. Veuillez les installer avant de continuer.")
        sys.exit(1)
    
    # Vérifier que configure_keystore_secrets.py a été exécuté
    if not Path("keystore_base64.txt").exists():
        print("❌ Le fichier keystore_base64.txt n'existe pas.")
        print("   Exécutez d'abord : python configure_keystore_secrets.py")
        sys.exit(1)
    
    # Vérifier que configure_secrets_final.ps1 existe
    if not Path("configure_secrets_final.ps1").exists():
        print("❌ Le fichier configure_secrets_final.ps1 n'existe pas.")
        print("   Exécutez d'abord : python configure_keystore_secrets.py")
        sys.exit(1)
    
    print("✅ Fichiers de configuration trouvés")
    
    # Demander confirmation des informations
    print("\n🔐 Informations pour les secrets GitHub :")
    print("Ces informations ont été générées par configure_keystore_secrets.py")
    
    keystore_password = input("🔐 Confirmez le mot de passe du keystore : ")
    key_alias = input("🔑 Confirmez l'alias de la clé (par défaut 'upload') : ").strip() or "upload"
    key_password = input("🔐 Confirmez le mot de passe de la clé (Entrée pour utiliser le même que le keystore) : ").strip()
    
    if not key_password:
        key_password = keystore_password
    
    # Configurer les secrets
    if not configure_secrets(keystore_password, key_alias, key_password):
        print("❌ Échec de la configuration des secrets")
        sys.exit(1)
    
    # Vérifier les secrets configurés
    print("\n🔍 Vérification des secrets configurés :")
    run_command("gh secret list", "Liste des secrets")
    
    # Créer un nouveau tag
    tag_name = "v1.3.1"
    if not create_and_push_tag(tag_name):
        print("❌ Échec de la création du tag")
        sys.exit(1)
    
    print(f"\n✅ Tag {tag_name} créé et poussé avec succès")
    print("🔄 Le pipeline va se déclencher automatiquement...")
    
    # Surveiller le workflow
    monitor_workflow()
    
    print("\n🎯 ÉTAPES SUIVANTES :")
    print("1. 👀 Surveillez l'exécution du workflow sur GitHub Actions")
    print("2. 🔍 Vérifiez que l'étape de signature réussit")
    print("3. 📱 Téléchargez l'AAB signé depuis les artifacts")
    print("4. 🚀 Publiez sur Google Play Console si nécessaire")
    
    print("\n🔗 Liens utiles :")
    print("   - GitHub Actions : https://github.com/your-repo/actions")
    print("   - Google Play Console : https://play.google.com/console/")
    
    print("\n🔮 Votre app de tarot sera bientôt prête pour la production ! ✨")

if __name__ == "__main__":
    main()
