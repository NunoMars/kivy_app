#!/usr/bin/env python3
"""
Script de nettoyage du projet Kivy App
Supprime tous les fichiers temporaires, scripts de test, et ne garde que l'essentiel.
"""

import os
import shutil
import glob

def cleanup_project():
    """Nettoie le projet en supprimant tous les fichiers non essentiels."""
    
    # Fichiers et dossiers à supprimer
    files_to_remove = [
        # Scripts temporaires/de test
        "check_simple.py",
        "create_android_icon.py", 
        "deploy_simple.py",
        "fix_buildozer_errors.py",
        "generate_signing_key.py",
        "trigger_build.py",
        "update_github_secrets.py",
        
        # AAB temporaires (on garde seulement le final signé)
        "macartedetarot-production.aab",
        
        # Documentation excessive (on garde README.md principal)
        "README_PIPELINE.md",
        "ETAT_FINAL_PIPELINE.md", 
        "store_descriptions.md",
        
        # Template qui ne sert plus
        "android_manifest_template.xml",
        
        # Cache Python
        "__pycache__",
        "*.pyc",
        
        # Environnement virtuel local (pas besoin en prod)
        "venv",
        
        # Dossiers temporaires
        "docs",
        "bin",
        ".buildozer",
    ]
    
    # Workflows à supprimer (on garde seulement publish-android.yml)
    workflows_to_remove = [
        ".github/workflows/build-android.yml",
        ".github/workflows/deploy-pages.yml", 
        ".github/workflows/test-build.yml"
    ]
    
    print("🧹 Nettoyage du projet...")
    
    # Supprimer les fichiers/dossiers spécifiés
    for item in files_to_remove:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    print(f"  📁 Suppression du dossier: {item}")
                    shutil.rmtree(item)
                else:
                    print(f"  📄 Suppression du fichier: {item}")
                    os.remove(item)
            except (PermissionError, OSError) as e:
                print(f"  ⚠️  Impossible de supprimer {item}: {e}")
                continue
        
        # Supprimer les patterns (comme *.pyc)
        for file_path in glob.glob(item):
            if os.path.exists(file_path):
                try:
                    if os.path.isdir(file_path):
                        print(f"  📁 Suppression du dossier: {file_path}")
                        shutil.rmtree(file_path)
                    else:
                        print(f"  📄 Suppression du fichier: {file_path}")
                        os.remove(file_path)
                except (PermissionError, OSError) as e:
                    print(f"  ⚠️  Impossible de supprimer {file_path}: {e}")
                    continue
    
    # Supprimer les workflows inutiles
    for workflow in workflows_to_remove:
        if os.path.exists(workflow):
            print(f"  ⚙️ Suppression du workflow: {workflow}")
            os.remove(workflow)
    
    print("\n✅ Nettoyage terminé!")
    print("\n📋 Fichiers essentiels conservés:")
    
    # Lister ce qui reste d'essentiel
    essential_files = [
        "main.py",
        "macartedetarotapp.kv", 
        "signification.py",
        "requirements.txt",
        "buildozer.spec",
        ".gitignore",
        "README.md",
        "googleplay.keystore",
        "google-play-service-account.json", 
        "macartedetarot-signed-production.aab",
        ".github/workflows/publish-android.yml",
        "tarot_img/"
    ]
    
    for item in essential_files:
        if os.path.exists(item):
            print(f"  ✓ {item}")
        else:
            print(f"  ❌ {item} (manquant)")

if __name__ == "__main__":
    cleanup_project()
