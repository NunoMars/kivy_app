#!/usr/bin/env python3
"""
Script de vérification finale avant déclenchement du build
"""
import os
import json
import subprocess

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filepath):
        print(f"OK {description}: {filepath}")
        return True
    else:
        print(f"MANQUANT {description}: {filepath}")
        return False

def check_buildozer_spec():
    """Vérifie la configuration buildozer.spec"""
    print("\nCONFIGURATION BUILDOZER.SPEC")
    print("-" * 40)
    
    if not os.path.exists('buildozer.spec'):
        print("❌ buildozer.spec manquant")
        return False
    
    with open('buildozer.spec', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('API 34', 'android.api = 34' in content),
        ('Format AAB', 'android.release_artifact = aab' in content),
        ('AndroidX', 'android.enable_androidx = True' in content),
        ('Clé signature', 'android.release_keystore = googleplay.keystore' in content),
        ('Alias clé', 'android.release_key = googleplay' in content),
    ]
    
    all_good = True
    for desc, check in checks:
        if check:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc}")
            all_good = False
    
    return all_good

def check_workflow():
    """Vérifie le workflow GitHub Actions"""
    print("\nWORKFLOW GITHUB ACTIONS")
    print("-" * 40)
    
    workflow_path = '.github/workflows/publish-android.yml'
    if not os.path.exists(workflow_path):
        print(f"❌ Workflow manquant: {workflow_path}")
        return False
    
    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('Trigger sur tags', 'tags:' in content),
        ('Java 17', 'openjdk-17-jdk' in content),
        ('API 34', 'ANDROID_API_LEVEL: "34"' in content or 'android.api = 34' in content),
        ('Secrets keystore', 'ANDROID_KEYSTORE' in content),
        ('Google Play upload', 'google-play-cli-py' in content or 'upload-google-play' in content),
    ]
    
    all_good = True
    for desc, check in checks:
        if check:
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc}")
            all_good = False
    
    return all_good

def check_keys():
    """Vérifie les clés et certificats"""
    print("\nCLES ET CERTIFICATS")
    print("-" * 40)
    
    # Clé de signature
    keystore_ok = check_file_exists('googleplay.keystore', 'Clé de signature Android')
    
    # Clé de service Google Play
    service_ok = check_file_exists('google-play-service-account.json', 'Clé de service Google Play')
    
    if service_ok:
        try:
            with open('google-play-service-account.json', 'r') as f:
                service_data = json.load(f)
                if 'client_email' in service_data and 'private_key' in service_data:
                    print("✅ Clé de service Google Play valide")
                else:
                    print("❌ Clé de service Google Play invalide")
                    service_ok = False
        except Exception as e:
            print(f"❌ Erreur lecture clé de service: {e}")
            service_ok = False
    
    return keystore_ok and service_ok

def check_git():
    """Vérifie l'état Git"""
    print("\nREPOSITORY GIT")
    print("-" * 40)
    
    try:
        # Vérifier qu'on est dans un repo git
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Pas un repository Git ou Git non installé")
            return False
        
        print("✅ Repository Git")
        
        # Vérifier la remote origin
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            print(f"✅ Remote origin: {remote_url}")
            if 'github.com' in remote_url:
                print("✅ Remote GitHub détectée")
            else:
                print("⚠️  Remote non-GitHub détectée")
        else:
            print("❌ Pas de remote origin configurée")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur Git: {e}")
        return False

def main():
    print("VERIFICATION FINALE AVANT BUILD")
    print("=" * 50)
    
    # Vérifications
    checks = [
        ("Fichiers requis", lambda: all([
            check_file_exists('main.py', 'Application principale'),
            check_file_exists('macartedetarotapp.kv', 'Interface Kivy'),
            check_file_exists('tarot_img/icon.png', 'Icône PNG'),
        ])),
        ("Configuration buildozer", check_buildozer_spec),
        ("Workflow GitHub", check_workflow),
        ("Clés et certificats", check_keys),
        ("Repository Git", check_git),
    ]
    
    all_passed = True
    results = []
    
    for desc, check_func in checks:
        try:
            result = check_func()
            results.append((desc, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Erreur lors de {desc}: {e}")
            results.append((desc, False))
            all_passed = False
    
    # Résumé
    print("\nRESUME DES VERIFICATIONS")
    print("-" * 40)
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {desc}")
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("TOUS LES TESTS PASSENT !")
        print()
        print("PROCHAINES ETAPES:")
        print("1. Mettez a jour les secrets GitHub avec:")
        print("   python update_github_secrets.py")
        print()
        print("2. Declenchez le build avec:")
        print("   python trigger_build.py v1.0.1")
        print()
        print("3. Surveillez le build sur GitHub Actions")
        print("4. Verifiez l'upload sur Google Play Console")
        
    else:
        print("CERTAINS TESTS ONT ECHOUE")
        print()
        print("ACTIONS REQUISES:")
        print("- Corrigez les erreurs ci-dessus")
        print("- Relancez ce script pour verifier")
        print("- Puis procedez au build")

if __name__ == "__main__":
    main()
