#!/usr/bin/env python3
"""
Script pour nettoyer les doublons dans buildozer.spec
"""

def clean_buildozer_spec():
    """Nettoie les doublons dans buildozer.spec"""
    
    print("🧹 Nettoyage des doublons dans buildozer.spec...")
    
    # Lire le fichier
    with open('buildozer.spec', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Supprimer les doublons de configuration de signature
    seen_configs = set()
    clean_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Identifier les lignes de configuration de signature
        if any(key in stripped for key in [
            'android.release_keystore =',
            'android.release_keystore_passwd =', 
            'android.release_key =',
            'android.release_key_passwd ='
        ]):
            # Extraire la clé de configuration
            if '=' in stripped:
                config_key = stripped.split('=')[0].strip()
                
                if config_key in seen_configs:
                    print(f"⚠️  Doublon détecté et supprimé: {config_key}")
                    continue  # Ignorer cette ligne (doublon)
                else:
                    seen_configs.add(config_key)
                    clean_lines.append(line)
            else:
                clean_lines.append(line)
        else:
            clean_lines.append(line)
    
    # Réécrire le fichier
    with open('buildozer.spec', 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✅ Nettoyage terminé. {len(lines) - len(clean_lines)} doublons supprimés.")
    
    # Vérifier qu'il n'y a plus de doublons
    config_counts = {}
    with open('buildozer.spec', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if any(key in stripped for key in [
                'android.release_keystore =',
                'android.release_keystore_passwd =', 
                'android.release_key =',
                'android.release_key_passwd ='
            ]) and '=' in stripped:
                config_key = stripped.split('=')[0].strip()
                config_counts[config_key] = config_counts.get(config_key, 0) + 1
    
    duplicates_found = False
    for config, count in config_counts.items():
        if count > 1:
            print(f"❌ Encore des doublons: {config} ({count} fois)")
            duplicates_found = True
        else:
            print(f"✅ {config}")
    
    if not duplicates_found:
        print("✅ Aucun doublon restant dans buildozer.spec")
    
    return not duplicates_found

if __name__ == "__main__":
    success = clean_buildozer_spec()
    exit(0 if success else 1)
