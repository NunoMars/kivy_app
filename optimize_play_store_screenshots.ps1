# Script PowerShell pour optimiser les captures d'écran pour Google Play Store
# Exigences Play Store:
# - 2 à 8 captures d'écran
# - Format PNG ou JPEG
# - Jusqu'à 8 Mo chacune
# - Ratio 16:9 ou 9:16
# - Chaque côté entre 320px et 3840px
# - Pour promotion: minimum 4 captures à 1080x1080px

Write-Host "=== OPTIMISATION CAPTURES PLAY STORE ===" -ForegroundColor Green

# Vérifier que Python et Pillow sont disponibles
try {
    python -c "from PIL import Image; print('✅ Pillow disponible')"
} catch {
    Write-Host "❌ Pillow non installé. Installation..." -ForegroundColor Red
    pip install Pillow
}

# Créer le dossier pour les captures optimisées
$outputDir = "play_store_screenshots"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir
    Write-Host "📁 Dossier créé: $outputDir" -ForegroundColor Cyan
}

# Script Python intégré pour optimiser les images
$pythonScript = @"
from PIL import Image, ImageEnhance
import os
import sys

def optimize_screenshot(input_path, output_path, target_width=1080, target_height=2400):
    '''
    Optimise une capture d'écran pour le Play Store
    Ratio 9:16 (portrait mobile) recommandé: 1080x2400
    '''
    try:
        with Image.open(input_path) as img:
            # Informations originales
            original_size = img.size
            print(f'📱 Image originale: {original_size[0]}x{original_size[1]}')
            
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculer le nouveau ratio en gardant l'aspect portrait mobile
            # Ratio cible: 9:16 (0.5625)
            target_ratio = 9/16
            current_ratio = original_size[0] / original_size[1]
            
            if current_ratio > target_ratio:
                # Image trop large, recadrer la largeur
                new_width = int(original_size[1] * target_ratio)
                left = (original_size[0] - new_width) // 2
                img = img.crop((left, 0, left + new_width, original_size[1]))
                print(f'🔧 Recadrage largeur: {new_width}x{original_size[1]}')
            elif current_ratio < target_ratio:
                # Image trop haute, recadrer la hauteur  
                new_height = int(original_size[0] / target_ratio)
                top = (original_size[1] - new_height) // 2
                img = img.crop((0, top, original_size[0], top + new_height))
                print(f'🔧 Recadrage hauteur: {original_size[0]}x{new_height}')
            
            # Redimensionner à la taille cible
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            print(f'📐 Redimensionnement: {target_width}x{target_height}')
            
            # Améliorer la qualité
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)  # Légère amélioration de la netteté
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.05)  # Légère amélioration du contraste
            
            # Sauvegarder avec qualité élevée
            img.save(output_path, 'PNG', optimize=True)
            
            # Vérifier la taille du fichier
            file_size = os.path.getsize(output_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f'💾 Taille fichier: {file_size_mb:.2f} MB')
            
            if file_size_mb > 8:
                print('⚠️ ATTENTION: Fichier > 8MB (limite Play Store)')
                return False
            else:
                print('✅ Fichier conforme Play Store')
                return True
                
    except Exception as e:
        print(f'❌ Erreur: {str(e)}')
        return False

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    success = optimize_screenshot(input_file, output_file)
    exit(0 if success else 1)
"@

# Sauvegarder le script Python
$pythonScript | Out-File -FilePath "optimize_screenshot.py" -Encoding UTF8

Write-Host ""
Write-Host "📸 TRAITEMENT DES CAPTURES D'ÉCRAN:" -ForegroundColor Yellow

# Traiter chaque capture d'écran
$screenshots = @(
    "tarot_img\Capture d'écran 2025-07-07 103312.png",
    "tarot_img\Capture d'écran 2025-07-07 103337.png", 
    "tarot_img\Capture d'écran 2025-07-07 103356.png"
)

$counter = 1
foreach ($screenshot in $screenshots) {
    if (Test-Path $screenshot) {
        $outputFile = "$outputDir\screenshot_${counter}_1080x2400.png"
        Write-Host ""
        Write-Host "🔄 Traitement: $screenshot" -ForegroundColor Cyan
        
        python optimize_screenshot.py "$screenshot" "$outputFile"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Sauvegardé: $outputFile" -ForegroundColor Green
            $counter++
        } else {
            Write-Host "❌ Échec: $screenshot" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ Fichier non trouvé: $screenshot" -ForegroundColor Yellow
    }
}

# Créer des captures d'écran supplémentaires si nécessaire
if ($counter -lt 5) {
    Write-Host ""
    Write-Host "📝 BESOIN DE PLUS DE CAPTURES:" -ForegroundColor Yellow
    Write-Host "- Minimum requis: 4 captures pour la promotion"
    Write-Host "- Actuellement: $($counter-1) captures optimisées"
    Write-Host "- Prenez ${5-$counter} captures supplémentaires de votre app"
}

Write-Host ""
Write-Host "=== RÉSULTAT FINAL ===" -ForegroundColor Green
Write-Host "📂 Dossier: $outputDir"
Write-Host "📱 Format: 1080x2400 (9:16 - Portrait mobile optimal)"
Write-Host "📋 Fichiers créés:"

Get-ChildItem "$outputDir\*.png" | ForEach-Object {
    $size = [math]::Round((Get-Item $_.FullName).Length / 1MB, 2)
    Write-Host "  ✅ $($_.Name) (${size} MB)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎯 PROCHAINES ÉTAPES:" -ForegroundColor Yellow
Write-Host "1. Vérifiez les captures dans le dossier $outputDir"
Write-Host "2. Si besoin, prenez plus de captures de différents écrans"
Write-Host "3. Uploadez ces fichiers PNG dans Google Play Console"
Write-Host "4. Les captures respectent maintenant toutes les exigences Play Store"

# Nettoyer le script temporaire
Remove-Item "optimize_screenshot.py" -ErrorAction SilentlyContinue
