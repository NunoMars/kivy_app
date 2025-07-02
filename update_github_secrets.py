#!/usr/bin/env python3
"""
Script pour mettre à jour les secrets GitHub avec la nouvelle clé de production
"""
import os

def read_file_content(file_path):
    """Lit le contenu d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Erreur lecture {file_path}: {e}")
        return None

def main():
    print("🔐 MISE À JOUR DES SECRETS GITHUB")
    print("=" * 50)
    
    # Lecture de la clé encodée en base64
    base64_key = read_file_content('googleplay-base64.txt')
    if not base64_key:
        print("❌ Impossible de lire googleplay-base64.txt")
        return
    
    # Nettoyage de la clé base64 (suppression des headers/footers)
    lines = base64_key.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('-----'):
            clean_lines.append(line)
    
    clean_base64 = ''.join(clean_lines)
    
    print("✅ Clé de signature encodée en base64")
    print(f"📏 Taille: {len(clean_base64)} caractères")
    
    # Informations sur les secrets à mettre à jour
    secrets_info = {
        'ANDROID_KEYSTORE': {
            'value': clean_base64,
            'description': 'Clé de signature Android (googleplay.keystore) encodée en base64'
        },
        'ANDROID_KEYSTORE_PASSWORD': {
            'value': 'GooglePlay2025!',
            'description': 'Mot de passe du keystore'
        },
        'ANDROID_KEY_ALIAS': {
            'value': 'googleplay',
            'description': 'Alias de la clé'
        },
        'ANDROID_KEY_PASSWORD': {
            'value': 'GooglePlay2025!',
            'description': 'Mot de passe de la clé'
        }
    }
    
    print("\n📝 SECRETS À METTRE À JOUR DANS GITHUB:")
    print("-" * 40)
    
    for secret_name, info in secrets_info.items():
        print(f"🔑 {secret_name}")
        print(f"   📄 {info['description']}")
        if secret_name == 'ANDROID_KEYSTORE':
            print(f"   📏 Valeur: {info['value'][:50]}... ({len(info['value'])} caractères)")
        else:
            print(f"   📏 Valeur: {info['value']}")
        print()
    
    print("🚀 INSTRUCTIONS:")
    print("1. Allez sur GitHub.com > Settings > Secrets and variables > Actions")
    print("2. Pour chaque secret ci-dessus:")
    print("   - Cliquez sur 'New repository secret' (ou 'Update' si existe)")
    print("   - Nom: nom du secret")
    print("   - Valeur: valeur indiquée")
    print("   - Cliquez 'Add secret'")
    print()
    
    # Vérification de la clé de service Google Play
    service_account_file = 'google-play-service-account.json'
    if os.path.exists(service_account_file):
        service_account_content = read_file_content(service_account_file)
        if service_account_content:
            print("✅ Clé de service Google Play trouvée")
            print("🔑 GOOGLE_PLAY_SERVICE_ACCOUNT")
            print(f"   📄 Contenu du fichier {service_account_file}")
            print(f"   📏 Taille: {len(service_account_content)} caractères")
            print("   💡 Copiez tout le contenu JSON dans le secret GOOGLE_PLAY_SERVICE_ACCOUNT")
            print()
    else:
        print("⚠️  Clé de service Google Play non trouvée")
        print("💡 Créez d'abord la clé avec: python setup_google_play_api.py")
        print()
    
    print("✅ APRÈS MISE À JOUR DES SECRETS:")
    print("- Testez le workflow: git tag v1.0.1 && git push origin v1.0.1")
    print("- Vérifiez le build dans Actions > Build Android")
    print("- L'AAB sera automatiquement uploadé sur Google Play Console")

if __name__ == "__main__":
    main()
