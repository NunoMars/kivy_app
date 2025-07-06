#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapping des noms de cartes avec accents vers les noms de fichiers sans accents.
Ce fichier permet de garder les beaux noms avec accents pour l'affichage
tout en utilisant des noms de fichiers compatibles Android.
"""

def normalize_card_name_for_file(card_name):
    """
    Convertit un nom de carte avec accents vers un nom de fichier sans accents
    compatible avec Android.
    
    Args:
        card_name (str): Nom de la carte avec accents (ex: "Le Cavalier D'Épée")
    
    Returns:
        str: Nom normalisé sans accents (ex: "Le Cavalier D'Epee")
    """
    # Remplacements des caractères accentués
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
        'Ô': 'O',
        'ô': 'o',
        'Î': 'I',
        'î': 'i',
        ''': "'",  # Apostrophe courbe vers droite
        ''': "'",  # Apostrophe courbe vers gauche
        '"': '"',  # Guillemets courbes ouvrants
        '"': '"',  # Guillemets courbes fermants
    }
    
    normalized = card_name
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized

def get_image_path(card_name, state="normal"):
    """
    Construit le chemin vers l'image d'une carte en gérant automatiquement
    la normalisation du nom pour la compatibilité Android.
    
    Args:
        card_name (str): Nom de la carte avec accents
        state (str): "normal" ou "a l'envers"
    
    Returns:
        str: Chemin vers le fichier image
    """
    # Normaliser le nom pour le fichier
    normalized_name = normalize_card_name_for_file(card_name)
    
    if state == "a l'envers":
        image_file_name = f"{normalized_name} {state}.jpg"
    else:
        image_file_name = f"{normalized_name}.jpg"
    
    return f"tarot_img/MajorArcanaCards/{image_file_name}"

# Mapping explicite pour les cas spéciaux (si nécessaire)
SPECIAL_CARD_MAPPINGS = {
    # Si certaines cartes ont des cas particuliers, les ajouter ici
    # "Nom Original": "nom_fichier_special",
}

def get_card_image_path(card_name, state="normal"):
    """
    Version publique de get_image_path avec gestion des cas spéciaux.
    
    Args:
        card_name (str): Nom de la carte avec accents
        state (str): "normal" ou "a l'envers"
    
    Returns:
        str: Chemin vers le fichier image
    """
    # Vérifier s'il y a un mapping spécial
    if card_name in SPECIAL_CARD_MAPPINGS:
        mapped_name = SPECIAL_CARD_MAPPINGS[card_name]
        if state == "a l'envers":
            image_file_name = f"{mapped_name} {state}.jpg"
        else:
            image_file_name = f"{mapped_name}.jpg"
        return f"tarot_img/MajorArcanaCards/{image_file_name}"
    
    # Utiliser la normalisation automatique
    return get_image_path(card_name, state)

# Test des mappings les plus problématiques
if __name__ == "__main__":
    test_cards = [
        "Le Cavalier D'Épée",
        "La Reine D'Épée", 
        "Le Roi D'Épée",
        "Le Valet D'Épée",
        "L'Étoile",
        "L'Empereur",
        "L'Impératrice"
    ]
    
    print("=== Test des mappings de noms ===")
    for card in test_cards:
        normal_path = get_card_image_path(card)
        reverse_path = get_card_image_path(card, "a l'envers")
        
        print(f"\nCarte: '{card}'")
        print(f"  Normal: {normal_path}")
        print(f"  Inversé: {reverse_path}")
        
        # Vérifier si les fichiers existent
        from pathlib import Path
        normal_exists = Path(normal_path).exists()
        reverse_exists = Path(reverse_path).exists()
        print(f"  Statut: Normal {'✅' if normal_exists else '❌'} | Inversé {'✅' if reverse_exists else '❌'}")
