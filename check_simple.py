#!/usr/bin/env python3
"""
Script de verification simplifie sans emojis pour Windows
"""
import os
import subprocess

def check_file_exists(filepath, description):
    """Verifie qu'un fichier existe"""
    if os.path.exists(filepath):
        print(f"OK {description}: {filepath}")
        return True
    else:
        print(f"MANQUANT {description}: {filepath}")
        return False

def main():
    print("VERIFICATION FINALE AVANT BUILD")
    print("=" * 50)
    
    # Verification des fichiers
    print("\nFICHIERS REQUIS")
    print("-" * 20)
    files_ok = all([
        check_file_exists('main.py', 'Application principale'),
        check_file_exists('macartedetarotapp.kv', 'Interface Kivy'),
        check_file_exists('tarot_img/icon.png', 'Icone PNG'),
        check_file_exists('buildozer.spec', 'Configuration buildozer'),
        check_file_exists('.github/workflows/publish-android.yml', 'Workflow GitHub'),
        check_file_exists('googleplay.keystore', 'Cle de signature'),
        check_file_exists('google-play-service-account.json', 'Cle de service Google Play'),
    ])
    
    # Verification buildozer.spec
    print("\nCONFIGURATION BUILDOZER")
    print("-" * 25)
    if os.path.exists('buildozer.spec'):
        with open('buildozer.spec', 'r', encoding='utf-8') as f:
            content = f.read()
        
        buildozer_ok = True
        if 'android.api = 34' in content:
            print("OK API 34")
        else:
            print("ERREUR API 34")
            buildozer_ok = False
            
        if 'android.release_artifact = aab' in content:
            print("OK Format AAB")
        else:
            print("ERREUR Format AAB")
            buildozer_ok = False
            
        if 'android.enable_androidx = True' in content:
            print("OK AndroidX")
        else:
            print("ERREUR AndroidX")
            buildozer_ok = False
    else:
        buildozer_ok = False
    
    # Verification Git
    print("\nREPOSITORY GIT")
    print("-" * 15)
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("OK Repository Git")
            
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                print(f"OK Remote: {remote_url}")
                git_ok = True
            else:
                print("ERREUR Pas de remote origin")
                git_ok = False
        else:
            print("ERREUR Pas un repository Git")
            git_ok = False
    except Exception:
        print("ERREUR Git non installe")
        git_ok = False
    
    # Resultat final
    print("\n" + "=" * 50)
    all_ok = files_ok and buildozer_ok and git_ok
    
    if all_ok:
        print("TOUS LES TESTS PASSENT !")
        print("\nPROCHAINES ETAPES:")
        print("1. Configurez les secrets GitHub")
        print("2. Lancez: python trigger_build.py v1.0.1")
        print("3. Surveillez le build sur GitHub Actions")
    else:
        print("CERTAINS TESTS ONT ECHOUE")
        print("Corrigez les erreurs ci-dessus")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
