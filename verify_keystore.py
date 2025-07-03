#!/usr/bin/env python3
"""
Script pour vérifier le keystore de production et diagnostiquer les problèmes de signature.
"""

import sys
import base64
import subprocess
from pathlib import Path

def check_keystore_file():
    """Vérifie l'existence et la validité du fichier keystore"""
    print("🔍 Vérification du fichier keystore...")
    
    keystore_path = Path("googleplay.keystore")
    if not keystore_path.exists():
        print("❌ Le fichier 'googleplay.keystore' n'existe pas dans le répertoire courant")
        return False
    
    print(f"✅ Fichier keystore trouvé: {keystore_path.absolute()}")
    print(f"   Taille: {keystore_path.stat().st_size} octets")
    
    return True

def encode_keystore_for_github():
    """Encode le keystore en base64 pour GitHub Secrets"""
    print("\n🔐 Encodage du keystore pour GitHub Secrets...")
    
    try:
        with open("googleplay.keystore", "rb") as f:
            keystore_data = f.read()
        
        base64_data = base64.b64encode(keystore_data).decode('utf-8')
        
        print("✅ Keystore encodé avec succès")
        print(f"   Longueur base64: {len(base64_data)} caractères")
        
        # Sauvegarder dans un fichier pour faciliter la copie
        with open("keystore_base64.txt", "w") as f:
            f.write(base64_data)
        
        print("💾 Keystore encodé sauvegardé dans 'keystore_base64.txt'")
        print("   Vous pouvez copier ce contenu dans GitHub Secrets > ANDROID_KEYSTORE")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'encodage: {e}")
        return False

def test_keystore_passwords():
    """Test différents mots de passe courants pour le keystore"""
    print("\n🔐 Test des mots de passe courants...")
    
    # Mots de passe courants à tester
    common_passwords = [
        "123456",
        "password", 
        "android",
        "googleplay",
        "tarot",
        "macartedetarot",
        "kivy",
        "buildozer",
        "release",
        "prod",
        "production",
        "",  # Mot de passe vide
    ]
    
    for password in common_passwords:
        try:
            cmd = [
                "keytool", "-list", "-keystore", "googleplay.keystore",
                "-storepass", password, "-v"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ SUCCÈS! Mot de passe du keystore: '{password}'")
                print("   Aliases disponibles:")
                
                # Extraire les aliases du output
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Alias name:" in line:
                        alias = line.split("Alias name:")[1].strip()
                        print(f"   - {alias}")
                
                return password
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout pour mot de passe: '{password}'")
        except Exception as e:
            print(f"❌ Erreur avec mot de passe '{password}': {e}")
    
    print("❌ Aucun mot de passe courant ne fonctionne")
    return None

def generate_secrets_commands(keystore_password=None, key_alias=None):
    """Génère les commandes pour configurer les secrets GitHub"""
    print("\n📝 Génération des commandes pour GitHub Secrets...")
    
    if not keystore_password:
        keystore_password = input("🔐 Entrez le mot de passe du keystore: ")
    
    if not key_alias:
        key_alias = input("🔑 Entrez l'alias de la clé (généralement 'upload' ou 'key0'): ")
    
    key_password = input("🔐 Entrez le mot de passe de la clé (souvent identique au keystore): ")
    
    print("\n🚀 Commandes PowerShell pour configurer les secrets GitHub:")
    print("=" * 60)
    
    # Lire le keystore encodé
    try:
        with open("keystore_base64.txt", "r") as f:
            keystore_base64 = f.read().strip()
    except FileNotFoundError:
        print("❌ Fichier keystore_base64.txt non trouvé. Exécutez d'abord l'encodage.")
        return
    
    commands = f"""
# Configurer les secrets GitHub (exécuter dans PowerShell)
gh secret set ANDROID_KEYSTORE --body "{keystore_base64}"
gh secret set ANDROID_KEYSTORE_PASSWORD --body "{keystore_password}"
gh secret set ANDROID_KEY_ALIAS --body "{key_alias}"
gh secret set ANDROID_KEY_PASSWORD --body "{key_password}"

# Vérifier les secrets
gh secret list
"""
    
    print(commands)
    
    # Sauvegarder les commandes
    with open("configure_secrets.ps1", "w") as f:
        f.write(commands)
    
    print("💾 Commandes sauvegardées dans 'configure_secrets.ps1'")

def main():
    """Fonction principale"""
    print("🔮 Vérification du keystore de production pour Ma Carte de Tarot")
    print("=" * 60)
    
    if not check_keystore_file():
        print("\n❌ Keystore introuvable. Assurez-vous que 'googleplay.keystore' existe.")
        sys.exit(1)
    
    if not encode_keystore_for_github():
        print("\n❌ Impossible d'encoder le keystore.")
        sys.exit(1)
    
    # Tester les mots de passe
    password = test_keystore_passwords()
    
    if password is not None:
        print(f"\n✅ Mot de passe trouvé: '{password}'")
        generate_secrets_commands(password)
    else:
        print("\n⚠️  Mot de passe non trouvé automatiquement.")
        print("   Vous devrez le fournir manuellement.")
        generate_secrets_commands()
    
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("1. 📋 Copiez le contenu de 'keystore_base64.txt' dans GitHub Secrets > ANDROID_KEYSTORE")
    print("2. 🔐 Configurez les autres secrets avec les bonnes valeurs")
    print("3. 🚀 Pushez un nouveau tag pour déclencher le pipeline")
    print("4. 📱 Vérifiez que la signature fonctionne correctement")
    
    print("\n🔧 Commandes de dépannage:")
    print("   # Créer un nouveau tag et déclencher le pipeline")
    print("   git tag v1.3.1")
    print("   git push origin v1.3.1")
    print("   # Ou déclencher manuellement via GitHub Actions")

if __name__ == "__main__":
    main()
