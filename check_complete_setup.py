#!/usr/bin/env python3
"""
🔍 Script de Vérification Complète des Clés
Vérifie la configuration des clés de signature Android et API Google Play
"""

import os
import json
from pathlib import Path

def check_android_signing_key():
    """Vérifie la clé de signature Android"""
    print("🔐 VÉRIFICATION CLÉ DE SIGNATURE ANDROID")
    print("=" * 50)
    
    keystore_files = list(Path(".").glob("*.keystore"))
    config_files = list(Path(".").glob("*.keystore.config"))
    base64_files = list(Path(".").glob("*.keystore.base64"))
    
    if keystore_files:
        keystore_file = keystore_files[0]
        print(f"✅ Clé de signature trouvée : {keystore_file}")
        print(f"📁 Taille : {os.path.getsize(keystore_file)} bytes")
        
        if config_files:
            config_file = config_files[0]
            print(f"✅ Configuration trouvée : {config_file}")
            
            # Lire la configuration
            try:
                with open(config_file, 'r') as f:
                    config_content = f.read()
                
                print("📋 Configuration détectée :")
                for line in config_content.split('\n'):
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        if 'PASSWORD' in key:
                            print(f"   {key} = {'*' * len(value)}")
                        else:
                            print(f"   {key} = {value}")
            except Exception as e:
                print(f"⚠️  Erreur lecture config : {e}")
        
        if base64_files:
            base64_file = base64_files[0]
            print(f"✅ Fichier base64 trouvé : {base64_file}")
            print(f"📁 Taille : {os.path.getsize(base64_file)} bytes")
        else:
            print("❌ Fichier base64 manquant")
            
        return True
    else:
        print("❌ Aucune clé de signature Android trouvée")
        print("💡 Exécutez : python generate_auto_signing_key.py")
        return False

