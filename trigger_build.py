#!/usr/bin/env python3
"""
Script pour créer un tag Git et déclencher le build GitHub Actions
"""
import subprocess
import sys

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔧 {description}")
    print(f"📤 Commande: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='.')
        
        if result.stdout:
            print(f"📤 STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"⚠️  STDERR: {result.stderr.strip()}")
        
        if result.returncode == 0:
            print("✅ Succès")
            return True
        else:
            print(f"❌ Échec (code {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python trigger_build.py <version>")
        print("Exemple: python trigger_build.py v1.0.2")
        sys.exit(1)
    
    version = sys.argv[1]
    if not version.startswith('v'):
        version = f"v{version}"
    
    print("🚀 DÉCLENCHEMENT DU BUILD GITHUB ACTIONS")
    print("=" * 50)
    print(f"📦 Version: {version}")
    print()
    
    # Vérifier le statut Git
    print("📍 Vérification du statut Git...")
    if not run_command("git status --porcelain", "Vérification des fichiers modifiés"):
        return
    
    # Ajouter tous les fichiers modifiés
    print("\n📁 Ajout des fichiers modifiés...")
    if not run_command("git add .", "Ajout des fichiers"):
        return
    
    # Commit
    print("\n💾 Commit des changements...")
    commit_msg = f"Release {version} - Build pour Google Play avec API 34"
    if not run_command(f'git commit -m "{commit_msg}"', "Commit"):
        print("ℹ️  Aucun changement à commiter ou déjà commité")
    
    # Vérifier si le tag existe
    print(f"\n🏷️  Vérification du tag {version}...")
    result = subprocess.run(f"git tag -l {version}", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"⚠️  Le tag {version} existe déjà, suppression...")
        run_command(f"git tag -d {version}", f"Suppression du tag local {version}")
        run_command(f"git push origin --delete {version}", f"Suppression du tag distant {version}")
    
    # Créer le tag
    print(f"\n🏷️  Création du tag {version}...")
    if not run_command(f'git tag -a {version} -m "Release {version}"', f"Création du tag {version}"):
        return
    
    # Push vers GitHub
    print("\n📤 Push vers GitHub...")
    if not run_command("git push origin main", "Push du code"):
        return
    
    if not run_command(f"git push origin {version}", f"Push du tag {version}"):
        return
    
    print(f"\n✅ SUCCÈS! Build déclenché pour {version}")
    print("🔗 Vérifiez le build sur GitHub:")
    print("   https://github.com/votre-username/votre-repo/actions")
    print()
    print("📱 Le workflow va:")
    print("   1. Builder l'AAB avec API 34")
    print("   2. Signer avec la clé de production")
    print("   3. Uploader sur Google Play Console")
    print()
    print("⏱️  Le build prend environ 10-15 minutes")

if __name__ == "__main__":
    main()
