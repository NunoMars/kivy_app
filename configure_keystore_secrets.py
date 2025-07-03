#!/usr/bin/env python3
"""
Script interactif pour récupérer les informations du keystore et configurer les secrets GitHub
"""

import base64
import subprocess
import sys
from pathlib import Path

def test_keystore_password(password):
    """Teste un mot de passe pour le keystore"""
    try:
        cmd = [
            "keytool", "-list", "-keystore", "googleplay.keystore",
            "-storepass", password, "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def extract_aliases(keystore_output):
    """Extrait les aliases du keystore"""
    aliases = []
    lines = keystore_output.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith("Alias name:"):
            alias = line.split("Alias name:")[1].strip()
            aliases.append(alias)
    
    return aliases

def main():
    print("🔮 Configuration des secrets GitHub pour Ma Carte de Tarot")
    print("=" * 60)
    
    # Vérifier l'existence du keystore
    if not Path("googleplay.keystore").exists():
        print("❌ Le fichier 'googleplay.keystore' n'existe pas")
        sys.exit(1)
    
    print("✅ Fichier keystore trouvé")
    
    # Encoder le keystore
    print("\n🔐 Encodage du keystore...")
    with open("googleplay.keystore", "rb") as f:
        keystore_data = f.read()
    
    keystore_base64 = base64.b64encode(keystore_data).decode('utf-8')
    
    with open("keystore_base64.txt", "w") as f:
        f.write(keystore_base64)
    
    print("✅ Keystore encodé et sauvegardé dans 'keystore_base64.txt'")
    
    # Demander le mot de passe
    print("\n🔐 Recherche du mot de passe du keystore...")
    print("Vous devez connaître le mot de passe utilisé lors de la création du keystore.")
    print("Essayez-vous de ces mots de passe courants :")
    
    suggestions = [
        "Le mot de passe que vous utilisez habituellement",
        "Le nom de votre application: macartedetarot",
        "Le nom de votre projet: tarot",
        "Votre nom ou pseudonyme",
        "Une combinaison avec 'android' ou 'app'"
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    while True:
        password = input("\n🔐 Entrez le mot de passe du keystore (ou 'quit' pour quitter): ")
        
        if password.lower() == 'quit':
            print("👋 Au revoir!")
            sys.exit(0)
        
        print(f"🔍 Test du mot de passe: '{password}'...")
        success, output = test_keystore_password(password)
        
        if success:
            print("✅ SUCCÈS! Mot de passe correct")
            aliases = extract_aliases(output)
            
            if aliases:
                print(f"🔑 Aliases trouvés: {', '.join(aliases)}")
                alias = aliases[0]  # Utiliser le premier alias par défaut
            else:
                print("⚠️  Aucun alias trouvé, utilisation de 'upload' par défaut")
                alias = "upload"
            
            # Demander le mot de passe de la clé
            print(f"\n🔐 Mot de passe de la clé (alias: {alias})")
            print("Généralement, c'est le même que le mot de passe du keystore.")
            key_password = input(f"Entrez le mot de passe pour l'alias '{alias}' (ou Entrée pour utiliser le même): ")
            
            if not key_password:
                key_password = password
            
            # Générer les commandes
            print("\n🚀 Commandes pour configurer les secrets GitHub:")
            print("=" * 50)
            
            commands = f'''# Configurer les secrets GitHub
gh secret set ANDROID_KEYSTORE --body "{keystore_base64}"
gh secret set ANDROID_KEYSTORE_PASSWORD --body "{password}"
gh secret set ANDROID_KEY_ALIAS --body "{alias}"
gh secret set ANDROID_KEY_PASSWORD --body "{key_password}"

# Vérifier les secrets
gh secret list'''
            
            print(commands)
            
            # Sauvegarder
            with open("configure_secrets_final.ps1", "w") as f:
                f.write(commands)
            
            print("\n💾 Commandes sauvegardées dans 'configure_secrets_final.ps1'")
            
            print("\n🎯 ÉTAPES SUIVANTES:")
            print("1. 📋 Exécutez le script 'configure_secrets_final.ps1' dans PowerShell")
            print("2. 🚀 Créez un nouveau tag pour déclencher le pipeline:")
            print("   git tag v1.3.1")
            print("   git push origin v1.3.1")
            print("3. 📱 Vérifiez que le pipeline s'exécute correctement")
            
            break
        else:
            print(f"❌ Mot de passe incorrect: {output}")
            print("Essayez un autre mot de passe.")

if __name__ == "__main__":
    main()
