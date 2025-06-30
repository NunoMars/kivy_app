#!/usr/bin/env python3
"""
Générateur d'assets pour publication sur Google Play Store
Crée automatiquement les images et textes nécessaires
"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

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
    draw.ellipse([margin-border_width, margin-border_width, 
                 size-margin+border_width, size-margin+border_width], 
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

def create_store_descriptions():
    """Crée les fichiers de description pour le store"""
    
    short_description = "Tarot de Marseille authentique - 78 cartes - Prédictions mystiques"
    
    long_description = """🔮 MA CARTE DE TAROT - L'authenticité du Tarot de Marseille

Découvrez les secrets de votre avenir avec notre application de tirage de tarot authentique basée sur la tradition française séculaire.

✨ FONCTIONNALITÉS COMPLÈTES :
• 78 cartes du Tarot de Marseille traditionnel
• Tirages en position droite et inversée
• Significations détaillées et authentiques
• Interface moderne et intuitive
• Animations mystiques immersives
• Fonctionne entièrement hors-ligne
• Design optimisé pour mobile

🎯 POURQUOI CHOISIR NOTRE APP ?
• Basée sur l'authentique Tarot de Marseille français
• Interprétations nuancées par des experts
• Design moderne respectant la tradition
• Expérience utilisateur fluide et captivante
• Pas d'abonnement, utilisation libre

🔮 COMMENT UTILISER :
1. Concentrez-vous sur votre question intérieure
2. Touchez la carte pour révéler votre tirage
3. Découvrez la signification personnalisée
4. Méditez sur les conseils prodigués

🌟 PARFAIT POUR :
• Guidance quotidienne et développement personnel
• Moments de réflexion et d'introspection
• Découverte de l'art divinatoire du tarot
• Connexion avec votre intuition profonde

📱 INTERFACE MODERNE :
• Navigation intuitive
• Animations fluides
• Couleurs mystiques apaisantes
• Textes lisibles et bien structurés

Téléchargez maintenant et laissez la sagesse ancestrale du Tarot de Marseille illuminer votre chemin !

Note : Cette application est destinée au divertissement et au développement personnel. Les prédictions ne substituent pas les conseils professionnels."""

    keywords = [
        "tarot", "marseille", "divination", "cartes", "prédiction", "voyance", 
        "spiritualité", "ésotérisme", "oracle", "tirage", "mystique", "avenir", 
        "destin", "guidance", "développement personnel", "méditation", "intuition"
    ]
    
    # Sauvegarder les descriptions
    os.makedirs('store_assets', exist_ok=True)
    
    with open('store_assets/descriptions.txt', 'w', encoding='utf-8') as f:
        f.write("=== DESCRIPTION COURTE (80 caractères max) ===\n")
        f.write(short_description + "\n\n")
        f.write("=== DESCRIPTION LONGUE ===\n")
        f.write(long_description + "\n\n")
        f.write("=== MOTS-CLÉS ASO ===\n")
        f.write(", ".join(keywords) + "\n")
    
    print("✅ Descriptions sauvegardées: store_assets/descriptions.txt")

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
    create_store_descriptions()
    
    print("\n🎯 ASSETS GÉNÉRÉS AVEC SUCCÈS !")
    print("\nPROCHAINES ÉTAPES :")
    print("1. Remplacer les screenshots templates par de vrais captures")
    print("2. Vérifier les descriptions dans store_assets/descriptions.txt")
    print("3. Utiliser app_icon_512x512.png comme icône principale")
    print("4. Uploader feature_graphic_1024x500.png comme bannière")
    print("\n📁 Tous les fichiers sont dans le dossier 'store_assets/'")

if __name__ == "__main__":
    main()
