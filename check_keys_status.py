#!/usr/bin/env python3
"""
🔍 Script de Vérification du Statut des Clés
Vérifie quelle configuration de clés vous avez et ce qui manque.
"""

from pathlib import Path

def check_local_keys():
    """Vérifie les clés présentes localement"""
    print("\n🔍 VÉRIFICATION DES CLÉS LOCALES")
    print("=" * 50)
    
    keystore_files = list(Path(".").glob("*.keystore"))
    if keystore_files:
        print(f"✅ Clé de signature Android trouvée : {keystore_files[0]}")
        return True
    else:
        print("❌ Aucune clé de signature Android (.keystore) trouvée")
        return False

def check_github_secrets_guide():
    """Guide pour vérifier les secrets GitHub"""
    print("\n🔐 SECRETS GITHUB À CONFIGURER")
    print("=" * 50)
    
    required_secrets = [
        ("ANDROID_KEYSTORE_BASE64", "Clé Android encodée en base64", "OBLIGATOIRE"),
        ("KEYSTORE_PASSWORD", "Mot de passe du keystore", "OBLIGATOIRE"),
        ("KEY_ALIAS", "Alias de la clé (ex: macartedetarot)", "OBLIGATOIRE"),
        ("KEY_PASSWORD", "Mot de passe de la clé", "OBLIGATOIRE"),
        ("GOOGLE_PLAY_SERVICE_ACCOUNT", "JSON API Google Play", "OPTIONNEL")
    ]
    
    print("Pour vérifier les secrets GitHub :")
    print("👉 Allez sur : https://github.com/VOTRE_USERNAME/VOTRE_REPO/settings/secrets/actions")
    print()
    
    for secret, description, status in required_secrets:
        status_icon = "🔴" if status == "OBLIGATOIRE" else "🟡"
        print(f"{status_icon} {secret:<30} | {description}")
    
    print(f"\n{'=' * 70}")
    print("🎯 PRIORITÉ ABSOLUE : Les 4 premiers secrets (signature Android)")
    print("🚀 BONUS : Le dernier secret (publication automatique)")

def analyze_workflow_features():
    """Analyse les fonctionnalités disponibles selon la configuration"""
    print("\n📊 FONCTIONNALITÉS SELON CONFIGURATION")
    print("=" * 50)
    
    scenarios = [
        {
            "config": "AUCUNE CLÉ",
            "build": "❌ Échec",
            "upload": "❌ Impossible",
            "publish": "❌ Impossible",
            "status": "🔴 BLOQUANT"
        },
        {
            "config": "CLÉ ANDROID SEULEMENT",
            "build": "✅ AAB signé",
            "upload": "✅ Manuel sur Play Console",
            "publish": "📱 Manuel depuis Play Console",
            "status": "🟢 FONCTIONNEL"
        },
        {
            "config": "CLÉ ANDROID + API GOOGLE PLAY",
            "build": "✅ AAB signé",
            "upload": "🚀 Automatique via GitHub",
            "publish": "🚀 Automatique sur track internal",
            "status": "🌟 OPTIMAL"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['status']} {scenario['config']}")
        print(f"   📦 Build AAB    : {scenario['build']}")
        print(f"   📤 Upload       : {scenario['upload']}")
        print(f"   🚀 Publication  : {scenario['publish']}")

def provide_next_steps():
    """Fournit les étapes suivantes recommandées"""
    print("\n🎯 ÉTAPES RECOMMANDÉES")
    print("=" * 50)
    
    steps = [
        {
            "step": "1. Générer la clé de signature Android",
            "command": "python generate_signing_key.py",
            "result": "Créé un fichier .keystore",
            "priority": "🔴 URGENT"
        },
        {
            "step": "2. Configurer les secrets GitHub (signature)",
            "command": "Suivre SIGNING_KEY_SOLUTION.md",
            "result": "4 secrets configurés dans GitHub",
            "priority": "🔴 URGENT"
        },
        {
            "step": "3. Tester le build",
            "command": ".\\deploy.ps1 v1.0.1",
            "result": "AAB signé généré",
            "priority": "🟡 TEST"
        },
        {
            "step": "4. Upload manuel sur Play Console",
            "command": "Via interface web Google Play",
            "result": "Version publiée manuellement",
            "priority": "🟢 VALIDATION"
        },
        {
            "step": "5. [OPTIONNEL] Configurer API Google Play",
            "command": "Suivre GOOGLE_PLAY_KEYS_GUIDE.md",
            "result": "Publication automatique",
            "priority": "🚀 BONUS"
        }
    ]
    
    for step_info in steps:
        print(f"\n{step_info['priority']} {step_info['step']}")
        print(f"   💻 Commande : {step_info['command']}")
        print(f"   🎯 Résultat : {step_info['result']}")

def check_google_play_api_files():
    """Vérifie si des fichiers d'API Google Play existent"""
    print("\n📱 VÉRIFICATION API GOOGLE PLAY")
    print("=" * 50)
    
    json_files = list(Path(".").glob("*service-account*.json")) + \
                 list(Path(".").glob("*google-play*.json")) + \
                 list(Path(".").glob("*api-key*.json"))
    
    if json_files:
        print(f"✅ Fichier API Google Play trouvé : {json_files[0]}")
        print("⚠️  ATTENTION : Ce fichier contient des secrets sensibles !")
        print("   👉 Assurez-vous qu'il est dans .gitignore")
        return True
    else:
        print("❌ Aucun fichier API Google Play trouvé")
        print("💡 Pas grave ! L'API Google Play n'est qu'optionnelle")
        return False

def main():
    """Fonction principale"""
    print("🔑 VÉRIFICATION DU STATUT DES CLÉS")
    print("=" * 60)
    print("Ce script vérifie votre configuration actuelle et vous guide")
    print("vers la solution pour publier sur Google Play Console.")
    
    # Vérifications
    has_android_key = check_local_keys()
    has_google_play_api = check_google_play_api_files()
    
    # Guide des secrets GitHub
    check_github_secrets_guide()
    
    # Analyse des fonctionnalités
    analyze_workflow_features()
    
    # Étapes suivantes
    provide_next_steps()
    
    # Résumé final
    print(f"\n{'=' * 60}")
    print("📋 RÉSUMÉ DE VOTRE SITUATION")
    print("=" * 60)
    
    if not has_android_key:
        print("🔴 SITUATION ACTUELLE : Pas de clé de signature Android")
        print("❌ Problème Play Console : 'Tous les app bundles doivent être signés'")
        print("🎯 SOLUTION IMMÉDIATE : Exécuter 'python generate_signing_key.py'")
    else:
        print("🟢 SITUATION ACTUELLE : Clé de signature Android présente")
        print("✅ Prêt pour : Build AAB signé + Upload manuel")
        if has_google_play_api:
            print("🌟 BONUS : API Google Play détectée → Publication automatique possible")
        else:
            print("🚀 BONUS POSSIBLE : Configurer API Google Play pour publication auto")
    
    print(f"\n{'🎯' * 20}")
    print("PRIORITÉ #1 : Clé de signature Android → Résout le problème immédiatement !")
    print("PRIORITÉ #2 : Tester avec un build → Valider la solution")
    print("PRIORITÉ #3 : API Google Play → Automatiser la publication (optionnel)")

if __name__ == "__main__":
    main()
