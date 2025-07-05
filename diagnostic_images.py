#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier la correspondance entre les noms de cartes 
dans signification.py et les fichiers d'images réels.
"""

import os
import unicodedata
from signification import cards_signification

def normalize_string(s):
    """Normalise une chaîne pour la comparaison"""
    # Normaliser les caractères Unicode
    normalized = unicodedata.normalize('NFD', s)
    # Afficher les caractères individuels avec leur code
    chars = []
    for char in normalized:
        chars.append(f"'{char}'(U+{ord(char):04X})")
    return normalized, chars

def check_file_exists(filepath):
    """Vérifie si un fichier existe avec différentes variantes"""
    if os.path.exists(filepath):
        return True, filepath
    
    # Essayer différentes normalizations
    variants = [
        filepath.replace("'", "'"),  # apostrophe droite vs courbe
        filepath.replace("'", "'"),  # apostrophe courbe vs droite
        filepath.replace("É", "E"),  # sans accent
        filepath.replace("è", "e"),  # sans accent
        filepath.replace("é", "e"),  # sans accent
        filepath.replace("à", "a"),  # sans accent
    ]
    
    for variant in variants:
        if os.path.exists(variant):
            return True, variant
    
    return False, None

def main():
    print("=== Diagnostic des images de cartes ===")
    
    # Récupérer toutes les cartes définies
    cards = cards_signification
    print(f"Nombre de cartes définies: {len(cards)}")
    
    # Répertoire des images
    img_dir = "tarot_img/MajorArcanaCards"
    
    if not os.path.exists(img_dir):
        print(f"❌ Répertoire d'images non trouvé: {img_dir}")
        return
    
    # Lister tous les fichiers d'images réels
    real_files = []
    for filename in os.listdir(img_dir):
        if filename.endswith('.jpg'):
            real_files.append(filename)
    
    print(f"Nombre de fichiers d'images trouvés: {len(real_files)}")
    
    # Vérifier chaque carte
    missing_files = []
    problematic_cards = []
    
    for card_name in cards.keys():
        print(f"\n--- Vérification: {card_name} ---")
        
        # Analyser les caractères du nom
        normalized_name, chars = normalize_string(card_name)
        print(f"Caractères: {' '.join(chars)}")
        
        # Tester les deux variantes (normale et à l'envers)
        for variant in ["", " a l'envers"]:
            test_name = card_name + variant
            expected_file = os.path.join(img_dir, f"{test_name}.jpg")
            
            exists, actual_file = check_file_exists(expected_file)
            
            if exists:
                print(f"✅ {test_name}.jpg -> {actual_file}")
            else:
                print(f"❌ {test_name}.jpg -> MANQUANT")
                missing_files.append(f"{test_name}.jpg")
                
                # Chercher des fichiers similaires
                similar = []
                for real_file in real_files:
                    if card_name.lower().replace(" ", "").replace("'", "") in real_file.lower().replace(" ", "").replace("'", ""):
                        similar.append(real_file)
                
                if similar:
                    print(f"   Fichiers similaires trouvés: {similar}")
                    problematic_cards.append((card_name, variant, similar))
    
    # Résumé
    print("=== RÉSUMÉ ===")
    print(f"Fichiers manquants: {len(missing_files)}")
    print(f"Cartes problématiques: {len(problematic_cards)}")
    
    if missing_files:
        print("\n❌ Fichiers manquants:")
        for file in missing_files:
            print(f"  - {file}")
    
    if problematic_cards:
        print("\n⚠️  Correspondances possibles:")
        for card, variant, similar in problematic_cards:
            print(f"  - {card}{variant} -> {similar}")
    
    # Vérifier spécifiquement "Le Cavalier D'Épée"
    print("\n=== FOCUS: Le Cavalier D'Épée ===")
    target_card = "Le Cavalier D'Épée"
    
    if target_card in cards:
        normalized, chars = normalize_string(target_card)
        print(f"Nom dans signification.py: {target_card}")
        print(f"Caractères détaillés: {' '.join(chars)}")
        
        # Chercher tous les fichiers qui contiennent "Cavalier" et "Épée"
        matching_files = []
        for filename in real_files:
            if "Cavalier" in filename and ("Épée" in filename or "Epee" in filename):
                matching_files.append(filename)
        
        print(f"Fichiers trouvés avec 'Cavalier' et 'Épée': {matching_files}")
        
        # Tester la construction du chemin comme dans main.py
        for state in ["", "a l'envers"]:
            if state:
                image_file_name = f"{target_card} {state}.jpg"
            else:
                image_file_name = f"{target_card}.jpg"
            
            image_path = os.path.join(img_dir, image_file_name)
            exists, actual = check_file_exists(image_path)
            
            print(f"Test chemin: {image_path}")
            print(f"Existe: {exists}, Chemin réel: {actual}")

if __name__ == "__main__":
    main()
