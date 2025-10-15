#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regroupe la logique de `card_image_mapping.py` et `card_name_mapping.py` :
- SPECIAL_CARD_MAPPINGS (noms multi-lang -> nom fichier FR)
- get_card_image_path, get_french_card_name
- get_card_name_for_lang et mappings de noms (EN/PT/RU)

Ce module remplace les deux anciens pour simplifier les imports et
éviter la duplication.
"""

from __future__ import annotations
import os
import unicodedata

# --- Copie consolidée des mappings ---
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
    
    # --- Portugais (PT/PT-BR) vers français ---
    "O Louco": "Le Mat",
    "O Mago": "Le Bateleur",
    "A Papisa": "La Papesse",
    "A Imperatriz": "L'Imperatrice",
    "O Imperador": "L'Empereur",
    "O Papa": "Le Pape",
    "Os Amantes": "L'Amoureux",
    "O Carro": "Le Chariot",
    "A Justiça": "La Justice",
    "O Eremita": "L'Hermite",
    "A Roda da Fortuna": "La Roue de La Fortune",
    "A Força": "La Force",
    "O Enforcado": "Le Pendu",
    "A Morte": "La Mort",
    "A Temperança": "La Temperance",
    "O Diabo": "Le Diable",
    "A Torre": "La Maison Dieu",
    "A Estrela": "L'Etoile",
    "A Lua": "La Lune",
    "O Sol": "Le Soleil",
    "O Julgamento": "Le Jugement",
    "O Mundo": "Le Monde",

    # Mappings supplémentaires pour les noms portugais des figures (pentacles, coupes, épées, bâtons)
    "A Rainha de Ouros": "La Reine De Deniers",
    "O Rei de Ouros": "Le Roi De Deniers",
    "O Cavaleiro de Ouros": "Le Cavalier de Deniers",
    "O Valete de Ouros": "Le Valet De Deniers",

    "A Rainha de Copas": "La Reine De Coupe",
    "O Rei de Copas": "Le Roi de Coupe",
    "O Cavaleiro de Copas": "Le Cavalier De Coupe",
    "O Valete de Copas": "Le Valet De Coupe",

    "A Rainha de Espadas": "La Reine D'Epee",
    "O Rei de Espadas": "Le Roi D'Epee",
    "O Cavaleiro de Espadas": "Le Cavalier D'Epee",
    "O Valete de Espadas": "Le Valet D'Epee",

    "A Rainha de Paus": "La Reine de Baton",
    "O Rei de Paus": "Le Roi De Baton",
    "O Cavaleiro de Paus": "Le Cavalier de Baton",
    "O Valete de Paus": "Le Valet de Baton",
    
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
    "La Roue de Fortune": "La Roue de La Fortune",
    "Tempérance": "La Temperance",
    "L'Étoile": "L'Etoile",

    # --- Anglais (EN) vers français ---
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

    # Figures (EN)
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
    
    # --- Espagnol (ES) vers français ---
    "El Loco": "Le Mat",
    "El Mago": "Le Bateleur",
    "La Sacerdotisa": "La Papesse",
    "La Emperatriz": "L'Imperatrice",
    "El Emperador": "L'Empereur",
    "El Papa": "Le Pape",
    "Los Enamorados": "L'Amoureux",
    "El Carro": "Le Chariot",
    "La Justicia": "La Justice",
    "El Ermitaño": "L'Hermite",
    "La Rueda de la Fortuna": "La Roue de La Fortune",
    "La Fuerza": "La Force",
    "El Colgado": "Le Pendu",
    "La Muerte": "La Mort",
    "La Templanza": "La Temperance",
    "El Diablo": "Le Diable",
    "La Torre": "La Maison Dieu",
    "La Estrella": "L'Etoile",
    "La Luna": "La Lune",
    "El Sol": "Le Soleil",
    "El Juicio": "Le Jugement",
    "El Mundo": "Le Monde",

    # Figures (ES)
    "Sota de Bastos": "Le Valet de Baton",
    "Caballero de Bastos": "Le Cavalier de Baton",
    "Reina de Bastos": "La Reine de Baton",
    "Rey de Bastos": "Le Roi De Baton",
    "Sota de Copas": "Le Valet De Coupe",
    "Caballero de Copas": "Le Cavalier De Coupe",
    "Reina de Copas": "La Reine De Coupe",
    "Rey de Copas": "Le Roi de Coupe",
    "Sota de Espadas": "Le Valet D'Epee",
    "Caballero de Espadas": "Le Cavalier D'Epee",
    "Reina de Espadas": "La Reine D'Epee",
    "Rey de Espadas": "Le Roi D'Epee",
    "Sota de Oros": "Le Valet De Deniers",
    "Caballero de Oros": "Le Cavalier de Deniers",
    "Reina de Oros": "La Reine De Deniers",
    "Rey de Oros": "Le Roi De Deniers",

    # --- Allemand (DE) vers français ---
    "Der Narr": "Le Mat",
    "Der Magier": "Le Bateleur",
    "Die Hohepriesterin": "La Papesse",
    "Die Kaiserin": "L'Imperatrice",
    "Der Kaiser": "L'Empereur",
    "Der Hierophant": "Le Pape",
    "Die Liebenden": "L'Amoureux",
    "Der Wagen": "Le Chariot",
    "Die Gerechtigkeit": "La Justice",
    "Der Einsiedler": "L'Hermite",
    "Das Rad des Schicksals": "La Roue de La Fortune",
    "Die Kraft": "La Force",
    "Der Gehängte": "Le Pendu",
    "Der Tod": "La Mort",
    "Die Mäßigkeit": "La Temperance",
    "Der Teufel": "Le Diable",
    "Der Turm": "La Maison Dieu",
    "Die Sterne": "L'Etoile",
    "Der Mond": "La Lune",
    "Die Sonne": "Le Soleil",
    "Das Gericht": "Le Jugement",
    "Die Welt": "Le Monde",

    # Figures (DE) - quelques exemples
    "Bube der Stäbe": "Le Valet de Baton",
    "Ritter der Stäbe": "Le Cavalier de Baton",

    # --- Italien (IT) vers français ---
    "Il Matto": "Le Mat",
    "Il Mago": "Le Bateleur",
    "La Papessa": "La Papesse",
    "L'Imperatrice": "L'Imperatrice",
    "L'Imperatore": "L'Empereur",
    "Il Papa": "Le Pape",
    "Gli Amanti": "L'Amoureux",
    "Il Carro": "Le Chariot",
    "La Giustizia": "La Justice",
    "L'Eremita": "L'Hermite",
    "La Ruota della Fortuna": "La Roue de La Fortune",
    "La Forza": "La Force",
    "L'Appeso": "Le Pendu",
    "La Morte": "La Mort",
    "La Temperanza": "La Temperance",
    "Il Diavolo": "Le Diable",
    "La Torre": "La Maison Dieu",
    "Le Stelle": "L'Etoile",
    "La Luna": "La Lune",
    "Il Sole": "Le Soleil",
    "Il Giudizio": "Le Jugement",
    "Il Mondo": "Le Monde",
    
    # --- Russe (RU) vers français ---
    "Дурак": "Le Mat",
    "Шут": "Le Mat",
    "Маг": "Le Bateleur",
    "Жрица": "La Papesse",
    "Императрица": "L'Imperatrice",
    "Император": "L'Empereur",
    "Иерофант": "Le Pape",
    "Влюблённые": "L'Amoureux",
    "Влюбленные": "L'Amoureux",
    "Колёсница": "Le Chariot",
    "Сила": "La Force",
    "Отшельник": "L'Hermite",
    "Колесо Фортуны": "La Roue de La Fortune",
    "Повешенный": "Le Pendu",
    "Смерть": "La Mort",
    "Умеренность": "La Temperance",
    "Дьявол": "Le Diable",
    "Башня": "La Maison Dieu",
    "Звезда": "L'Etoile",
    "Луна": "La Lune",
    "Солнце": "Le Soleil",
    "Суд": "Le Jugement",
    "Мир": "Le Monde",

    # --- Japonais (JA) vers français ---
    "愚者": "Le Mat",
    "魔術師": "Le Bateleur",
    "女教皇": "La Papesse",
    "女帝": "L'Imperatrice",
    "皇帝": "L'Empereur",
    "教皇": "Le Pape",
    "恋人": "L'Amoureux",
    "戦車": "Le Chariot",
    "力": "La Force",
    "隠者": "L'Hermite",
    "運命の輪": "La Roue de La Fortune",
    "吊るされた男": "Le Pendu",
    "死神": "La Mort",
    "節制": "La Temperance",
    "悪魔": "Le Diable",
    "塔": "La Maison Dieu",
    "星": "L'Etoile",
    "月": "La Lune",
    "太陽": "Le Soleil",
    "審判": "Le Jugement",
    "世界": "Le Monde",

    # --- Turc (TR) vers français ---
    "Deli": "Le Mat",
    "Büyücü": "Le Bateleur",
    "Başrahibe": "La Papesse",
    "İmparatoriçe": "L'Imperatrice",
    "İmparator": "L'Empereur",
    "Başrahip": "Le Pape",
    "Aşıklar": "L'Amoureux",
    "Savaş Arabası": "Le Chariot",
    "Güç": "La Force",
    "Keşiş": "L'Hermite",
    "Kaderin Çarkı": "La Roue de La Fortune",
    "Asılan Adam": "Le Pendu",
    "Ölüm": "La Mort",
    "Yaratma": "La Temperance",
    "Şeytan": "Le Diable",
    "Kule": "La Maison Dieu",
    "Yıldız": "L'Etoile",
    "Ay": "La Lune",
    "Güneş": "Le Soleil",
    "Mahkeme": "Le Jugement",
    "Dünya": "Le Monde",

    # --- Chinois simplifié (ZH) vers français ---
    "愚者": "Le Mat",
    "魔术师": "Le Bateleur",
    "女祭司": "La Papesse",
    "皇后": "L'Imperatrice",
    "皇帝": "L'Empereur",
    "教皇": "Le Pape",
    "恋人": "L'Amoureux",
    "战车": "Le Chariot",
    "力量": "La Force",
    "隐士": "L'Hermite",
    "命运之轮": "La Roue de La Fortune",
    "倒吊人": "Le Pendu",
    "死亡": "La Mort",
    "节制": "La Temperance",
    "恶魔": "Le Diable",
    "高塔": "La Maison Dieu",
    "星星": "L'Etoile",
    "月亮": "La Lune",
    "太阳": "Le Soleil",
    "审判": "Le Jugement",
    "世界": "Le Monde",
}

# --- Helpers ---
def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def get_card_image_path(card_name: str, state: str = "droite") -> str:
    base_path = "tarot_img/MajorArcanaCards"
    if card_name in SPECIAL_CARD_MAPPINGS:
        french_file_name = SPECIAL_CARD_MAPPINGS[card_name]
    else:
        french_file_name = card_name

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
            if os.path.exists(path_candidate):
                return path_candidate

    return os.path.join("tarot_img", "Back.jpg")


def get_french_card_name(card_name: str) -> str:
    if not card_name:
        return card_name
    if card_name in SPECIAL_CARD_MAPPINGS:
        return SPECIAL_CARD_MAPPINGS[card_name]

    normalized = remove_accents(card_name).strip()
    for key, val in SPECIAL_CARD_MAPPINGS.items():
        if remove_accents(key).strip().lower() == normalized.lower():
            return val

    lower = card_name.lower()
    for suffix in [" a l'envers", " a l'envers.jpg", " a l'envers.png"]:
        if lower.endswith(suffix):
            base = card_name[: -len(suffix)].strip()
            if base in SPECIAL_CARD_MAPPINGS:
                return SPECIAL_CARD_MAPPINGS[base]

    return card_name


# --- Name mappings (from previous card_name_mapping.py) ---
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
    "Cavalier de Bâton": "Knight of Wands",
}

FRENCH_TO_PORTUGUESE = {
    "Le Mat": "O Louco",
    "Le Bateleur": "O Mago",
    "La Papesse": "A Papisa",
    "L'Imperatrice": "A Imperatriz",
    "L'Imperatrice": "A Imperatriz",
    "L'Empereur": "O Imperador",
    "Le Pape": "O Papa",
    "L'Amoureux": "Os Amantes",
    "Le Chariot": "O Carro",
    "La Justice": "A Justiça",
    "L'Hermite": "O Eremita",
    "La Roue de Fortune": "A Roda da Fortuna",
    "La Force": "A Força",
    "Le Pendu": "O Enforcado",
    "La Mort": "A Morte",
    "L'Etoile": "A Estrela",
    "L'Ã‰toile": "A Estrela",
    "La Lune": "A Lua",
    "Le Soleil": "O Sol",
    "Le Jugement": "O Julgamento",
    "Le Monde": "O Mundo",
    # Quelques cartes mineures courantes
    "Valet de Bâton": "O Valete de Paus",
    "Valet de Baton": "O Valete de Paus",
    "Roi de Denier": "O Rei de Ouros",
    "Reine de Denier": "A Rainha de Ouros",
    "Cavalier de Denier": "O Cavaleiro de Ouros",
    "Valet de Denier": "O Valete de Ouros",
    "Valet de Coupe": "O Valete de Copas",
    "Roi d'Épée": "O Rei de Espadas",
    "Roi d'Epée": "O Rei de Espadas",
    "Reine d'Épée": "A Rainha de Espadas",
    "Cavalier d'Épée": "O Cavaleiro de Espadas",
    "Valet d'Épée": "O Valete de Espadas",
    "Roi de Coupe": "O Rei de Copas",
    "Reine de Coupe": "A Rainha de Copas",
    "Cavalier de Coupe": "O Cavaleiro de Copas",
    "Roi de Bâton": "O Rei de Paus",
    "Reine de Bâton": "A Rainha de Paus",
    "Cavalier de Bâton": "O Cavaleiro de Paus",
}

FRENCH_TO_RUSSIAN = {
    "Le Mat": "Дурак",
    "Le Bateleur": "Маг",
    "La Papesse": "Жрица",
    "L'Imperatrice": "Императрица",
    "L'Empereur": "Император",
    "Le Pape": "Иерофант",
    "L'Amoureux": "Влюблённые",
    "Le Chariot": "Колёсница",
    "La Justice": "Справедливость",
    "L'Hermite": "Отшельник",
    "La Roue de La Fortune": "Колесо Фортуны",
    "La Force": "Сила",
    "Le Pendu": "Повешенный",
    "La Mort": "Смерть",
    "La Temperance": "Умеренность",
    "Le Diable": "Дьявол",
    "La Maison Dieu": "Башня",
    "L'Etoile": "Звезда",
    "La Lune": "Луна",
    "Le Soleil": "Солнце",
    "Le Jugement": "Суд",
    "Le Monde": "Мир",
}


def _normalize_card_key(name: str) -> str:
    if not name:
        return ""
    s = name.strip().lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c))
    for prefix in ("le ", "la ", "l'", "l "):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    s = s.replace("d'", " ")
    s = s.replace(" de ", " ")
    s = s.replace(" des ", " ")
    for ch in [".", "'", '"', ","]:
        s = s.replace(ch, "")
    s = ' '.join(s.split())
    return s


def _get_card_name_pt(french_name: str) -> str:
    if not french_name:
        return french_name
    key = _normalize_card_key(french_name)
    global _FRENCH_PT_NORMAL_INDEX
    if '_FRENCH_PT_NORMAL_INDEX' not in globals():
        _FRENCH_PT_NORMAL_INDEX = {}
        for f, pt in FRENCH_TO_PORTUGUESE.items():
            _FRENCH_PT_NORMAL_INDEX[_normalize_card_key(f)] = pt
        try:
            for k, v in SPECIAL_CARD_MAPPINGS.items():
                _FRENCH_PT_NORMAL_INDEX[_normalize_card_key(v)] = FRENCH_TO_PORTUGUESE.get(v, FRENCH_TO_PORTUGUESE.get(k, v))
        except Exception:
            pass

    return _FRENCH_PT_NORMAL_INDEX.get(key, french_name)


def get_card_name_for_lang(french_name: str, target_lang: str) -> str:
    if not target_lang:
        return french_name
    lang = str(target_lang).lower()
    if '_' in lang:
        lang = lang.split('_', 1)[0]
    if '-' in lang:
        lang = lang.split('-', 1)[0]

    if lang == 'en':
        return FRENCH_TO_ENGLISH.get(french_name, french_name)
    if lang == 'pt':
        return _get_card_name_pt(french_name)
    if lang == 'ru':
        return FRENCH_TO_RUSSIAN.get(french_name, french_name)
    return french_name
