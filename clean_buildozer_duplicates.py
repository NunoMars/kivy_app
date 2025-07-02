#!/usr/bin/env python3
"""
Script pour nettoyer les doublons dans buildozer.spec
"""
import os

def clean_buildozer_duplicates():
    """Supprime les lignes dupliquées dans buildozer.spec"""
    print("NETTOYAGE DES DOUBLONS BUILDOZER.SPEC")
    print("=" * 50)
    
    if not os.path.exists('buildozer.spec'):
        print("ERREUR: buildozer.spec non trouvé")
        return False
    
    # Lire le fichier
    with open('buildozer.spec', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Lignes originales: {len(lines)}")
    
    # Nettoyer les doublons tout en préservant l'ordre
    seen_lines = set()
    clean_lines = []
    duplicates_found = 0
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Ignorer les lignes vides et commentaires
        if not line_stripped or line_stripped.startswith('#'):
            clean_lines.append(line)
            continue
        
        # Vérifier les doublons pour les options de configuration
        if '=' in line_stripped:
            key = line_stripped.split('=')[0].strip()
            
            # Cas spécial pour la signature Android
            if key.startswith('android.release_'):
                if line_stripped in seen_lines:
                    print(f"DOUBLON SUPPRIME ligne {i}: {line_stripped}")
                    duplicates_found += 1
                    continue
                else:
                    seen_lines.add(line_stripped)
        
        clean_lines.append(line)
    
    print(f"Doublons supprimés: {duplicates_found}")
    print(f"Lignes finales: {len(clean_lines)}")
    
    # Sauvegarder le fichier nettoyé
    with open('buildozer.spec', 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print("✅ buildozer.spec nettoyé avec succès")
    return True

if __name__ == "__main__":
    clean_buildozer_duplicates()
