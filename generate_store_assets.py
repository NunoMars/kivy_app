#!/usr/bin/env python3
"""
Générateur d'assets pour publication sur Google Play Store
Crée automatiquement les images et textes nécessaires
"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Store descriptions for Google Play
STORE_DESCRIPTIONS = {
    "short": "🔮 Tirage de Tarot de Marseille authentique - Guidance spirituelle",
    
    "long": """🔮 **MA CARTE DE TAROT - TIRAGE AUTHENTIQUE DE MARSEILLE** 🔮

Découvrez l'art ancestral du Tarot de Marseille avec une application authentique et respectueuse de la tradition cartomantique française. Que vous soyez débutant curieux ou pratiquant expérimenté, plongez dans l'univers mystique des 78 arcanes.

✨ **CARACTÉRISTIQUES PRINCIPALES**

🎴 **Cartes Authentiques**
• 22 Arcanes Majeurs du Tarot de Marseille traditionnel
• Illustrations fidèles aux tarots historiques
• Symbolique préservée et respectée

🔮 **Tirages Personnalisés**
• Tirage quotidien pour guidance spirituelle
• Sélection aléatoire authentique
• Interprétation détaillée de chaque carte

📖 **Significations Complètes**
• Interprétations traditionnelles enrichies
• Signification à l'endroit et à l'envers
• Contexte spirituel et psychologique
• Conseils pratiques pour votre quotidien

🌟 **Interface Intuitive**
• Design élégant et mystique
• Navigation fluide et apaisante
• Animations douces pour l'immersion
• Optimisé pour tous les écrans

🎯 **POURQUOI CHOISIR CETTE APPLICATION ?**

• **Authenticité** : Respecte la tradition du Tarot de Marseille
• **Gratuit** : Accès complet sans frais cachés
• **Hors ligne** : Fonctionne sans connexion internet
• **Respect** : Approche bienveillante de la divination
• **Apprentissage** : Parfait pour découvrir le tarot

🧘 **IDÉAL POUR :**
• Méditation et introspection quotidienne
• Guidance dans les moments de doute
• Apprentissage de la cartomancie
• Développement personnel et spirituel

🔒 **CONFIDENTIALITÉ ET RESPECT**
Vos tirages restent privés et confidentiels. Aucune donnée personnelle n'est collectée.

⭐ **Note importante :** Le tarot est un outil de réflexion personnelle et de développement spirituel. Les interprétations proposées sont à des fins de divertissement et d'introspection.

📧 **Support** : tarot.support@gmail.com
🌐 **Site web** : https://nunomars.github.io/kivy_app/

#TarotDeMarseille #Cartomancie #Spiritualité #Méditation #DéveloppementPersonnel""",

    "keywords": [
        "Tarot de Marseille", "Cartomancie", "Tirage tarot gratuit", 
        "Arcanes majeurs", "Spiritualité", "Méditation", "Divination",
        "Oracle", "Cartes voyance", "Guidance spirituelle", 
        "Développement personnel", "Introspection"
    ]
}