def check_google_play_api():
    """Vérifie les fichiers API Google Play"""
    print("\n🚀 VÉRIFICATION API GOOGLE PLAY")
    print("=" * 50)
    
    json_patterns = [
        "*service-account*.json",
        "*google-play*.json", 
        "*api-key*.json",
        "*-publish-*.json"
    ]
    
    json_files = []
    for pattern in json_patterns:
        json_files.extend(list(Path(".").glob(pattern)))
    
    if json_files:
        json_file = json_files[0]
        print(f"✅ Fichier API Google Play trouvé : {json_file}")
        print(f"📁 Taille : {os.path.getsize(json_file)} bytes")
        
        # Vérifier le contenu JSON
        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            print("📋 Contenu JSON validé :")
            required_fields = ["type", "project_id", "private_key", "client_email"]
            for field in required_fields:
                if field in json_data:
                    if field == "private_key":
                        print(f"   ✅ {field} : -----BEGIN PRIVATE KEY-----...")
                    else:
                        print(f"   ✅ {field} : {json_data[field]}")
                else:
                    print(f"   ❌ {field} : MANQUANT")
                    
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide : {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lecture : {e}")
            return False
    else:
        print("❌ Aucun fichier API Google Play trouvé")
        print("💡 Suivez : GOOGLE_PLAY_API_SETUP.md")
        return False

def check_gitignore():
    """Vérifie la protection .gitignore"""
    print("\n🛡️  VÉRIFICATION SÉCURITÉ (.gitignore)")
    print("=" * 50)
    
    if not os.path.exists(".gitignore"):
        print("❌ Fichier .gitignore manquant")
        return False
    
    with open(".gitignore", 'r') as f:
        gitignore_content = f.read()
    
    security_patterns = [
        "*.keystore",
        "*.keystore.base64", 
        "*.keystore.config",
        "*service-account*.json"
    ]
    
    protected_count = 0
    for pattern in security_patterns:
        if pattern in gitignore_content:
            print(f"✅ Protégé : {pattern}")
            protected_count += 1
        else:
            print(f"⚠️  Non protégé : {pattern}")
    
    if protected_count == len(security_patterns):
        print("🛡️  Sécurité : EXCELLENT")
        return True
    elif protected_count > 0:
        print("🟡 Sécurité : PARTIELLE")
        return True
    else:
        print("🔴 Sécurité : DANGER - Fichiers sensibles non protégés")
        return False

def display_github_secrets_status():
    """Affiche le statut des secrets GitHub à configurer"""
    print("\n🔑 SECRETS GITHUB À CONFIGURER")
    print("=" * 50)
    
    print("🌐 URL : https://github.com/VOTRE_USERNAME/kivy_app/settings/secrets/actions")
    print()
    
    # Lire la configuration pour afficher les valeurs
    config_files = list(Path(".").glob("*.keystore.config"))
    
    if config_files:
        config_file = config_files[0]
        try:
            config_data = {}
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config_data[key] = value
            
            print("🔐 SIGNATURE ANDROID (OBLIGATOIRE) :")
            secrets = [
                ("ANDROID_KEYSTORE_BASE64", "Contenu du fichier .base64"),
                ("KEYSTORE_PASSWORD", config_data.get("KEYSTORE_PASSWORD", "???")),
                ("KEY_ALIAS", config_data.get("KEY_ALIAS", "???")),
                ("KEY_PASSWORD", config_data.get("KEY_PASSWORD", "???"))
            ]
            
            for i, (secret_name, secret_value) in enumerate(secrets, 1):
                if secret_name == "ANDROID_KEYSTORE_BASE64":
                    print(f"{i}. {secret_name}")
                    print(f"   📄 Copiez le contenu de : {config_data.get('BASE64_FILE', '*.base64')}")
                else:
                    print(f"{i}. {secret_name}")
                    print(f"   🔑 Valeur : {secret_value}")
                print()
                
        except Exception as e:
            print(f"⚠️  Erreur lecture config : {e}")
    
    print("🚀 PUBLICATION AUTOMATIQUE (OPTIONNEL) :")
    print("5. GOOGLE_PLAY_SERVICE_ACCOUNT")
    print("   📄 Copiez le contenu JSON complet du service account")
    print()

def analyze_deployment_readiness():
    """Analyse la préparation pour le déploiement"""
    print("\n🎯 ANALYSE DE PRÉPARATION DÉPLOIEMENT")
    print("=" * 50)
    
    has_android_key = len(list(Path(".").glob("*.keystore"))) > 0
    has_google_api = len(list(Path(".").glob("*service-account*.json"))) > 0 or \
                     len(list(Path(".").glob("*google-play*.json"))) > 0
    
    scenarios = [
        {
            "name": "🔴 AUCUNE CLÉ",
            "condition": not has_android_key and not has_google_api,
            "capabilities": [
                "❌ Build AAB signé",
                "❌ Upload Google Play", 
                "❌ Publication automatique"
            ],
            "action": "🚨 URGENT : Exécuter generate_auto_signing_key.py"
        },
        {
            "name": "🟡 CLÉ ANDROID SEULEMENT", 
            "condition": has_android_key and not has_google_api,
            "capabilities": [
                "✅ Build AAB signé",
                "📱 Upload manuel Google Play",
                "📱 Publication manuelle"
            ],
            "action": "🎯 PRÊT pour test : .\\deploy.ps1 v1.0.1"
        },
        {
            "name": "🟢 CONFIGURATION COMPLÈTE",
            "condition": has_android_key and has_google_api, 
            "capabilities": [
                "✅ Build AAB signé",
                "🚀 Upload automatique Google Play",
                "🚀 Publication automatique track internal"
            ],
            "action": "🌟 OPTIMAL : Déploiement automatisé complet"
        }
    ]
    
    current_scenario = None
    for scenario in scenarios:
        if scenario["condition"]:
            current_scenario = scenario
            break
    
    if current_scenario:
        print(f"📊 STATUT ACTUEL : {current_scenario['name']}")
        print("\n🎯 Capacités disponibles :")
        for capability in current_scenario["capabilities"]:
            print(f"   {capability}")
        print(f"\n💡 Action recommandée :")
        print(f"   {current_scenario['action']}")
    
    return current_scenario

def provide_next_steps():
    """Fournit les étapes suivantes"""
    print(f"\n{'🎯' * 20}")
    print("ÉTAPES SUIVANTES RECOMMANDÉES")
    print("=" * 60)
    
    has_android_key = len(list(Path(".").glob("*.keystore"))) > 0
    
    if not has_android_key:
        print("1. 🔴 URGENT : Générer la clé de signature Android")
        print("   💻 python generate_auto_signing_key.py")
        print("   🎯 Résout l'erreur 'AAB doit être signé'")
        print()
        print("2. 🔐 Configurer les 4 secrets GitHub de signature")
        print("   🌐 GitHub → Settings → Secrets → Actions")
        print("   🎯 Permet le build AAB signé")
        print()
        print("3. 🚀 Tester le déploiement")
        print("   💻 .\\deploy.ps1 v1.0.1")
        print("   🎯 Valide la solution complète")
    else:
        print("1. ✅ Clé de signature Android : OK")
        print()
        print("2. 🔐 Vérifier les secrets GitHub")
        print("   🌐 GitHub → Settings → Secrets → Actions")
        print("   🎯 4 secrets obligatoires + 1 optionnel")
        print()
        print("3. 🚀 Tester le déploiement") 
        print("   💻 .\\deploy.ps1 v1.0.1")
        print("   🎯 Build AAB + Upload Google Play")
        print()
        print("4. 🎯 [OPTIONNEL] Configurer API Google Play")
        print("   📖 Suivre GOOGLE_PLAY_API_SETUP.md")
        print("   🎯 Publication automatique complète")

def main():
    """Fonction principale"""
    print("🔍 VÉRIFICATION COMPLÈTE DE LA CONFIGURATION")
    print("=" * 60)
    print("Analyse de votre configuration pour la publication Google Play")
    
    # Vérifications
    android_ok = check_android_signing_key()
    google_api_ok = check_google_play_api()
    security_ok = check_gitignore()
    
    # Statut secrets GitHub
    display_github_secrets_status()
    
    # Analyse de préparation
    scenario = analyze_deployment_readiness()
    
    # Étapes suivantes
    provide_next_steps()
    
    # Résumé final
    print(f"\n{'=' * 60}")
    print("📋 RÉSUMÉ FINAL")
    print("=" * 60)
    
    score = sum([android_ok, security_ok]) + (0.5 if google_api_ok else 0)
    max_score = 2.5
    
    if score >= 2.5:
        status = "🌟 EXCELLENT"
        message = "Configuration optimale pour publication automatisée"
    elif score >= 2.0:
        status = "🟢 TRÈS BON"
        message = "Prêt pour publication avec upload manuel"
    elif score >= 1.0:
        status = "🟡 EN COURS"
        message = "Configuration partielle, actions requises"
    else:
        status = "🔴 À FAIRE"
        message = "Configuration minimale requise"
    
    print(f"🎯 STATUT GLOBAL : {status} ({score}/{max_score})")
    print(f"💬 {message}")
    
    if android_ok:
        print("🎉 Votre problème 'AAB doit être signé' sera résolu !")
    else:
        print("⚠️  Problème 'AAB doit être signé' non encore résolu")

if __name__ == "__main__":
    main()
