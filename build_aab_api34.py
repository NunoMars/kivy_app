#!/usr/bin/env python3
"""
🚀 Build AAB Local avec API 34
Génère un AAB correctement configuré pour Google Play Console
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Exécute une commande et retourne le résultat"""
    print(f"🔧 Exécution : {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(f"📤 STDOUT: {result.stdout}")
    if result.stderr and result.stderr.strip():
        print(f"⚠️  STDERR: {result.stderr}")
    
    if check and result.returncode != 0:
        print(f"❌ Commande échouée avec code: {result.returncode}")
        return False
    
    return result.returncode == 0

def build_aab_api34():
    """Build un AAB avec API 34 et signature correcte"""
    print("🚀 BUILD AAB LOCAL AVEC API 34")
    print("=" * 50)
    
    # Vérifier que buildozer est installé
    if not run_command("buildozer --version", check=False):
        print("❌ Buildozer non installé. Installation...")
        if not run_command("pip install buildozer"):
            print("❌ Échec installation buildozer")
            return False
    
    # Vérifier la configuration API 34
    try:
        with open("buildozer.spec", "r") as f:
            content = f.read()
        
        if "android.api = 34" not in content:
            print("❌ API 34 non configurée dans buildozer.spec")
            return False
        
        print("✅ API 34 configurée")
        
    except Exception as e:
        print(f"❌ Erreur lecture buildozer.spec: {e}")
        return False
    
    # Vérifier que la clé de signature existe
    if not os.path.exists("googleplay.keystore"):
        print("❌ Clé de signature googleplay.keystore non trouvée")
        print("💡 La clé doit être générée d'abord")
        return False
    
    print("✅ Clé de signature trouvée")
    
    # Nettoyer les builds précédents
    print("\n🧹 Nettoyage des builds précédents...")
    run_command("buildozer android clean", check=False)
    
    # Configurer buildozer avec la clé de production
    print("\n🔑 Configuration de la signature...")
    
    # Lire le fichier buildozer.spec
    try:
        with open("buildozer.spec", "r") as f:
            lines = f.readlines()
        
        # Supprimer les anciennes configurations de signature
        lines = [line for line in lines if not any(keyword in line for keyword in [
            "android.release_keystore",
            "android.release_keystore_passwd", 
            "android.release_key",
            "android.release_key_passwd"
        ])]
        
        # Ajouter la nouvelle configuration
        lines.append("\n# Configuration signature production API 34\n")
        lines.append("android.release_keystore = googleplay.keystore\n")
        lines.append("android.release_keystore_passwd = GooglePlay2025!\n")
        lines.append("android.release_key = googleplay\n")
        lines.append("android.release_key_passwd = GooglePlay2025!\n")
        
        # Écrire le fichier modifié
        with open("buildozer.spec", "w") as f:
            f.writelines(lines)
        
        print("✅ Configuration signature ajoutée")
        
    except Exception as e:
        print(f"❌ Erreur modification buildozer.spec: {e}")
        return False
    
    # Build AAB avec API 34
    print("\n🏗️  Build AAB avec API 34...")
    print("⏳ Ceci peut prendre plusieurs minutes...")
    
    if run_command("buildozer android release", check=False):
        print("✅ Build AAB réussi !")
        
        # Vérifier que l'AAB a été généré
        aab_files = list(Path("bin").glob("*.aab")) if os.path.exists("bin") else []
        
        if aab_files:
            aab_file = aab_files[0]
            final_aab = "macartedetarot-api34-production.aab"
            
            # Copier avec un nom explicite
            run_command(f'copy "{aab_file}" "{final_aab}"')
            
            # Vérifier la signature
            print(f"\n🔍 Vérification de la signature : {final_aab}")
            if run_command(f'jarsigner -verify -verbose "{final_aab}"', check=False):
                print("✅ AAB correctement signé !")
                print(f"\n🎯 FICHIER PRÊT POUR GOOGLE PLAY : {final_aab}")
                print("\n📋 CARACTÉRISTIQUES :")
                print("   - API Level 34 ✅")
                print("   - Signature production ✅")
                print("   - Format AAB ✅")
                print("\n📤 Uploadez ce fichier sur Google Play Console !")
                return True
            else:
                print("⚠️  Problème de signature détecté")
                return False
        else:
            print("❌ Aucun fichier AAB généré")
            return False
    else:
        print("❌ Build AAB échoué")
        
        # Afficher les logs d'erreur
        log_file = Path(".buildozer/logs/buildozer.log")
        if log_file.exists():
            print("\n📋 Dernières lignes du log d'erreur :")
            with open(log_file, "r") as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(f"   {line.rstrip()}")
        
        return False

if __name__ == "__main__":
    print("🎯 Ce script va générer un AAB avec API 34 pour Google Play Console")
    print("⚠️  Assurez-vous que buildozer et toutes les dépendances sont installées")
    print()
    
    if build_aab_api34():
        print("\n🎉 SUCCESS ! AAB API 34 généré avec succès !")
    else:
        print("\n❌ ÉCHEC du build AAB API 34")
        sys.exit(1)
