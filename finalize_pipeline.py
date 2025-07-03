#!/usr/bin/env python3
"""
Script pour finaliser et publier la version v1.3.0 du pipeline CI/CD Android.
Commit les derniers changements et crée le tag pour déclencher le build.
"""

import os
import subprocess
import sys

def run_command(command, description, check=True):
    """Exécute une commande et affiche le résultat."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Erreur: {result.stderr}")
            return False
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        print(f"✅ {description} terminé")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_git_status():
    """Vérifie le statut Git."""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def main():
    """Fonction principale."""
    print("🔮 FINALISATION DU PIPELINE CI/CD ANDROID")
    print("   Version: v1.3.0")
    print("   Application: Ma Carte de Tarot")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("main.py") or not os.path.exists("buildozer.spec"):
        print("❌ Veuillez exécuter ce script depuis le répertoire racine du projet")
        sys.exit(1)
    
    # Vérifier les fichiers modifiés
    print("\n📋 VÉRIFICATION DES CHANGEMENTS")
    modified_files = check_git_status()
    
    if not modified_files:
        print("✅ Aucun changement à commiter")
    else:
        print("📝 Fichiers modifiés détectés:")
        for file in modified_files:
            print(f"   {file}")
    
    # Ajouter tous les nouveaux fichiers
    print("\n📦 AJOUT DES FICHIERS")
    files_to_add = [
        "test_pipeline_readiness.py",
        "configure_github_secrets.ps1", 
        "CONFIGURATION_SECRETS_FINALE.md",
        ".github/workflows/publish-android.yml",
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            run_command(f"git add {file}", f"Ajout de {file}")
    
    # Supprimer le fichier obsolète
    if os.path.exists(".github/workflows/publish-android-clean.yml"):
        run_command("git rm .github/workflows/publish-android-clean.yml", "Suppression du workflow obsolète")
    
    # Créer le commit
    print("\n💾 CRÉATION DU COMMIT")
    commit_message = """feat: finaliser pipeline CI/CD Android v1.3.0

- ✅ Build AAB fonctionnel et testé
- 🔐 Gestion complète de la signature de production
- 🤖 Upload automatique vers Google Play Console
- 📱 Génération d'App Bundle (AAB) optimisé
- 🔧 Scripts de validation et configuration automatisée
- 📚 Documentation complète des secrets GitHub
- 🎯 Pipeline prêt pour la production

Prochaine étape: Configurer les secrets GitHub et créer le tag v1.3.0"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Commit des changements"):
        print("⚠️  Aucun changement à commiter ou erreur de commit")
    
    # Pousser les changements
    print("\n🚀 PUSH VERS GITHUB")
    if not run_command("git push origin main", "Push vers la branche main"):
        print("❌ Erreur lors du push")
        sys.exit(1)
    
    # Instructions pour créer le tag
    print("\n🏷️  CRÉATION DU TAG DE RELEASE")
    print("⚠️  ATTENTION: Avant de créer le tag, assurez-vous que les secrets GitHub sont configurés!")
    print("")
    print("📝 Secrets requis dans GitHub:")
    print("   - ANDROID_KEYSTORE (clé base64)")
    print("   - ANDROID_KEYSTORE_PASSWORD")
    print("   - ANDROID_KEY_ALIAS")
    print("   - ANDROID_KEY_PASSWORD")
    print("")
    print("🔧 Pour configurer les secrets:")
    print("   1. Utilisez le script: .\\configure_github_secrets.ps1")
    print("   2. Ou configurez manuellement: https://github.com/NunoMars/kivy_app/settings/secrets/actions")
    print("")
    
    # Demander confirmation pour créer le tag
    response = input("🤔 Voulez-vous créer le tag v1.3.0 maintenant ? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'oui']:
        print("\n🎯 CRÉATION DU TAG v1.3.0")
        
        # Créer le tag
        tag_message = """Version 1.3.0 - Pipeline CI/CD Android Production

🔮 Ma Carte de Tarot - Version Stable Android

✨ Nouvelles fonctionnalités:
- Pipeline CI/CD Android complet et automatisé
- Génération d'App Bundle (AAB) optimisé pour Google Play
- Signature automatique avec clé de production
- Upload automatique vers Google Play Console
- Scripts de validation et configuration
- Documentation complète du processus

🔧 Améliorations techniques:
- Build Android avec Buildozer optimisé
- Compatibilité Python 3.9 + Cython 0.29.36
- Support Java 17 et Android SDK 34
- Gestion des secrets GitHub sécurisée
- Artefacts de build automatisés

📱 Compatibilité:
- Android API 21+ (Android 5.0+)
- Toutes les architectures Android
- App Bundle AAB pour Google Play Store

🎯 Prêt pour la production !"""
        
        if run_command(f'git tag -a v1.3.0 -m "{tag_message}"', "Création du tag v1.3.0"):
            if run_command("git push origin v1.3.0", "Push du tag v1.3.0"):
                print("\n🎉 TAG v1.3.0 CRÉÉ ET POUSSÉ!")
                print("🚀 Le build Android se lance automatiquement...")
                print("👀 Suivez le progrès: https://github.com/NunoMars/kivy_app/actions")
                print("")
                print("⏱️  Le build prendra environ 10-15 minutes")
                print("📱 L'AAB signé sera disponible dans les artifacts")
                print("🏪 L'upload vers Google Play se fera automatiquement (si secrets configurés)")
            else:
                print("❌ Erreur lors du push du tag")
                sys.exit(1)
        else:
            print("❌ Erreur lors de la création du tag")
            sys.exit(1)
    else:
        print("\n⏸️  Tag non créé")
        print("✅ Changements commitées et poussés sur main")
        print("🔧 Configurez les secrets GitHub puis créez le tag manuellement:")
        print("   git tag v1.3.0")
        print("   git push origin v1.3.0")
    
    print("\n📚 DOCUMENTATION DISPONIBLE:")
    print("   - README.md : Documentation générale")
    print("   - CONFIGURATION_SECRETS_FINALE.md : Guide des secrets")
    print("   - test_pipeline_readiness.py : Script de validation")
    print("   - configure_github_secrets.ps1 : Configuration automatique")
    
    print("\n🔮 PIPELINE CI/CD ANDROID FINALISÉ!")
    print("   Votre application de tarot est prête pour la production.")

if __name__ == "__main__":
    main()
