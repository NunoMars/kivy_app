#!/usr/bin/env python3
"""
Script de déploiement complet - Pipeline CI/CD Android
Finalise et déploie l'application Kivy sur Google Play
"""
import subprocess
import sys

def print_banner(title):
    """Affiche un banner décoré"""
    print()
    print("=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_step(step_num, title):
    """Affiche une étape numérotée"""
    print()
    print(f"📍 ÉTAPE {step_num}: {title}")
    print("-" * 40)

def run_script(script_name, description):
    """Exécute un script Python et affiche le résultat"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd='.')
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print(f"⚠️  Erreurs: {result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy_complete.py <version>")
        print("Exemple: python deploy_complete.py v1.0.1")
        sys.exit(1)
    
    version = sys.argv[1]
    if not version.startswith('v'):
        version = f"v{version}"
    
    print_banner(f"DÉPLOIEMENT COMPLET - VERSION {version}")
    
    # Étape 1: Vérification finale
    print_step(1, "VÉRIFICATION FINALE")
    if not run_script("check_ready_for_build.py", "Vérification de la configuration"):
        print("❌ La vérification a échoué. Corrigez les erreurs avant de continuer.")
        return
    
    print("✅ Toutes les vérifications passent !")
    
    # Étape 2: Informations sur les secrets
    print_step(2, "CONFIGURATION DES SECRETS GITHUB")
    print("📋 Exécution du guide des secrets...")
    run_script("update_github_secrets.py", "Affichage des secrets à configurer")
    
    print()
    input("⏸️  APPUYEZ SUR ENTRÉE APRÈS AVOIR MIS À JOUR LES SECRETS GITHUB...")
    
    # Étape 3: Build et déploiement
    print_step(3, "BUILD ET DÉPLOIEMENT")
    if not run_script("trigger_build.py", f"Déclenchement du build {version}"):
        print("❌ Le déclenchement du build a échoué.")
        return
    
    # Informations post-déploiement
    print_step(4, "SURVEILLANCE DU BUILD")
    print("🔗 Liens utiles:")
    print("   📊 GitHub Actions: https://github.com/NunoMars/kivy_app/actions")
    print("   📱 Google Play Console: https://play.google.com/console")
    print()
    
    print("⏱️  TEMPS D'ATTENTE ESTIMÉ:")
    print("   - Build Android: 10-15 minutes")
    print("   - Upload Google Play: 2-3 minutes")
    print("   - Total: ~15-20 minutes")
    print()
    
    print("🔍 VÉRIFICATIONS À FAIRE:")
    print("   1. ✅ Build réussi dans GitHub Actions")
    print("   2. ✅ AAB généré et signé correctement")
    print("   3. ✅ Upload sur Google Play Console réussi")
    print("   4. ✅ Pas d'erreurs de signature ou d'API")
    print()
    
    print("📱 APRÈS LE BUILD RÉUSSI:")
    print("   1. Allez sur Google Play Console")
    print("   2. Vérifiez l'AAB dans 'Release Management > App releases'")
    print("   3. Configurez les informations de l'app (description, screenshots)")
    print("   4. Testez avec des utilisateurs internes")
    print("   5. Publiez en production")
    print()
    
    print_banner("DÉPLOIEMENT LANCÉ AVEC SUCCÈS!")
    print("🎉 Votre pipeline CI/CD est maintenant opérationnel !")
    print("📧 Vous recevrez une notification GitHub en cas de succès/échec.")

if __name__ == "__main__":
    main()
