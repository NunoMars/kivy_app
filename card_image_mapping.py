#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapping des noms de cartes avec accents vers les noms de fichiers sans accents.
Ce fichier permet de garder les beaux noms avec accents pour l'affichage
tout en utilisant des noms de fichiers compatibles Android.
"""

import os
import unicodedata

# Mapping pour convertir TOUS les noms de cartes vers les VRAIS noms de fichiers
SPECIAL_CARD_MAPPINGS = {
    # Mappings anglais vers français (noms EXACTS des fichiers)
    "The Fool": "Le Mat",
    "The Magician": "Le Bateleur", 
    "The High Priestess": "La Papesse",
    "The Empress": "L'Imperatrice",
    "The Emperor": "L'Empereur",
    "The Hierophant": "Le Pape",
    "The Lovers": "L'Amoureux",
    "The Chariot": "Le Chariot",
    "Justice": "La Justice",
    "The Hermit": "L'Hermite",
    "Wheel of Fortune": "La Roue de La Fortune",
    "Strength": "La Force",
    "The Hanged Man": "Le Pendu",
    "Death": "La Mort",
    "Temperance": "La Temperance",
    "The Devil": "Le Diable",
    "The Tower": "La Maison Dieu",
    "The Star": "L'Etoile",
    "The Moon": "La Lune",
    "The Sun": "Le Soleil",
    "Judgement": "Le Jugement",
    "The World": "Le Monde",
    
    # Mappings portugais vers français (CORRIGER)
    "O Louco": "Le Mat",
    "O Mago": "Le Bateleur",
    "A Papisa": "La Papesse",
    "A Imperatriz": "L'Imperatrice",  # Pas "L Imperatrice"
    "O Imperador": "L'Empereur",      # Pas "L Empereur"
    "O Papa": "Le Pape",
    "Os Amantes": "L'Amoureux",       # Pas "L Amoureux"
    "O Carro": "Le Chariot",
    "A Justiça": "La Justice",
    "O Eremita": "L'Hermite",         # Pas "L Hermite"
    "A Roda da Fortuna": "La Roue de La Fortune",  # Pas "La Roue de Fortune"
    "A Força": "La Force",
    "O Enforcado": "Le Pendu",
    "A Morte": "La Mort",
    "A Temperança": "La Temperance",  # Pas "Temperance"
    "O Diabo": "Le Diable",
    "A Torre": "La Maison Dieu",
    "A Estrela": "L'Etoile",          # Pas "L Etoile"
    "A Lua": "La Lune",
    "O Sol": "Le Soleil",
    "O Julgamento": "Le Jugement",
    "O Mundo": "Le Monde",
    
    # Cartes mineures anglaises vers français (noms EXACTS des fichiers)
    "Page of Wands": "Le Valet de Baton",
    "Knight of Wands": "Le Cavalier de Baton",
    "Queen of Wands": "La Reine de Baton",
    "King of Wands": "Le Roi De Baton",
    
    "Page of Cups": "Le Valet De Coupe",
    "Knight of Cups": "Le Cavalier De Coupe",
    "Queen of Cups": "La Reine De Coupe",
    "King of Cups": "Le Roi de Coupe",
    
    "Page of Swords": "Le Valet D'Epee",
    "Knight of Swords": "Le Cavalier D'Epee",
    "Queen of Swords": "La Reine D'Epee",
    "King of Swords": "Le Roi D'Epee",
    
    "Page of Pentacles": "Le Valet De Deniers",
    "Knight of Pentacles": "Le Cavalier de Deniers",
    "Queen of Pentacles": "La Reine De Deniers",
    "King of Pentacles": "Le Roi De Deniers",
    
    # Noms français corrigés pour correspondre EXACTEMENT aux fichiers
    "L'Impératrice": "L'Imperatrice",
    "L'Empereur": "L'Empereur", 
    "L'Amoureux": "L'Amoureux",
    "L'Hermite": "L'Hermite",
    "La Roue de Fortune": "La Roue de La Fortune",  # IMPORTANT: "La" pas "la"
    "Tempérance": "La Temperance",  # IMPORTANT: Ajouter "La"
    "L'Étoile": "L'Etoile",
}

def remove_accents(input_str):
    """Supprime les accents d'une chaîne"""
    nfkd_form = unicodedata.normalize('NFD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def get_card_image_path(card_name, state="droite"):
    """
    Retourne le chemin complet vers l'image de la carte
    Utilise les VRAIS noms de fichiers avec apostrophes et espaces exacts
    
    Args:
        card_name: Nom de la carte (dans n'importe quelle langue)
        state: État de la carte
    
    Returns:
        str: Chemin complet vers l'image française
    """
    base_path = "tarot_img/MajorArcanaCards"
    
    # Convertir vers le nom français correspondant
    if card_name in SPECIAL_CARD_MAPPINGS:
        french_file_name = SPECIAL_CARD_MAPPINGS[card_name]
    else:
        # Fallback : utiliser le nom tel quel
        french_file_name = card_name
    
    candidates = []

    def _normalized_names(name: str):
        seen = set()
        for variant in (name, remove_accents(name)):
            cleaned = variant.strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                yield cleaned

    reversed_suffixes = [" a l'envers.jpg", ".jpg"]
    normal_suffixes = [".jpg"]

    suffixes = reversed_suffixes if state in ["a l'envers", "invertida", "reversed", "umgekehrt", "rovesciata"] else normal_suffixes

    for candidate_name in _normalized_names(french_file_name):
        for suffix in suffixes:
            path_candidate = os.path.join(base_path, f"{candidate_name}{suffix}")
            candidates.append(path_candidate)
            if os.path.exists(path_candidate):
                return path_candidate

    # Fallback ultime vers le dos de carte
    return os.path.join("tarot_img", "Back.jpg")

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
