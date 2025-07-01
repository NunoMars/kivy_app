# Script de déploiement PowerShell pour Ma Carte de Tarot
# Usage: .\deploy.ps1 [version]

param(
    [string]$Version = "v1.0.0"
)

$ErrorActionPreference = "Stop"

# Configuration
$ProjectName = "Ma Carte de Tarot"
$Branch = "main"

Write-Host "🚀 Déploiement $ProjectName - Version $Version" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Vérifier que nous sommes sur la bonne branche
$CurrentBranch = git branch --show-current
if ($CurrentBranch -ne $Branch) {
    Write-Host "❌ Vous devez être sur la branche $Branch" -ForegroundColor Red
    Write-Host "   Branche actuelle: $CurrentBranch" -ForegroundColor Yellow
    exit 1
}

# Vérifier que le workspace est propre
$GitStatus = git status --porcelain
if ($GitStatus) {
    Write-Host "⚠️  Des changements non committés détectés" -ForegroundColor Yellow
    Write-Host "📋 Fichiers modifiés:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $Continue = Read-Host "Continuer quand même? (y/N)"
    if ($Continue -notmatch "^[Yy]$") {
        Write-Host "❌ Déploiement annulé" -ForegroundColor Red
        exit 1
    }
}

# Validation finale
Write-Host "🔍 Validation finale du pipeline..." -ForegroundColor Cyan
try {
    # Appliquer les corrections buildozer avant validation
    Write-Host "🔧 Application des corrections buildozer..." -ForegroundColor Yellow
    & python create_android_icon.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Échec création icône, mais on continue..." -ForegroundColor Yellow
    }
    
    & python fix_buildozer_errors.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Échec corrections buildozer, mais on continue..." -ForegroundColor Yellow
    }
    
    # Validation du workflow
    & python validate_aab_workflow.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Validation réussie" -ForegroundColor Green
    } else {
        Write-Host "❌ Validation échouée" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors de la validation: $_" -ForegroundColor Red
    exit 1
}

# Commit et push
Write-Host "📤 Push du code..." -ForegroundColor Cyan
git add .
try {
    git commit -m "fix: correction erreurs AAB - icône PNG + AndroidX + extractNativeLibs"
} catch {
    Write-Host "Nothing to commit" -ForegroundColor Yellow
}
git push origin $Branch

Write-Host "✅ Code pushé vers $Branch" -ForegroundColor Green

# Attendre un peu pour que les hooks Git se déclenchent
Write-Host "⏳ Attente de synchronisation GitHub..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Créer et pousser le tag
Write-Host "🏷️  Création du tag $Version..." -ForegroundColor Cyan
$ExistingTag = git tag -l | Select-String "^$Version$"
if ($ExistingTag) {
    Write-Host "⚠️  Le tag $Version existe déjà" -ForegroundColor Yellow
    $Force = Read-Host "Forcer la recréation? (y/N)"
    if ($Force -match "^[Yy]$") {
        git tag -d $Version
        git push origin ":refs/tags/$Version"
    } else {
        Write-Host "❌ Déploiement annulé" -ForegroundColor Red
        exit 1
    }
}

$TagMessage = @"
Release $Version - AAB ready for Google Play Store

🎯 Features:
- App Bundle (AAB) generation for Google Play Store
- Automated signing with production keys
- Compatible with Ubuntu 22.04 CI/CD
- Optimized build pipeline without libffi/autotools errors

🔧 Technical:
- Kivy 2.2.0 with optimized dependencies  
- Android NDK 25c for SDL2 compatibility
- API Level 33 for modern Android support
- Automated GitHub Actions workflow

🚀 Ready for Google Play Store publication!
"@

git tag -a $Version -m $TagMessage
git push origin $Version

Write-Host "✅ Tag $Version créé et poussé" -ForegroundColor Green

# Obtenir l'URL du repository
$RemoteUrl = git config --get remote.origin.url
$RepoPath = if ($RemoteUrl -match "github\.com[:/]([^.]+)") { $Matches[1] } else { "YOUR_REPO" }

# Afficher les informations de déploiement
Write-Host ""
Write-Host "🎉 DÉPLOIEMENT TERMINÉ !" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "📋 Informations:" -ForegroundColor Cyan
Write-Host "   Version: $Version" -ForegroundColor White
Write-Host "   Branche: $Branch" -ForegroundColor White
Write-Host "   Tag: $Version" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Liens utiles:" -ForegroundColor Cyan
Write-Host "   GitHub Actions: https://github.com/$RepoPath/actions" -ForegroundColor Blue
Write-Host "   Releases: https://github.com/$RepoPath/releases" -ForegroundColor Blue
Write-Host ""
Write-Host "⏳ Le build GitHub Actions va démarrer automatiquement..." -ForegroundColor Yellow
Write-Host "📱 L'AAB sera disponible dans les artifacts et releases" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔑 N'oubliez pas de configurer les secrets GitHub pour la signature de production:" -ForegroundColor Magenta
Write-Host "   - ANDROID_KEYSTORE_BASE64" -ForegroundColor White
Write-Host "   - KEYSTORE_PASSWORD" -ForegroundColor White
Write-Host "   - KEY_ALIAS" -ForegroundColor White
Write-Host "   - KEY_PASSWORD" -ForegroundColor White
Write-Host "   - GOOGLE_PLAY_SERVICE_ACCOUNT (pour publication automatique)" -ForegroundColor White
Write-Host ""
Write-Host "🎮 Ma Carte de Tarot est prête pour Google Play Store ! 🔮" -ForegroundColor Green
