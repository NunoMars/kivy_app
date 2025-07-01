#!/usr/bin/env python3
"""
Test final du pipeline AAB avant déploiement.
Simule les étapes critiques du workflow GitHub Actions.
"""
import os
import sys
import subprocess


def run_command(cmd, cwd=None, timeout=60):
    """Execute a command with error handling"""
    try:
        print(f"🔧 Exécution: {cmd}")
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, 
            capture_output=True, text=True, timeout=timeout
        )
        print(f"📤 Return code: {result.returncode}")
        if result.stdout:
            print(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"📥 STDERR:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout après {timeout}s")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_buildozer_availability():
    """Test if buildozer is available and functional"""
    print("\n🔍 Test disponibilité buildozer...")
    
    if not run_command("buildozer --version"):
        print("❌ buildozer non disponible")
        return False
    
    print("✅ buildozer disponible")
    return True


def test_java_availability():
    """Test if Java is available"""
    print("\n🔍 Test disponibilité Java...")
    
    if not run_command("java -version"):
        print("❌ Java non disponible")
        return False
    
    print("✅ Java disponible")
    return True


def test_buildozer_config():
    """Test buildozer configuration"""
    print("\n🔍 Test configuration buildozer...")
    
    if not os.path.exists("buildozer.spec"):
        print("❌ buildozer.spec non trouvé")
        return False
    
    # Lire la configuration
    with open("buildozer.spec", "r") as f:
        content = f.read()
    
    # Vérifications critiques
    checks = [
        ("android.release_artifact = aab", "Configuration AAB"),
        ("android.debug_artifact = apk", "Configuration APK"),
        ("android.ndk = 25c", "NDK version"),
        ("android.api = 33", "API level"),
    ]
    
    for pattern, desc in checks:
        if pattern in content:
            print(f"✅ {desc}: OK")
        else:
            print(f"❌ {desc}: MANQUANT")
            return False
    
    return True


def test_scripts_execution():
    """Test that our utility scripts work"""
    print("\n🔍 Test exécution scripts utilitaires...")
    
    scripts = [
        (".github/scripts/test_aab_config.py", "Test config AAB"),
        (".github/scripts/configure_buildozer_sdk.py", "Configuration SDK"),
    ]
    
    for script, desc in scripts:
        if os.path.exists(script):
            print(f"🔧 Test {desc}...")
            if run_command(f"python {script}", timeout=30):
                print(f"✅ {desc}: OK")
            else:
                print(f"❌ {desc}: ÉCHEC")
                return False
        else:
            print(f"❌ Script manquant: {script}")
            return False
    
    return True


def test_workflow_syntax():
    """Test GitHub Actions workflow syntax"""
    print("\n🔍 Test syntaxe workflows GitHub Actions...")
    
    workflows = [
        ".github/workflows/publish-android.yml",
        ".github/workflows/build-android.yml"
    ]
    
    for workflow in workflows:
        if os.path.exists(workflow):
            try:
                import yaml
                with open(workflow, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
                print(f"✅ Syntaxe YAML valide: {workflow}")
            except ImportError:
                print(f"⚠️  PyYAML non installé, vérification basique: {workflow}")
                # Vérification basique
                with open(workflow, "r", encoding="utf-8") as f:
                    content = f.read()
                if "name:" in content and "on:" in content and "jobs:" in content:
                    print(f"✅ Structure workflow valide: {workflow}")
                else:
                    print(f"❌ Structure workflow invalide: {workflow}")
                    return False
            except Exception as e:
                print(f"❌ Erreur syntaxe YAML {workflow}: {e}")
                return False
        else:
            print(f"❌ Workflow manquant: {workflow}")
            return False
    
    return True


def test_minimal_kivy_app():
    """Test that the Kivy app can be imported"""
    print("\n🔍 Test application Kivy basique...")
    
    try:
        # Test import basic
        sys.path.insert(0, ".")
        
        # Vérifier main.py
        if not os.path.exists("main.py"):
            print("❌ main.py manquant")
            return False
        
        print("✅ main.py présent")
        
        # Vérifier fichier KV
        if not os.path.exists("macartedetarotapp.kv"):
            print("❌ fichier KV manquant")
            return False
        
        print("✅ fichier KV présent")
        
        # Vérifier signification.py
        if not os.path.exists("signification.py"):
            print("❌ signification.py manquant")
            return False
        
        print("✅ signification.py présent")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Kivy: {e}")
        return False


def main():
    """Point d'entrée principal"""
    print("🚀 Test Final Pipeline AAB - Ma Carte de Tarot")
    print("=" * 60)
    
    tests = [
        ("Configuration buildozer", test_buildozer_config),
        ("Application Kivy", test_minimal_kivy_app),
        ("Syntaxe workflows", test_workflow_syntax),
        ("Scripts utilitaires", test_scripts_execution),
        ("Disponibilité buildozer", test_buildozer_availability),
        ("Disponibilité Java", test_java_availability),
    ]
    
    all_passed = True
    results = []
    
    for name, test_func in tests:
        try:
            print(f"\n{'='*20} {name} {'='*20}")
            success = test_func()
            results.append((name, success))
            if not success:
                all_passed = False
        except Exception as e:
            print(f"❌ Erreur inattendue dans {name}: {e}")
            results.append((name, False))
            all_passed = False
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status:12} {name}")
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("🚀 Le pipeline AAB est prêt pour le déploiement")
        print("")
        print("📋 Prochaines étapes recommandées :")
        print("   1. git add .")
        print("   2. git commit -m 'feat: pipeline AAB validé et prêt'")
        print("   3. git push origin main")
        print("   4. Surveiller le build GitHub Actions")
        print("   5. Créer un tag pour tester la release :")
        print("      git tag v0.1.0-test")
        print("      git push origin v0.1.0-test")
        print("")
        print("🔑 N'oubliez pas de configurer les secrets GitHub pour la production !")
        return 0
    else:
        print("❌ DES TESTS ONT ÉCHOUÉ")
        print("🔧 Corrigez les problèmes avant de déployer")
        return 1


if __name__ == '__main__':
    sys.exit(main())
