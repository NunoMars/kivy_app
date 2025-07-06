#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour renommer les fichiers d'images avec accents vers des noms sans accents
compatibles Android.
"""

import os
import shutil
from pathlib import Path

def normalize_filename(filename):
    """
    Normalise un nom de fichier en supprimant les accents et caractères spéciaux
    """
    # Supprimer l'extension
    name, ext = os.path.splitext(filename)
    
    # Remplacer les caractères spéciaux courants
    replacements = {
        'É': 'E',
        'È': 'E', 
        'Ê': 'E',
        'Ë': 'E',
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        'ë': 'e',
        'À': 'A',
        'Á': 'A',
        'Â': 'A',
        'Ä': 'A',
        'à': 'a',
        'á': 'a',
        'â': 'a',
        'ä': 'a',
        'Ù': 'U',
        'Ú': 'U',
        'Û': 'U',
        'Ü': 'U',
        'ù': 'u',
        'ú': 'u',
        'û': 'u',
        'ü': 'u',
        'Ç': 'C',
        'ç': 'c',
        ''': "'",  # Apostrophe courbe vers droite
        ''': "'",  # Apostrophe courbe vers gauche
        '"': '"',  # Guillemets courbes
    }
    
    # Appliquer les remplacements
    normalized = name
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized + ext

def main():
    print("=== Normalisation des noms de fichiers d'images ===")
    
    # Répertoire des images
    image_dir = Path("tarot_img/MajorArcanaCards")
    if not image_dir.exists():
        print(f"❌ Répertoire d'images non trouvé: {image_dir}")
        return 1
    
    # Créer un répertoire de sauvegarde
    backup_dir = Path("tarot_img/MajorArcanaCards_backup")
    if not backup_dir.exists():
        print("📁 Création du répertoire de sauvegarde...")
        shutil.copytree(image_dir, backup_dir)
        print(f"✅ Sauvegarde créée dans: {backup_dir}")
    
    # Lister tous les fichiers .jpg
    jpg_files = list(image_dir.glob("*.jpg"))
    print(f"✅ Trouvé {len(jpg_files)} fichiers .jpg")
    
    # Analyser les fichiers à renommer
    files_to_rename = []
    for file_path in jpg_files:
        normalized_name = normalize_filename(file_path.name)
        if normalized_name != file_path.name:
            files_to_rename.append((file_path, normalized_name))
    
    if not files_to_rename:
        print("✅ Aucun fichier à renommer (tous les noms sont déjà compatibles)")
        return 0
    
    print(f"\n📋 {len(files_to_rename)} fichiers à renommer:")
    
    # Mapping pour mettre à jour signification.py
    name_mapping = {}
    
    for old_path, new_name in files_to_rename:
        new_path = old_path.parent / new_name
        
        print(f"  '{old_path.name}' -> '{new_name}'")
        
        # Extraire le nom de la carte (sans .jpg et sans " a l'envers")
        old_card_name = old_path.stem
        new_card_name = Path(new_name).stem
        
        if old_card_name.endswith(" a l'envers"):
            old_card_name = old_card_name.replace(" a l'envers", "")
            new_card_name = new_card_name.replace(" a l'envers", "")
        
        name_mapping[old_card_name] = new_card_name
        
        # Renommer le fichier
        try:
            old_path.rename(new_path)
            print("    ✅ Renommé avec succès")
        except Exception as e:
            print(f"    ❌ Erreur lors du renommage: {e}")
    
    # Créer un fichier de mapping pour mettre à jour signification.py
    mapping_file = Path("card_name_mapping.py")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write("# Mapping des anciens noms vers les nouveaux noms (sans accents)\n")
        f.write("CARD_NAME_MAPPING = {\n")
        for old_name, new_name in name_mapping.items():
            f.write(f"    '{old_name}': '{new_name}',\n")
        f.write("}\n")
    
    print(f"\n✅ Mapping sauvegardé dans: {mapping_file}")
    print(f"📝 Vous devez maintenant mettre à jour signification.py avec ces nouveaux noms")
    
    # Afficher les changements les plus importants
    print(f"\n🔍 Principaux changements:")
    for old_name, new_name in name_mapping.items():
        if old_name != new_name:
            print(f"  '{old_name}' -> '{new_name}'")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
