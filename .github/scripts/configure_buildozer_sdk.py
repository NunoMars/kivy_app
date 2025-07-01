#!/usr/bin/env python3
"""
Script pour configurer buildozer.spec et forcer l'utilisation 
des SDK/NDK Android préinstallés sur GitHub Actions.
"""
import os
import re


def update_buildozer_config():
    """Met à jour buildozer.spec pour utiliser les SDK/NDK système"""
    config_file = "buildozer.spec"
    
    # Lire le contenu actuel
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Variables d'environnement GitHub Actions
    android_home = os.environ.get('ANDROID_HOME', '/usr/local/lib/android/sdk')
    android_ndk = os.environ.get('ANDROID_NDK_HOME', '/usr/local/lib/android/sdk/ndk/25.2.9519653')
    
    print("🔧 Configuration buildozer avec :")
    print(f"   ANDROID_HOME: {android_home}")
    print(f"   ANDROID_NDK: {android_ndk}")
    
    # Modifications à appliquer
    modifications = [
        # Forcer les chemins SDK/NDK pour éviter le téléchargement
        (r'#android\.sdk_path.*', f'android.sdk_path = {android_home}'),
        (r'#android\.ndk_path.*', f'android.ndk_path = {android_ndk}'),
        
        # S'assurer que skip_update est False pour utiliser les SDK préinstallés
        (r'android\.skip_update = .*', 'android.skip_update = False'),
        
        # Accepter automatiquement les licences
        (r'android\.accept_sdk_license = .*', 'android.accept_sdk_license = True'),
        
        # Utiliser la version NDK 25c (compatible SDL2)
        (r'android\.ndk = .*', 'android.ndk = 25c'),
        
        # Supprimer Pillow des requirements s'il existe
        (r'requirements = ([^,]*),?pillow[^,]*,?([^,]*)', r'requirements = \1,\2'),
        (r'requirements = pillow,?(.*)', r'requirements = \1'),
        (r'requirements = (.*),pillow', r'requirements = \1'),
        
        # Configurer les artefacts correctement (APK debug, AAB release)
        (r'android\.debug_artifact = .*', 'android.debug_artifact = apk'),
        (r'android\.release_artifact = .*', 'android.release_artifact = aab'),
        
        # Nettoyer les virgules doubles
        (r'requirements = ([^,]+),,+([^,]+)', r'requirements = \1,\2'),
        (r'requirements = ,+(.+)', r'requirements = \1'),
        (r'requirements = (.+),+$', r'requirements = \1'),
    ]
    
    # Appliquer les modifications
    original_content = content
    for pattern, replacement in modifications:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Ajouter les chemins SDK/NDK s'ils n'existent pas
    if 'android.sdk_path' not in content:
        # Trouver la section [app] et ajouter après android.accept_sdk_license
        sdk_line = f"\n# (str) Android SDK directory - forced for GitHub Actions\nandroid.sdk_path = {android_home}\n"
        content = re.sub(
            r'(android\.accept_sdk_license = True\n)',
            r'\1' + sdk_line,
            content
        )
    
    if 'android.ndk_path' not in content:
        # Ajouter après android.sdk_path
        ndk_line = f"\n# (str) Android NDK directory - forced for GitHub Actions\nandroid.ndk_path = {android_ndk}\n"
        content = re.sub(
            r'(android\.sdk_path = .*\n)',
            r'\1' + ndk_line,
            content
        )
    
    # Vérifier si nous avons fait des changements
    if content != original_content:
        # Sauvegarder le fichier modifié
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ buildozer.spec mis à jour avec les chemins SDK/NDK système")
    else:
        print("ℹ️  buildozer.spec déjà configuré correctement")
    
    # Afficher la configuration finale
    print("\n📋 Configuration finale :")
    with open(config_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if any(keyword in line for keyword in ['requirements =', 'android.sdk_path', 'android.ndk_path', 'android.ndk =', 'android.api']):
                print(f"   {line_num:3d}: {line.strip()}")


def clean_buildozer_cache():
    """Nettoie le cache buildozer pour forcer l'utilisation des nouveaux SDK"""
    cache_dirs = ['.buildozer', os.path.expanduser('~/.buildozer')]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"🧹 Nettoyage du cache buildozer : {cache_dir}")
            os.system(f"rm -rf {cache_dir}")
        else:
            print(f"ℹ️  Cache buildozer non trouvé : {cache_dir}")


if __name__ == '__main__':
    print("🔧 Configuration buildozer pour GitHub Actions...")
    update_buildozer_config()
    clean_buildozer_cache()
    print("✅ Configuration terminée")
