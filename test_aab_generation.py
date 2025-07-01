#!/usr/bin/env python3
"""
Script de test pour vérifier la génération d'AAB avec buildozer.
Simule le processus du workflow GitHub Actions.
"""
import os
import subprocess
import sys
import tempfile


def run_command(cmd, cwd=None, timeout=300):
    """Exécute une commande avec gestion d'erreur"""
    try:
        print(f"🔧 Exécution: {cmd}")
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, 
            capture_output=True, text=True, timeout=timeout
        )
        
        if result.stdout:
            print(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"📥 STDERR:\n{result.stderr}")
            
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout après {timeout}s")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False, "", str(e)


def test_aab_generation():
    """Test de génération d'AAB avec buildozer"""
    
    print("🎯 Test de génération AAB avec buildozer")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("buildozer.spec"):
        print("❌ buildozer.spec non trouvé")
        print("   Assurez-vous d'être dans le répertoire du projet Kivy")
        return False
    
    print("✅ buildozer.spec trouvé")
    
    # Vérifier buildozer
    success, stdout, stderr = run_command("buildozer --version")
    if not success:
        print("❌ buildozer non installé ou non fonctionnel")
        print("   Installez buildozer: pip install buildozer")
        return False
    
    print(f"✅ buildozer version: {stdout.strip()}")
    
    # Vérifier Java
    success, stdout, stderr = run_command("java -version")
    if not success:
        print("❌ Java non installé")
        return False
    
    print("✅ Java détecté")
    
    # Générer une clé de signature temporaire
    print("\n🔑 Génération clé de signature temporaire...")
    keystore_cmd = (
        "keytool -genkey -v -keystore test.keystore -alias testkey "
        "-keyalg RSA -keysize 2048 -validity 365 "
        "-dname 'CN=Test, OU=Test, O=Test, L=Test, S=Test, C=FR' "
        "-storepass testpass -keypass testpass"
    )
    
    success, stdout, stderr = run_command(keystore_cmd)
    if not success:
        print("❌ Impossible de créer la clé de signature")
        return False
    
    print("✅ Clé de signature temporaire créée: test.keystore")
    
    # Sauvegarder buildozer.spec original
    if os.path.exists("buildozer.spec.backup"):
        os.remove("buildozer.spec.backup")
    
    import shutil
    shutil.copy("buildozer.spec", "buildozer.spec.backup")
    print("💾 buildozer.spec sauvegardé")
    
    try:
        # Modifier buildozer.spec pour la signature
        print("\n⚙️  Configuration buildozer pour AAB...")
        with open("buildozer.spec", "a") as f:
            f.write("\n")
            f.write("# Configuration test AAB\n")
            f.write("android.release_keystore = test.keystore\n")
            f.write("android.release_keystore_passwd = testpass\n")
            f.write("android.release_key = testkey\n")
            f.write("android.release_key_passwd = testpass\n")
        
        print("✅ buildozer.spec configuré pour signature")
        
        # Nettoyer les builds précédents
        print("\n🧹 Nettoyage des builds précédents...")
        if os.path.exists(".buildozer"):
            run_command("rm -rf .buildozer")
        if os.path.exists("bin"):
            run_command("rm -rf bin")
        
        # Lancer le build AAB
        print("\n🏗️  Lancement build AAB avec 'buildozer android release'...")
        print("   (Ceci peut prendre plusieurs minutes...)")
        
        success, stdout, stderr = run_command(
            "buildozer android release --verbose", 
            timeout=1800  # 30 minutes
        )
        
        if success:
            print("✅ Build AAB réussi!")
            
            # Vérifier les fichiers générés
            if os.path.exists("bin"):
                print("\n📁 Fichiers générés dans bin/:")
                files = os.listdir("bin")
                for file in files:
                    print(f"   📱 {file}")
                    if file.endswith(".aab"):
                        print(f"   🎯 AAB trouvé: {file}")
                        return True
                
                print("⚠️  Aucun fichier .aab trouvé dans bin/")
                return False
            else:
                print("❌ Répertoire bin/ non créé")
                return False
        else:
            print("❌ Build AAB échoué")
            return False
            
    finally:
        # Restaurer buildozer.spec original
        if os.path.exists("buildozer.spec.backup"):
            shutil.move("buildozer.spec.backup", "buildozer.spec")
            print("🔄 buildozer.spec restauré")
        
        # Nettoyer les fichiers temporaires
        if os.path.exists("test.keystore"):
            os.remove("test.keystore")
            print("🧹 Clé temporaire supprimée")


def main():
    """Point d'entrée principal"""
    print("🔧 Test de génération AAB pour Kivy")
    print("=" * 60)
    
    success = test_aab_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test réussi: AAB généré avec succès!")
        print("   Le workflow GitHub Actions devrait maintenant fonctionner")
        return 0
    else:
        print("❌ Test échoué: Impossible de générer AAB")
        print("   Vérifiez la configuration buildozer et les dépendances")
        return 1


if __name__ == '__main__':
    sys.exit(main())
