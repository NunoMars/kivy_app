#!/usr/bin/env python3
"""
Script de deployement simplifie pour Windows
"""
import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy_simple.py <version>")
        print("Exemple: python deploy_simple.py v1.0.1")
        sys.exit(1)
    
    version = sys.argv[1]
    if not version.startswith('v'):
        version = f"v{version}"
    
    print("=" * 60)
    print(f"DEPLOIEMENT ANDROID - VERSION {version}")
    print("=" * 60)
    
    # Etape 1: Verification
    print("\nETAPE 1: VERIFICATION")
    print("-" * 30)
    result = subprocess.run([sys.executable, "check_simple.py"], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print("ERREUR: La verification a echoue")
        print(result.stderr)
        return
    
    if "TOUS LES TESTS PASSENT" not in result.stdout:
        print("ERREUR: Tous les tests ne passent pas")
        print(result.stdout)
        return
    
    print("OK: Toutes les verifications passent")
    
    # Etape 2: Affichage des secrets
    print("\nETAPE 2: SECRETS GITHUB")
    print("-" * 30)
    print("Verification des secrets a configurer...")
    subprocess.run([sys.executable, "update_github_secrets.py"])
    
    print("\n" + "="*50)
    print("IMPORTANT: Configurez les secrets GitHub maintenant!")
    print("1. Allez sur GitHub.com > Settings > Secrets")
    print("2. Ajoutez tous les secrets affiches ci-dessus")
    print("="*50)
    
    response = input("\nSecrets configures? (y/N): ")
    if response.lower() != 'y':
        print("Arret: Configurez d'abord les secrets GitHub")
        return
    
    # Etape 3: Declenchement du build
    print("\nETAPE 3: DECLENCHEMENT DU BUILD")
    print("-" * 30)
    result = subprocess.run([sys.executable, "trigger_build.py", version])
    
    if result.returncode == 0:
        print("\n" + "="*60)
        print("BUILD DECLENCHE AVEC SUCCES!")
        print("="*60)
        print("Surveillez le build sur:")
        print("https://github.com/NunoMars/kivy_app/actions")
        print("\nTemps estime: 15-20 minutes")
    else:
        print("ERREUR: Echec du declenchement du build")

if __name__ == "__main__":
    main()
