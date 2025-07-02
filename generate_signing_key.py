#!/usr/bin/env python3
"""
Script pour générer une clé de signature Android et préparer les secrets GitHub.
ATTENTION: Ce script génère une VRAIE clé de production - gardez-la en sécurité !
"""
import os
import subprocess
import sys
import base64
import getpass


def run_command(cmd, capture_output=True):
    """Exécuter une commande avec gestion d'erreur"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def generate_android_keystore():
    """Générer une clé de signature Android pour production"""
    
    print("🔑 Génération d'une clé de signature Android pour Google Play Store")
    print("=" * 70)
    print("⚠️  ATTENTION: Cette clé sera utilisée pour signer votre application")
    print("   Gardez-la en sécurité et ne la perdez jamais !")
    print("   Google Play n'accepte que les AAB signés avec la même clé.")
    print("")
    
    # Paramètres de la clé
    keystore_file = "macartedetarot-release.keystore"
    key_alias = "macartedetarot"
    
    # Demander les mots de passe
    print("📋 Configuration de la clé de signature:")
    keystore_password = getpass.getpass("Mot de passe du keystore (min 6 caractères): ")
    if len(keystore_password) < 6:
        print("❌ Le mot de passe doit faire au moins 6 caractères")
        return False
    
    key_password = getpass.getpass("Mot de passe de la clé (min 6 caractères): ")
    if len(key_password) < 6:
        print("❌ Le mot de passe doit faire au moins 6 caractères")
        return False
    
    # Informations du certificat
    print("\n📄 Informations du certificat (pour Google Play Store):")
    cn = input("Nom complet ou nom de l'organisation [Ma Carte de Tarot]: ") or "Ma Carte de Tarot"
    ou = input("Unité organisationnelle [Mobile Apps]: ") or "Mobile Apps"
    o = input("Organisation [Tarot Software]: ") or "Tarot Software"
    city = input("Ville [Paris]: ") or "Paris"
    st = input("État/Province [Ile-de-France]: ") or "Ile-de-France"
    c = input("Code pays (2 lettres) [FR]: ") or "FR"
    
    # Construire le DN
    dname = f"CN={cn}, OU={ou}, O={o}, L={city}, ST={st}, C={c}"
    
    # Commande keytool (Windows - pas de continuation de ligne)
    keytool_cmd = f'keytool -genkey -v -keystore {keystore_file} -alias {key_alias} -keyalg RSA -keysize 2048 -validity 10000 -dname "{dname}" -storepass "{keystore_password}" -keypass "{key_password}"'
    
    print(f"\n🔧 Génération de la clé: {keystore_file}")
    print("   (Ceci peut prendre quelques secondes...)")
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(keystore_file):
        overwrite = input(f"⚠️  Le fichier {keystore_file} existe déjà. Écraser ? (y/N): ")
        if overwrite.lower() != 'y':
            print("❌ Génération annulée")
            return False
        os.remove(keystore_file)
    
    # Générer la clé
    success, stdout, stderr = run_command(keytool_cmd, capture_output=False)
    
    if not success:
        print("❌ Erreur lors de la génération de la clé:")
        print(f"STDERR: {stderr}")
        return False
    
    if not os.path.exists(keystore_file):
        print(f"❌ Le fichier {keystore_file} n'a pas été créé")
        return False
    
    print(f"✅ Clé de signature créée: {keystore_file}")
    
    # Vérifier la clé
    verify_cmd = f'keytool -list -keystore {keystore_file} -storepass "{keystore_password}"'
    success, stdout, stderr = run_command(verify_cmd)
    
    if success:
        print("✅ Clé vérifiée avec succès")
        print(f"📋 Informations de la clé:")
        print(stdout)
    else:
        print("⚠️  Impossible de vérifier la clé")
    
    # Encoder en base64
    print(f"\n🔒 Encodage de la clé en base64 pour GitHub...")
    
    try:
        with open(keystore_file, "rb") as f:
            keystore_data = f.read()
        
        keystore_base64 = base64.b64encode(keystore_data).decode('utf-8')
        
        # Sauvegarder le base64
        base64_file = f"{keystore_file}.base64"
        with open(base64_file, "w") as f:
            f.write(keystore_base64)
        
        print(f"✅ Clé encodée sauvegardée: {base64_file}")
        
        # Afficher les secrets GitHub
        print("\n" + "="*70)
        print("🔑 SECRETS GITHUB À CONFIGURER")
        print("="*70)
        print("Allez dans GitHub Settings > Secrets and variables > Actions")
        print("et ajoutez ces secrets:")
        print()
        print(f"ANDROID_KEYSTORE_BASE64:")
        print(f"{keystore_base64}")
        print()
        print(f"KEYSTORE_PASSWORD:")
        print(f"{keystore_password}")
        print()
        print(f"KEY_ALIAS:")
        print(f"{key_alias}")
        print()
        print(f"KEY_PASSWORD:")
        print(f"{key_password}")
        print()
        print("="*70)
        print("⚠️  SÉCURITÉ IMPORTANTE:")
        print("1. Gardez le fichier .keystore en sécurité (backup hors-ligne)")
        print("2. Ne committez JAMAIS le fichier .keystore dans Git")
        print("3. Les mots de passe ne doivent être connus que de vous")
        print("4. Si vous perdez cette clé, vous ne pourrez plus mettre à jour l'app sur Google Play")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'encodage: {e}")
        return False


def create_gitignore_entry():
    """Ajouter les fichiers de clé au .gitignore"""
    
    gitignore_entries = [
        "\n# Android signing keys (NEVER commit these!)",
        "*.keystore",
        "*.keystore.base64",
        "android_signing_key*",
        "release.keystore*",
        "macartedetarot-release.keystore*"
    ]
    
    gitignore_file = ".gitignore"
    
    # Lire le .gitignore existant
    existing_content = ""
    if os.path.exists(gitignore_file):
        with open(gitignore_file, "r") as f:
            existing_content = f.read()
    
    # Ajouter les entrées si elles n'existent pas
    updated = False
    for entry in gitignore_entries:
        if entry.strip() not in existing_content:
            existing_content += entry + "\n"
            updated = True
    
    if updated:
        with open(gitignore_file, "w") as f:
            f.write(existing_content)
        print(f"✅ Fichiers de signature ajoutés au .gitignore")
    else:
        print("ℹ️  .gitignore déjà à jour")


def main():
    """Point d'entrée principal"""
    print("🔐 Générateur de Clé de Signature Android - Ma Carte de Tarot")
    print("=" * 70)
    
    # Vérifier que keytool est disponible
    success, _, _ = run_command("keytool -help")
    if not success:
        print("❌ keytool non trouvé")
        print("   Installez Java JDK (OpenJDK 17 recommandé)")
        return 1
    
    print("✅ keytool disponible")
    
    # Générer la clé
    if not generate_android_keystore():
        print("❌ Échec de la génération de la clé")
        return 1
    
    # Mettre à jour .gitignore
    create_gitignore_entry()
    
    print("\n🎉 CLÉS DE SIGNATURE GÉNÉRÉES AVEC SUCCÈS !")
    print("📋 Prochaines étapes:")
    print("   1. Configurez les secrets GitHub avec les valeurs affichées ci-dessus")
    print("   2. Sauvegardez le fichier .keystore dans un endroit sûr")
    print("   3. Testez le build avec: git tag v1.0.1 && git push origin v1.0.1")
    print("   4. L'AAB sera maintenant correctement signé pour Google Play Store")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
