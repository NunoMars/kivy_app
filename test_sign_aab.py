#!/usr/bin/env python3
"""
Script pour tester la signature locale d'un AAB
"""
import subprocess
import os

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
    print("SIGNATURE LOCALE AAB AVEC CLE DE PRODUCTION")
    print("=" * 50)
    
    # Vérifier les fichiers requis
    aab_file = "macartedetarot-production.aab"
    keystore_file = "googleplay.keystore"
    
    if not os.path.exists(aab_file):
        print(f"❌ AAB non trouvé: {aab_file}")
        return False
    
    if not os.path.exists(keystore_file):
        print(f"❌ Clé de signature non trouvée: {keystore_file}")
        return False
    
    print(f"✅ AAB source: {aab_file}")
    print(f"✅ Clé de signature: {keystore_file}")
    
    # Copier l'AAB pour la signature
    print("\n📋 PREPARATION DE LA SIGNATURE")
    print("-" * 30)
    
    unsigned_aab = "macartedetarot-unsigned.aab"
    signed_aab = "macartedetarot-signed-final.aab"
    
    if not run_command(f"copy {aab_file} {unsigned_aab}", "Copie de l'AAB"):
        return False
    
    # Paramètres de signature
    keystore_password = "GooglePlay2025!"
    key_alias = "googleplay"
    key_password = "GooglePlay2025!"
    
    # Signature avec jarsigner
    print("\n🔏 SIGNATURE DE L'AAB")
    print("-" * 20)
    
    sign_cmd = f'''jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 ^
        -keystore {keystore_file} ^
        -storepass {keystore_password} ^
        -keypass {key_password} ^
        {unsigned_aab} {key_alias}'''
    
    if not run_command(sign_cmd, "Signature de l'AAB"):
        return False
    
    # Copier le résultat
    if not run_command(f"copy {unsigned_aab} {signed_aab}", "Copie AAB signé"):
        return False
    
    # Vérification de la signature
    print("\n🔍 VERIFICATION DE LA SIGNATURE")
    print("-" * 30)
    
    if run_command(f"jarsigner -verify -verbose {signed_aab}", "Vérification signature"):
        print("\n✅ AAB CORRECTEMENT SIGNE!")
        print(f"📱 Fichier final: {signed_aab}")
        
        # Afficher les détails du fichier
        if os.path.exists(signed_aab):
            size = os.path.getsize(signed_aab) / (1024 * 1024)
            print(f"📏 Taille: {size:.1f} MB")
        
        return True
    else:
        print("❌ Erreur de vérification de signature")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SIGNATURE REUSSIE!")
        print("L'AAB est prêt pour upload sur Google Play Console")
    else:
        print("\n❌ SIGNATURE ECHOUEE")
        print("Vérifiez les paramètres de signature")
