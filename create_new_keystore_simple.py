#!/usr/bin/env python3
"""
Script simplifié pour générer une nouvelle clé de signature Android
"""

import subprocess
import base64
from pathlib import Path

def main():
    print("🔮 Génération d'une nouvelle clé de signature pour Ma Carte de Tarot")
    print("=" * 70)
    
    # Sauvegarder l'ancienne clé si elle existe
    if Path("googleplay.keystore").exists():
        backup_name = "googleplay.keystore.backup"
        Path("googleplay.keystore").rename(backup_name)
        print(f"📦 Ancienne clé sauvegardée dans {backup_name}")
    
    # Paramètres de la nouvelle clé
    keystore_password = "macartedetarot2024"
    key_alias = "upload"
    key_password = keystore_password
    
    print(f"🔐 Mot de passe: {keystore_password}")
    print(f"🔑 Alias: {key_alias}")
    
    # Générer la clé avec keytool
    print("🔨 Génération de la clé...")
    
    cmd = [
        "keytool", "-genkeypair", "-v",
        "-keystore", "googleplay.keystore",
        "-alias", key_alias,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-dname", "CN=Ma Carte de Tarot, OU=Development, O=Tarot App, L=Paris, S=IDF, C=FR",
        "-storepass", keystore_password,
        "-keypass", key_password
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Clé générée avec succès!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la génération: {e.stderr}")
        return False
    
    # Vérifier la clé
    print("🔍 Vérification de la clé...")
    verify_cmd = ["keytool", "-list", "-keystore", "googleplay.keystore", "-storepass", keystore_password, "-v"]
    
    try:
        subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
        print("✅ Clé vérifiée avec succès!")
        print(f"📋 Alias trouvé: {key_alias}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur de vérification: {e.stderr}")
        return False
    
    # Encoder la clé en base64
    print("🔐 Encodage de la clé...")
    
    with open("googleplay.keystore", "rb") as f:
        keystore_data = f.read()
    
    keystore_base64 = base64.b64encode(keystore_data).decode('utf-8')
    
    with open("keystore_base64.txt", "w") as f:
        f.write(keystore_base64)
    
    print("✅ Clé encodée et sauvegardée dans 'keystore_base64.txt'")
    
    # Mettre à jour buildozer.spec
    print("📝 Mise à jour de buildozer.spec...")
    
    with open("buildozer.spec", "r") as f:
        content = f.read()
    
    # Supprimer les anciennes configurations
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
    
    with open("buildozer.spec", "w") as f:
        f.write('\n'.join(new_lines))
    
    print("✅ buildozer.spec mis à jour")
    
    # Créer le script PowerShell de configuration
    print("📝 Création du script PowerShell...")
    
    ps_script = f'''# Configuration des secrets GitHub
Write-Host "Configuration des secrets GitHub..." -ForegroundColor Cyan

gh secret set ANDROID_KEYSTORE --body "{keystore_base64}"
gh secret set ANDROID_KEYSTORE_PASSWORD --body "{keystore_password}"
gh secret set ANDROID_KEY_ALIAS --body "{key_alias}"
gh secret set ANDROID_KEY_PASSWORD --body "{key_password}"

gh secret list

Write-Host "Secrets configures!" -ForegroundColor Green
'''
    
    with open("configure_new_secrets.ps1", "w", encoding='utf-8') as f:
        f.write(ps_script)
    
    print("✅ Script PowerShell créé: configure_new_secrets.ps1")
    
    # Mettre à jour la version
    print("📝 Mise à jour de la version...")
    
    with open("buildozer.spec", "r") as f:
        content = f.read()
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('version ='):
            lines[i] = "version = 1.4"
            break
    
    with open("buildozer.spec", "w") as f:
        f.write('\n'.join(lines))
    
    print("✅ Version mise à jour à 1.4")
    
    print("\n🎯 RÉSUMÉ:")
    print("=" * 40)
    print("📁 Keystore: googleplay.keystore")
    print(f"🔐 Mot de passe: {keystore_password}")
    print(f"🔑 Alias: {key_alias}")
    print("📝 Version: 1.4")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("1. 📋 Configurez les secrets GitHub:")
    print("   .\\configure_new_secrets.ps1")
    print("2. 🏷️ Déployez la nouvelle version:")
    print("   git add .")
    print("   git commit -m 'feat: nouvelle clé de signature v1.4'")
    print("   git tag v1.4.0")
    print("   git push origin main")
    print("   git push origin v1.4.0")
    
    print("\n🔮 Nouvelle clé créée avec succès! ✨")
    return True

if __name__ == "__main__":
    main()
