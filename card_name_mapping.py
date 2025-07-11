# Mapping des noms français vers anglais
FRENCH_TO_ENGLISH = {
    "Le Mat": "The Fool",
    "Le Bateleur": "The Magician", 
    "La Papesse": "The High Priestess",
    "L'Impératrice": "The Empress",
    "L'Empereur": "The Emperor",
    "Le Pape": "The Hierophant",
    "L'Amoureux": "The Lovers",
    "Le Chariot": "The Chariot",
    "La Justice": "Justice",
    "L'Hermite": "The Hermit",
    "La Roue de Fortune": "Wheel of Fortune",
    "La Force": "Strength",
    "Le Pendu": "The Hanged Man",
    "La Mort": "Death",
    "Tempérance": "Temperance",
    "Le Diable": "The Devil",
    "La Maison Dieu": "The Tower",
    "L'Étoile": "The Star",
    "La Lune": "The Moon",
    "Le Soleil": "The Sun",
    "Le Jugement": "Judgement",
    "Le Monde": "The World",
    # Ajoutez les cartes mineures si nécessaire
    "Valet de Bâton": "Page of Wands",
    "Roi de Denier": "King of Pentacles",
    "Reine de Denier": "Queen of Pentacles",
    "Cavalier de Denier": "Knight of Pentacles",
    "Valet de Denier": "Page of Pentacles",
    "Valet de Coupe": "Page of Cups",
    "Roi d'Épée": "King of Swords",
    "Reine d'Épée": "Queen of Swords",
    "Cavalier d'Épée": "Knight of Swords",
    "Valet d'Épée": "Page of Swords",
    "Roi de Coupe": "King of Cups",
    "Reine de Coupe": "Queen of Cups",
    "Cavalier de Coupe": "Knight of Cups",
    "Roi de Bâton": "King of Wands",
    "Reine de Bâton": "Queen of Wands",
    "Cavalier de Bâton": "Knight of Wands"
}

def get_card_name_for_lang(french_name, target_lang):
    """Retourne le nom de la carte dans la langue cible"""
    if target_lang == "en":
        return FRENCH_TO_ENGLISH.get(french_name, french_name)
    return french_name