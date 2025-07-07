# Script pour créer une capture de présentation optimisée
from PIL import Image, ImageDraw, ImageFont
import os

def create_presentation_screenshot():
    """Crée une capture de présentation pour le Play Store"""
    
    # Dimensions cibles Play Store (9:16 portrait)
    width, height = 1080, 2400
    
    # Couleurs du thème tarot
    bg_color = (25, 25, 35)  # Fond sombre mystique
    accent_color = (153, 102, 51)  # Marron doré
    text_color = (240, 220, 180)  # Beige clair
    
    # Créer l'image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Titre principal
    title_text = "🔮 Ma Carte de Tarot"
    subtitle_text = "Découvrez votre avenir"
    
    # Features
    features = [
        "✨ Tirage gratuit illimité",
        "🃏 22 Arcanes Majeurs",
        "📱 Interface mystique",
        "🔍 Interprétations détaillées",
        "⬆⬇ Cartes endroit & envers",
        "🎯 Guidance spirituelle"
    ]
    
    try:
        # Utiliser une police système par défaut
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        feature_font = ImageFont.load_default()
    except Exception:
        # Fallback si pas de police
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        feature_font = ImageFont.load_default()
    
    # Position du contenu
    y_pos = 300
    
    # Dessiner le titre
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((width//2 - title_width//2, y_pos), title_text, 
              fill=accent_color, font=title_font)
    
    y_pos += 100
    
    # Dessiner le sous-titre
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text((width//2 - subtitle_width//2, y_pos), subtitle_text, 
              fill=text_color, font=subtitle_font)
    
    y_pos += 200
    
    # Dessiner les fonctionnalités
    for feature in features:
        feature_bbox = draw.textbbox((0, 0), feature, font=feature_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        draw.text((width//2 - feature_width//2, y_pos), feature, 
                  fill=text_color, font=feature_font)
        y_pos += 80
    
    # Ajouter un cadre décoratif
    border_width = 10
    draw.rectangle([border_width, border_width, 
                   width-border_width, height-border_width], 
                  outline=accent_color, width=3)
    
    # Sauvegarder
    output_path = "play_store_screenshots/screenshot_4_presentation_1080x2400.png"
    img.save(output_path, 'PNG', optimize=True)
    
    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Capture de présentation créée: {output_path}")
    print(f"📐 Dimensions: {width}x{height}")
    print(f"💾 Taille: {file_size_mb:.2f} MB")
    
    return True

if __name__ == "__main__":
    create_presentation_screenshot()
