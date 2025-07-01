#!/usr/bin/env python3
"""
Script pour créer une icône PNG à partir de l'icône ICO existante.
"""
import os
import sys
from PIL import Image


def create_android_icon():
    """Créer une icône Android PNG depuis l'icône ICO"""
    
    ico_path = "tarot_img/tapis.ico"
    png_path = "tarot_img/icon.png"
    
    print(f"🔧 Conversion d'icône: {ico_path} -> {png_path}")
    
    if not os.path.exists(ico_path):
        print(f"❌ Fichier ICO non trouvé: {ico_path}")
        return False
    
    try:
        # Ouvrir l'icône ICO
        with Image.open(ico_path) as img:
            # Convertir en RGBA si nécessaire
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Redimensionner à 512x512 (taille recommandée pour Android)
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Sauvegarder en PNG
            img.save(png_path, 'PNG', optimize=True)
            
        print(f"✅ Icône PNG créée: {png_path}")
        
        # Vérifier que le fichier est valide
        with Image.open(png_path) as test_img:
            print(f"📱 Taille: {test_img.size}")
            print(f"📱 Mode: {test_img.mode}")
            print(f"📱 Format: {test_img.format}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        return False


def create_fallback_icon():
    """Créer une icône de fallback simple si la conversion échoue"""
    
    png_path = "tarot_img/icon.png"
    
    print("🔧 Création d'une icône de fallback...")
    
    try:
        # Créer une image simple 512x512 avec un fond coloré
        img = Image.new('RGBA', (512, 512), (75, 0, 130, 255))  # Indigo pour le tarot
        
        # Ajouter un cercle simple au centre
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Cercle extérieur
        draw.ellipse([50, 50, 462, 462], fill=(138, 43, 226, 255))  # Violet
        
        # Cercle intérieur
        draw.ellipse([100, 100, 412, 412], fill=(25, 25, 112, 255))  # Bleu nuit
        
        # Texte simple
        try:
            from PIL import ImageFont
            # Essayer d'utiliser une police par défaut
            font = ImageFont.load_default()
            draw.text((200, 230), "🔮", font=font, fill=(255, 215, 0, 255))  # Or
            draw.text((180, 270), "TAROT", font=font, fill=(255, 255, 255, 255))  # Blanc
        except Exception:
            # Si pas de police, juste des formes géométriques
            draw.rectangle([200, 200, 312, 312], fill=(255, 215, 0, 255))
        
        # Sauvegarder
        img.save(png_path, 'PNG', optimize=True)
        
        print(f"✅ Icône de fallback créée: {png_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'icône de fallback: {e}")
        return False


def main():
    """Point d'entrée principal"""
    print("🎨 Création d'icône Android pour Ma Carte de Tarot")
    print("=" * 50)
    
    # Essayer de convertir l'icône ICO existante
    if create_android_icon():
        print("✅ Conversion réussie!")
        return 0
    
    print("⚠️  Conversion échouée, création d'une icône de fallback...")
    
    # Créer une icône de fallback
    if create_fallback_icon():
        print("✅ Icône de fallback créée!")
        return 0
    
    print("❌ Impossible de créer une icône")
    return 1


if __name__ == '__main__':
    sys.exit(main())
