#!/usr/bin/env python3
"""
Script pour vérifier et créer l'icône Android PNG si nécessaire
"""

import os

def check_or_create_android_icon():
    """Vérifier si l'icône existe, sinon la créer"""
    
    icon_path = "tarot_img/icon.png"
    
    # Vérifier si l'icône existe déjà
    if os.path.exists(icon_path):
        print(f"✅ Icône Android déjà présente: {icon_path}")
        
        # Vérifier la taille du fichier (minimum raisonnable)
        size = os.path.getsize(icon_path)
        if size > 1000:  # Au moins 1KB
            print(f"✅ Icône valide ({size} bytes)")
            return True
        else:
            print(f"⚠️  Icône trop petite ({size} bytes), recréation...")
    
    # Créer l'icône si elle n'existe pas ou est invalide
    print("📱 Création de l'icône Android...")
    
    try:
        from PIL import Image
        create_icon_with_pillow()
    except ImportError:
        print("⚠️  Pillow non disponible, création d'une icône simple...")
        create_simple_icon()
    
    return True

def create_icon_with_pillow():
    """Créer l'icône avec Pillow si disponible"""
    from PIL import Image
    
    # Chercher une image source
    source_files = [
        "tarot_img/tapis.ico",
        "tarot_img/bg.jpg",
        "tarot_img/carte.gif"
    ]
    
    source_image = None
    for file_path in source_files:
        if os.path.exists(file_path):
            source_image = file_path
            break
    
    if source_image:
        print(f"📱 Création depuis: {source_image}")
        img = Image.open(source_image)
        icon = img.resize((512, 512), Image.Resampling.LANCZOS)
        if icon.mode != 'RGB':
            icon = icon.convert('RGB')
        icon.save("tarot_img/icon.png", "PNG")
        print("✅ Icône créée avec Pillow")
    else:
        create_simple_icon()

def create_simple_icon():
    """Créer une icône simple sans Pillow"""
    # Créer un fichier PNG minimal (1x1 pixel transparent)
    # Ce n'est pas idéal mais permet au build de continuer
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open("tarot_img/icon.png", "wb") as f:
        f.write(png_data)
    
    print("✅ Icône simple créée (fallback)")

if __name__ == "__main__":
    # Créer le dossier s'il n'existe pas
    os.makedirs("tarot_img", exist_ok=True)
    
    check_or_create_android_icon()
