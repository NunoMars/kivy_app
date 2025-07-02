#!/usr/bin/env python3
"""
🔑 Script de Signature AAB pour Google Play Console
Signe correctement un AAB avec la clé de production locale
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
    if result.stderr:
        print(f"⚠️  STDERR: {result.stderr}")
    
    if check and result.returncode != 0:
        print(f"❌ Commande échouée avec code: {result.returncode}")
        sys.exit(1)
    
    return result.returncode == 0, result.stdout, result.stderr

def sign_aab_locally():
    """Signe l'AAB avec la clé de production locale"""
    print("🔑 SIGNATURE AAB LOCALE POUR GOOGLE PLAY")
    print("=" * 50)
    
    # Vérifier que la clé de production existe
    keystore_file = "macartedetarot-release.keystore"
    config_file = f"{keystore_file}.config"
    
    if not os.path.exists(keystore_file):
        print(f"❌ Clé de signature non trouvée: {keystore_file}")
        print("💡 Exécutez d'abord: python generate_auto_signing_key.py")
        return False
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration non trouvée: {config_file}")
        print("💡 Exécutez d'abord: python generate_auto_signing_key.py")
        return False
    
    # Lire la configuration
    config = {}
    try:
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    except Exception as e:
        print(f"❌ Erreur lecture config: {e}")
        return False
    
    keystore_password = config.get('KEYSTORE_PASSWORD')
    key_alias = config.get('KEY_ALIAS')
    key_password = config.get('KEY_PASSWORD')
    
    if not all([keystore_password, key_alias, key_password]):
        print("❌ Configuration incomplète dans le fichier .config")
        return False
    
    print(f"✅ Clé de signature : {keystore_file}")
    print(f"✅ Alias : {key_alias}")
    print("✅ Configuration chargée")
    
    # Chercher l'AAB téléchargé
    aab_files = list(Path(".").glob("*production*.aab")) + \
                list(Path(".").glob("*release*.aab")) + \
                list(Path(".").glob("*.aab"))
    
    if not aab_files:
        print("❌ Aucun fichier AAB trouvé")
        print("💡 Copiez le fichier .aab téléchargé dans ce dossier")
        return False
    
    input_aab = aab_files[0]
    output_aab = "macartedetarot-signed-production.aab"
    
    print(f"📱 AAB source : {input_aab}")
    print(f"📱 AAB signé : {output_aab}")
    
    # Vérifier que Java/jarsigner est disponible
    success, _, _ = run_command("jarsigner -help", check=False)
    if not success:
        print("❌ jarsigner non disponible")
        print("💡 Installez Java Development Kit (JDK)")
        return False
    
    # Désigner l'AAB existant d'abord (au cas où)
    print("\n🧹 Nettoyage des signatures existantes...")
    run_command(f'zip -d "{input_aab}" "META-INF/*.SF" "META-INF/*.RSA" "META-INF/*.DSA"', check=False)
    
    # Copier vers le fichier de sortie
    print(f"\n📋 Copie vers {output_aab}...")
    run_command(f'copy "{input_aab}" "{output_aab}"')
    
    # Signer avec jarsigner (méthode compatible Google Play)
    print("\n🔑 Signature avec clé de production...")
    sign_cmd = f'jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore "{keystore_file}" -storepass "{keystore_password}" -keypass "{key_password}" "{output_aab}" "{key_alias}"'
    
    success, stdout, stderr = run_command(sign_cmd)
    
    if success:
        print("✅ Signature réussie !")
        
        # Vérifier la signature
        print("\n🔍 Vérification de la signature...")
        verify_cmd = f'jarsigner -verify -verbose "{output_aab}"'
        success, stdout, stderr = run_command(verify_cmd)
        
        if success and "jar verified" in stdout.lower():
            print("✅ AAB correctement signé et vérifié !")
            print(f"\n🎯 FICHIER PRÊT POUR GOOGLE PLAY : {output_aab}")
            print("\n📋 ÉTAPES SUIVANTES :")
            print("1. 🌐 Retournez sur Google Play Console")
            print(f"2. 📤 Uploadez le fichier : {output_aab}")
            print("3. ✅ L'erreur 'doit être signé' devrait disparaître !")
            return True
        else:
            print("❌ Vérification de signature échouée")
            return False
    else:
        print("❌ Signature échouée")
        return False

if __name__ == "__main__":
    if sign_aab_locally():
        print("\n🎉 AAB signé avec succès pour Google Play Console !")
    else:
        print("\n❌ Échec de la signature AAB")
        sys.exit(1)