def create_app_icon(size=512):
    """Crée l'icône de l'app en HD"""
    # Créer une image de base
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fond circulaire mystique
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(45, 20, 70, 255))  # Violet mystique
    
    # Bordure dorée
    border_width = size // 25
    draw.ellipse([margin-border_width, margin-borderWidth, 
                 size-margin+border_width, size-margin+borderWidth], 
                outline=(255, 215, 0, 255), width=border_width)
    
    # Symbole central (carte stylisée)
    center = size // 2
    card_width = size // 3
    card_height = int(card_width * 1.4)
    
    # Carte centrale
    card_x = center - card_width // 2
    card_y = center - card_height // 2
    draw.rectangle([card_x, card_y, card_x + card_width, card_y + card_height],
                  fill=(245, 245, 220, 255), outline=(255, 215, 0, 255), width=3)
    
    # Étoiles mystiques
    star_positions = [
        (center - size//4, center - size//4),
        (center + size//4, center - size//4),
        (center - size//4, center + size//4),
        (center + size//4, center + size//4)
    ]
    
    for x, y in star_positions:
        star_size = size // 20
        draw.polygon([
            (x, y - star_size), (x + star_size//3, y - star_size//3),
            (x + star_size, y), (x + star_size//3, y + star_size//3),
            (x, y + star_size), (x - star_size//3, y + star_size//3),
            (x - star_size, y), (x - star_size//3, y - star_size//3)
        ], fill=(255, 215, 0, 255))
    
    # Sauvegarder
    os.makedirs('store_assets', exist_ok=True)
    img.save(f'store_assets/app_icon_{size}x{size}.png')
    print(f"✅ Icône créée: store_assets/app_icon_{size}x{size}.png")

def create_feature_graphic():
    """Crée la bannière feature graphic (1024x500)"""
    width, height = 1024, 500
    img = Image.new('RGB', (width, height), (20, 10, 35))  # Fond sombre mystique
    draw = ImageDraw.Draw(img)
    
    # Dégradé de fond
    for y in range(height):
        r = int(20 + (45 * y / height))
        g = int(10 + (20 * y / height))
        b = int(35 + (70 * y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Titre principal
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        subtitle_font = ImageFont.truetype("arial.ttf", 35)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Texte principal
    title = "TAROT DE MARSEILLE"
    subtitle = "Authentique • Moderne • Mystique"
    
    # Centrer le titre
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
    title_y = height // 3
    
    # Ombre du titre
    draw.text((title_x + 3, title_y + 3), title, fill=(0, 0, 0, 180), font=title_font)
    # Titre principal en or
    draw.text((title_x, title_y), title, fill=(255, 215, 0), font=title_font)
    
    # Sous-titre
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_x = (width - (subtitle_bbox[2] - subtitle_bbox[0])) // 2
    subtitle_y = title_y + 80
    
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(200, 200, 200), font=subtitle_font)
    
    # Éléments décoratifs (cartes stylisées)
    card_positions = [
        (100, 200), (width - 150, 200)
    ]
    
    for x, y in card_positions:
        # Carte inclinée
        card_width, card_height = 80, 120
        draw.polygon([
            (x, y), (x + card_width - 20, y - 20),
            (x + card_width, y + card_height - 20), (x + 20, y + card_height)
        ], fill=(245, 245, 220), outline=(255, 215, 0, 3))
    
    img.save('store_assets/feature_graphic_1024x500.png')
    print("✅ Feature graphic créée: store_assets/feature_graphic_1024x500.png")

def create_screenshots_template():
    """Crée des templates pour les screenshots"""
    phone_width, phone_height = 720, 1280  # Résolution mobile standard
    
    screenshots = [
        {
            'name': 'welcome_screen',
            'title': 'Écran d\'accueil',
            'description': 'Interface élégante et mystique'
        },
        {
            'name': 'card_draw',
            'title': 'Tirage de carte',
            'description': 'Animation immersive du tirage'
        },
        {
            'name': 'card_result',
            'title': 'Révélation',
            'description': 'Signification détaillée'
        },
        {
            'name': 'interpretation',
            'title': 'Interprétation',
            'description': 'Guidance personnalisée'
        }
    ]
    
    for i, screenshot in enumerate(screenshots, 1):
        img = Image.new('RGB', (phone_width, phone_height), (45, 20, 70))
        draw = ImageDraw.Draw(img)
        
        # Simuler l'interface
        # Header
        draw.rectangle([0, 0, phone_width, 150], fill=(30, 15, 50))
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
            small_font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Titre du screenshot
        title = screenshot['title']
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_x = (phone_width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 60), title, fill=(255, 215, 0), font=font)
        
        # Zone de contenu principale
        content_y = 200
        draw.rectangle([50, content_y, phone_width-50, phone_height-200], 
                      fill=(60, 40, 90), outline=(255, 215, 0, 3))
        
        # Description
        desc_lines = textwrap.wrap(screenshot['description'], width=30)
        for j, line in enumerate(desc_lines):
            line_bbox = draw.textbbox((0, 0), line, font=small_font)
            line_x = (phone_width - (line_bbox[2] - line_bbox[0])) // 2
            draw.text((line_x, content_y + 50 + j * 40), line, 
                     fill=(200, 200, 200), font=small_font)
        
        # Note pour le développeur
        note = f"Screenshot {i}/4 - {screenshot['name']}"
        draw.text((50, phone_height - 100), note, fill=(150, 150, 150), font=small_font)
        
        filename = f'store_assets/screenshot_{i}_{screenshot["name"]}.png'
        img.save(filename)
        print(f"✅ Template screenshot créé: {filename}")

def generate_store_descriptions():
    """Génère les fichiers de description pour le store"""
    try:
        # Créer le dossier store_assets s'il n'existe pas
        store_dir = "store_assets"
        os.makedirs(store_dir, exist_ok=True)
        
        # Sauvegarder la description courte
        with open(f"{store_dir}/short_description.txt", "w", encoding="utf-8") as f:
            f.write(STORE_DESCRIPTIONS["short"])
        
        # Sauvegarder la description longue
        with open(f"{store_dir}/long_description.txt", "w", encoding="utf-8") as f:
            f.write(STORE_DESCRIPTIONS["long"])
        
        # Sauvegarder les mots-clés
        with open(f"{store_dir}/keywords.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(STORE_DESCRIPTIONS["keywords"]))
        
        # Créer un fichier de métadonnées pour Google Play
        metadata = {
            "title": "Ma Carte de Tarot",
            "short_description": STORE_DESCRIPTIONS["short"],
            "full_description": STORE_DESCRIPTIONS["long"],
            "category": "Entertainment",
            "content_rating": "Everyone",
            "contact_email": "tarot.support@gmail.com",
            "website": "https://nunomars.github.io/kivy_app/",
            "privacy_policy": "https://nunomars.github.io/kivy_app/privacy-policy.html"
        }
        
        import json
        with open(f"{store_dir}/play_store_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Descriptions du store générées dans {store_dir}/")
        print(f"   - Description courte : {len(STORE_DESCRIPTIONS['short'])} caractères")
        print(f"   - Description longue : {len(STORE_DESCRIPTIONS['long'])} caractères")
        print(f"   - Mots-clés : {len(STORE_DESCRIPTIONS['keywords'])} éléments")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des descriptions : {e}")

def main():
    """Génère tous les assets nécessaires"""
    print("🎨 Génération des assets pour Google Play Store...\n")
    
    # Créer le dossier
    os.makedirs('store_assets', exist_ok=True)
    
    # Générer tous les assets
    create_app_icon(512)  # Icône HD
    create_app_icon(192)  # Icône normale
    create_feature_graphic()
    create_screenshots_template()
    generate_store_descriptions()
    
    print("\n🎯 ASSETS GÉNÉRÉS AVEC SUCCÈS !")
    print("\nPROCHAINES ÉTAPES :")
    print("1. Remplacer les screenshots templates par de vrais captures")
    print("2. Vérifier les descriptions dans store_assets/descriptions.txt")
    print("3. Utiliser app_icon_512x512.png comme icône principale")
    print("4. Uploader feature_graphic_1024x500.png comme bannière")
    print("\n📁 Tous les fichiers sont dans le dossier 'store_assets/'")

if __name__ == "__main__":
    main()
