#!/usr/bin/env python3
"""
Script pour générer une nouvelle clé de signature Android et configurer le projet
"""

import subprocess
import sys
import os
import base64
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande avec gestion d'erreur"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - Succès")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None

def generate_new_keystore():
    """Génère une nouvelle clé de signature"""
    print("🔐 Génération d'une nouvelle clé de signature...")
    
    # Sauvegarder l'ancienne clé si elle existe
    if Path("googleplay.keystore").exists():
        backup_name = "googleplay.keystore.backup"
        Path("googleplay.keystore").rename(backup_name)
        print(f"📦 Ancienne clé sauvegardée dans {backup_name}")
    
    # Demander les informations pour la nouvelle clé
    print("📝 Informations pour la nouvelle clé de signature:")
    
    # Utiliser des valeurs par défaut appropriées pour une app de tarot
    keystore_password = input("🔐 Mot de passe du keystore (ou Entrée pour 'macartedetarot2024'): ").strip()
    if not keystore_password:
        keystore_password = "macartedetarot2024"
    
    key_alias = input("🔑 Alias de la clé (ou Entrée pour 'upload'): ").strip()
    if not key_alias:
        key_alias = "upload"
    
    key_password = input("🔐 Mot de passe de la clé (ou Entrée pour utiliser le même): ").strip()
    if not key_password:
        key_password = keystore_password
    
    # Informations du certificat
    print("\n📋 Informations du certificat (ou Entrée pour valeurs par défaut):")
    
    cn = input("Nom (CN) [Ma Carte de Tarot]: ").strip() or "Ma Carte de Tarot"
    ou = input("Unité organisationnelle (OU) [Development]: ").strip() or "Development"
    o = input("Organisation (O) [Tarot App]: ").strip() or "Tarot App"
    city = input("Ville (L) [Paris]: ").strip() or "Paris"
    state = input("État/Province (S) [IDF]: ").strip() or "IDF"
    country = input("Code pays (C) [FR]: ").strip() or "FR"
    
    # Construire le DN (Distinguished Name)
    dname = f"CN={cn}, OU={ou}, O={o}, L={city}, S={state}, C={country}"
    
    # Générer la clé
    keytool_cmd = [
        "keytool", "-genkeypair", "-v",
        "-keystore", "googleplay.keystore",
        "-alias", key_alias,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-dname", dname,
        "-storepass", keystore_password,
        "-keypass", key_password
    ]
    
    print(f"🔨 Génération de la clé avec l'alias '{key_alias}'...")
    result = subprocess.run(keytool_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Nouvelle clé générée avec succès!")
        return keystore_password, key_alias, key_password
    else:
        print(f"❌ Erreur lors de la génération: {result.stderr}")
        return None, None, None

def verify_keystore(password, alias):
    """Vérifie la clé générée"""
    print("🔍 Vérification de la nouvelle clé...")
    
    cmd = ["keytool", "-list", "-keystore", "googleplay.keystore", "-storepass", password, "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Clé vérifiée avec succès!")
        print(f"📋 Alias trouvé: {alias}")
        return True
    else:
        print(f"❌ Erreur de vérification: {result.stderr}")
        return False

def encode_keystore():
    """Encode la clé en base64"""
    print("🔐 Encodage de la clé...")
    
    with open("googleplay.keystore", "rb") as f:
        keystore_data = f.read()
    
    keystore_base64 = base64.b64encode(keystore_data).decode('utf-8')
    
    with open("keystore_base64.txt", "w") as f:
        f.write(keystore_base64)
    
    print("✅ Clé encodée et sauvegardée dans 'keystore_base64.txt'")
    return keystore_base64

def update_buildozer_spec(keystore_password, key_alias, key_password):
    """Met à jour buildozer.spec avec les nouvelles informations"""
    print("📝 Mise à jour de buildozer.spec...")
    
    # Lire le fichier existant
    with open("buildozer.spec", "r") as f:
        content = f.read()
    
    # Supprimer les anciennes configurations de signature
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if not any(keyword in line for keyword in [
            'android.release_keystore',
            'android.release_key',
            '# Configuration signature'
        ]):
            new_lines.append(line)
    
    # Ajouter la nouvelle configuration
    new_lines.append("")
    new_lines.append("# Configuration signature de production")
    new_lines.append("android.release_keystore = googleplay.keystore")
    new_lines.append(f"android.release_keystore_passwd = {keystore_password}")
    new_lines.append(f"android.release_key = {key_alias}")
    new_lines.append(f"android.release_key_passwd = {key_password}")
    new_lines.append("android.release_artifact = aab")
    
    # Sauvegarder
    with open("buildozer.spec", "w") as f:
        f.write('\n'.join(new_lines))
    
    print("✅ buildozer.spec mis à jour")

def generate_github_secrets_script(keystore_base64, keystore_password, key_alias, key_password):
    """Génère le script de configuration des secrets GitHub"""
    print("📝 Génération du script de configuration des secrets...")
    
    # Script PowerShell
    ps_script = f'''# Configuration des secrets GitHub pour la nouvelle clé
Write-Host "🔐 Configuration des secrets GitHub..." -ForegroundColor Cyan

# Configurer les secrets
gh secret set ANDROID_KEYSTORE --body "{keystore_base64}"
gh secret set ANDROID_KEYSTORE_PASSWORD --body "{keystore_password}"
gh secret set ANDROID_KEY_ALIAS --body "{key_alias}"
gh secret set ANDROID_KEY_PASSWORD --body "{key_password}"

# Vérifier les secrets
gh secret list

Write-Host "✅ Secrets configurés avec succès!" -ForegroundColor Green
'''
    
    with open("configure_new_secrets.ps1", "w") as f:
        f.write(ps_script)
    
    # Script Bash
    bash_script = f'''#!/bin/bash
# Configuration des secrets GitHub pour la nouvelle clé
echo "🔐 Configuration des secrets GitHub..."

# Configurer les secrets
gh secret set ANDROID_KEYSTORE --body "{keystore_base64}"
gh secret set ANDROID_KEYSTORE_PASSWORD --body "{keystore_password}"
gh secret set ANDROID_KEY_ALIAS --body "{key_alias}"
gh secret set ANDROID_KEY_PASSWORD --body "{key_password}"

# Vérifier les secrets
gh secret list

echo "✅ Secrets configurés avec succès!"
'''
    
    with open("configure_new_secrets.sh", "w") as f:
        f.write(bash_script)
    
    # Rendre le script bash exécutable
    os.chmod("configure_new_secrets.sh", 0o755)
    
    print("✅ Scripts de configuration créés:")
    print("   - configure_new_secrets.ps1 (PowerShell)")
    print("   - configure_new_secrets.sh (Bash)")

def main():
    """Fonction principale"""
    print("🔮 Génération d'une nouvelle clé de signature pour Ma Carte de Tarot")
    print("=" * 70)
    
    # Vérifier que keytool est disponible
    if not run_command("keytool -help", "Vérification de keytool"):
        print("❌ keytool n'est pas disponible. Installez le JDK Java.")
        sys.exit(1)
    
    # Générer la nouvelle clé
    keystore_password, key_alias, key_password = generate_new_keystore()
    
    if not keystore_password:
        print("❌ Échec de la génération de la clé")
        sys.exit(1)
    
    # Vérifier la clé
    if not verify_keystore(keystore_password, key_alias):
        print("❌ Échec de la vérification de la clé")
        sys.exit(1)
    
    # Encoder la clé
    keystore_base64 = encode_keystore()
    
    # Mettre à jour buildozer.spec
    update_buildozer_spec(keystore_password, key_alias, key_password)
    
    # Générer les scripts de configuration
    generate_github_secrets_script(keystore_base64, keystore_password, key_alias, key_password)
    
    print("\n🎯 RÉSUMÉ:")
    print("=" * 40)
    print("📁 Keystore: googleplay.keystore")
    print(f"🔐 Mot de passe: {keystore_password}")
    print(f"🔑 Alias: {key_alias}")
    print(f"🔐 Mot de passe clé: {key_password}")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("1. 📋 Exécutez le script de configuration des secrets:")
    print("   PowerShell: .\\configure_new_secrets.ps1")
    print("   Bash: ./configure_new_secrets.sh")
    print("2. 🏷️ Créez un nouveau tag:")
    print("   git add .")
    print("   git commit -m 'feat: nouvelle clé de signature'")
    print("   git tag v1.4.0")
    print("   git push origin main")
    print("   git push origin v1.4.0")
    print("3. 📱 Vérifiez le pipeline sur GitHub Actions")
    
    print("\n💡 IMPORTANT:")
    print("- Sauvegardez le mot de passe dans un gestionnaire sécurisé")
    print("- La nouvelle clé sera utilisée pour toutes les futures versions")
    print("- L'ancienne clé a été sauvegardée en .backup")
    
    print("\n🔮 Votre nouvelle clé de signature est prête! ✨")

if __name__ == "__main__":
    main()
