#!/usr/bin/env python3
"""
Script pour configurer buildozer.spec pour GitHub Actions
"""
import re
import os

def update_buildozer_spec():
    """Met à jour buildozer.spec avec les bonnes configurations"""
    
    if not os.path.exists('buildozer.spec'):
        print("❌ buildozer.spec not found!")
        return False
    
    # Lire le fichier
    with open('buildozer.spec', 'r') as f:
        content = f.read()
    
    # Modifications nécessaires pour GitHub Actions
    modifications = [
        # Chemins SDK/NDK
        (r'#android\.sdk_path = .*', 'android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk'),
        (r'#android\.ndk_path = .*', 'android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk'),
        
        # Versions Android
        (r'android\.api = \d+', 'android.api = 33'),
        (r'android\.minapi = \d+', 'android.minapi = 21'),
        (r'android\.ndk = .*', 'android.ndk = 25b'),
        (r'android\.sdk = \d+', 'android.sdk = 33'),
        
        # Acceptance des licences
        (r'# android\.accept_sdk_license = False', 'android.accept_sdk_license = True'),
        (r'android\.accept_sdk_license = False', 'android.accept_sdk_license = True')
    ]
    
    # Appliquer les modifications
    for pattern, replacement in modifications:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            print(f"✅ Applied: {replacement}")
    
    # Sauvegarder
    with open('buildozer.spec', 'w') as f:
        f.write(content)
    
    print("✅ buildozer.spec updated successfully")
    return True

if __name__ == "__main__":
    success = update_buildozer_spec()
    exit(0 if success else 1)
