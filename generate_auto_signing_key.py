#!/usr/bin/env python3
"""
🔐 Générateur Automatisé de Clé de Signature Android
Génère automatiquement une clé de signature sécurisée pour Google Play Store
"""

import subprocess
import os
import base64
import secrets
import string

def generate_secure_password(length=12):
    """Génère un mot de passe sécurisé"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def generate_android_signing_key():
    """Génère automatiquement une clé de signature Android"""
    print("🔐 GÉNÉRATION AUTOMATIQUE DE CLÉ DE SIGNATURE ANDROID")
    print("=" * 60)
    
    # Configuration automatique
    keystore_file = "macartedetarot-release.keystore"
    key_alias = "macartedetarot"
    keystore_password = generate_secure_password(16)
    key_password = generate_secure_password(16)
    
    # Informations du certificat
    dname = "CN=Ma Carte de Tarot, OU=Mobile Apps, O=Tarot Software, L=Eragny, ST=Ile-de-France, C=FR"
    
    print(f"🔑 Génération de: {keystore_file}")
    print(f"🔑 Alias: {key_alias}")
    print("🔒 Mots de passe générés automatiquement (sécurisés)")
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(keystore_file):
        print(f"⚠️  Le fichier {keystore_file} existe déjà.")
        backup_name = f"{keystore_file}.backup"
        os.rename(keystore_file, backup_name)
        print(f"📂 Ancien fichier sauvegardé: {backup_name}")
    
    # Commande keytool
    keytool_cmd = [
        "keytool", "-genkey", "-v",
        "-keystore", keystore_file,
        "-alias", key_alias,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-dname", dname,
        "-storepass", keystore_password,
        "-keypass", key_password
    ]
    
    print("\n🔧 Génération en cours...")
    
    # Générer la clé
    try:
        result = subprocess.run(keytool_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Clé de signature créée avec succès!")
        else:
            print(f"❌ Erreur lors de la génération:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur d'exécution: {e}")
        return False
    
    if not os.path.exists(keystore_file):
        print(f"❌ Le fichier {keystore_file} n'a pas été créé")
        return False
    
    # Vérifier la clé
    print("\n🔍 Vérification de la clé...")
    verify_cmd = ["keytool", "-list", "-keystore", keystore_file, "-storepass", keystore_password]
    
    try:
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Clé vérifiée avec succès")
            print("📋 Informations de la clé:")
            print(result.stdout)
        else:
            print("⚠️  Impossible de vérifier la clé")
    except Exception as e:
        print(f"⚠️  Erreur lors de la vérification: {e}")
    
    # Encoder en base64
    print("\n🔒 Encodage de la clé en base64 pour GitHub...")
    
    try:
        with open(keystore_file, "rb") as f:
            keystore_data = f.read()
        
        keystore_base64 = base64.b64encode(keystore_data).decode('utf-8')
        
        # Sauvegarder le base64
        base64_file = f"{keystore_file}.base64"
        with open(base64_file, "w") as f:
            f.write(keystore_base64)
        
        print(f"✅ Clé encodée sauvegardée: {base64_file}")
        
        # Sauvegarder les informations de configuration
        config_file = f"{keystore_file}.config"
        with open(config_file, "w") as f:
            f.write(f"# Configuration de clé de signature Android\n")
            f.write(f"# Généré automatiquement le {os.popen('date /t').read().strip()}\n")
            f.write(f"KEYSTORE_FILE={keystore_file}\n")
            f.write(f"KEY_ALIAS={key_alias}\n")
            f.write(f"KEYSTORE_PASSWORD={keystore_password}\n")
            f.write(f"KEY_PASSWORD={key_password}\n")
            f.write(f"BASE64_FILE={base64_file}\n")
        
        print(f"✅ Configuration sauvegardée: {config_file}")
        
        # Afficher les secrets GitHub
        print("\n" + "="*70)
        print("🔑 SECRETS GITHUB À CONFIGURER")
        print("="*70)
        print("Allez sur : https://github.com/VOTRE_USERNAME/VOTRE_REPO/settings/secrets/actions")
        print("\nAjoutez ces 4 secrets :")
        print()
        print("1. ANDROID_KEYSTORE_BASE64:")
        print(f"   {keystore_base64[:50]}...") 
        print()
        print("2. KEYSTORE_PASSWORD:")
        print(f"   {keystore_password}")
        print()
        print("3. KEY_ALIAS:")
        print(f"   {key_alias}")
        print()
        print("4. KEY_PASSWORD:")
        print(f"   {key_password}")
        print()
        print("="*70)
        
        # Mise à jour du .gitignore
        gitignore_entries = [
            "# Clés de signature Android (SENSIBLE !)",
            "*.keystore",
            "*.keystore.backup",
            "*.keystore.base64", 
            "*.keystore.config",
            "*-release.keystore*",
            "*signing-key*",
            "*service-account*.json",
            "*google-play*.json"
        ]
        
        gitignore_path = ".gitignore"
        existing_content = ""
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                existing_content = f.read()
        
        # Ajouter les entrées manquantes
        new_entries = []
        for entry in gitignore_entries:
            if entry not in existing_content:
                new_entries.append(entry)
        
        if new_entries:
            with open(gitignore_path, "a") as f:
                f.write("\n" + "\n".join(new_entries) + "\n")
            print("✅ Fichiers de signature ajoutés au .gitignore")
        
        print("\n🎯 ÉTAPES SUIVANTES :")
        print("1. ✅ Clé de signature créée")
        print("2. 📤 Configurer les 4 secrets GitHub (voir ci-dessus)")
        print("3. 🚀 Tester avec: .\\deploy.ps1 v1.0.1")
        print("4. 🎯 [OPTIONNEL] Configurer l'API Google Play Console")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'encodage: {e}")
        return False

if __name__ == "__main__":
    if generate_android_signing_key():
        print("\n🎉 Clé de signature Android générée avec succès !")
        print("🔑 Votre app peut maintenant être signée pour Google Play Store")
    else:
        print("\n❌ Échec de la génération de la clé")
