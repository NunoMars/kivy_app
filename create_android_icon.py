#!/usr/bin/env python3
"""
Script pour créer une icône PNG valide pour Android à partir d'une image existante
"""

from PIL import Image
import os

def create_android_icon():
    """Crée une icône PNG 512x512 pour Android"""
    
    # Essayons plusieurs sources possibles
    source_files = [
        "tarot_img/Back.jpg",
        "tarot_img/bg.jpg", 
        "tarot_img/carte.gif",
        "tarot_img/MajorArcanaCards/Le Bateleur.jpg"
    ]
    
    source_file = None
    for file in source_files:
        if os.path.exists(file):
            source_file = file
            break
    
    if not source_file:
        print("❌ Aucune image source trouvée")
        return False
    
    try:
        print(f"📷 Utilisation de: {source_file}")
        
        # Ouvrir l'image source
        with Image.open(source_file) as img:
            # Convertir en RGB si nécessaire (pour les GIF/PNG avec transparence)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionner en 512x512 (taille recommandée pour Android)
            icon = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Sauvegarder l'icône
            output_path = "tarot_img/icon.png"
            icon.save(output_path, "PNG", quality=95)
            
            print(f"✅ Icône créée: {output_path}")
            print(f"📏 Taille: 512x512 pixels")
            
            # Créer aussi une version 192x192 pour la compatibilité
            icon_small = img.resize((192, 192), Image.Resampling.LANCZOS)
            icon_small.save("tarot_img/icon_small.png", "PNG", quality=95)
            print(f"✅ Icône petite créée: tarot_img/icon_small.png")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'icône: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Création d'icône Android...")
    
    if create_android_icon():
        print("\n🎉 Icône créée avec succès !")
        print("\n📝 Prochaines étapes:")
        print("1. Mettez à jour buildozer.spec:")
        print("   icon.filename = %(source.dir)s/tarot_img/icon.png")
        print("2. Relancez le build: buildozer android debug")
    else:
        print("\n❌ Échec de la création de l'icône")
        print("Vérifiez que Pillow est installé: pip install Pillow")
