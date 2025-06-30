# Script PowerShell pour préparer la publication sur les stores
# Usage: .\prepare_store_release.ps1

Write-Host "🚀 Préparation de l'app Tarot pour publication..." -ForegroundColor Green

# 1. Vérifier les fichiers de base
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Erreur: main.py non trouvé. Êtes-vous dans le bon répertoire ?" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "buildozer.spec")) {
    Write-Host "❌ Erreur: buildozer.spec non trouvé" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Fichiers de base trouvés" -ForegroundColor Green

# 2. Demander la version
$VERSION = Read-Host "Version de l'app (ex: 1.0.0)"
if ([string]::IsNullOrEmpty($VERSION)) {
    $VERSION = "1.0.0"
}

# 3. Mettre à jour main.py avec la version
$mainContent = Get-Content "main.py"
$mainContent[0] = "__version__ = `"$VERSION`""
$mainContent | Set-Content "main.py"

Write-Host "✅ Version mise à jour: $VERSION" -ForegroundColor Green

# 4. Vérifier requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Host "⚠️ requirements.txt manquant, création..." -ForegroundColor Yellow
    @"
kivy==2.2.0
pillow==10.0.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
}

# 5. Vérifier les images
Write-Host "🖼️ Vérification des assets..." -ForegroundColor Cyan

$requiredImages = @(
    "tarot_img\bg.jpg",
    "tarot_img\Back.jpg", 
    "tarot_img\tapis.ico"
)

foreach ($img in $requiredImages) {
    if (Test-Path $img) {
        Write-Host "✅ $img trouvé" -ForegroundColor Green
    } else {
        Write-Host "❌ $img manquant" -ForegroundColor Red
    }
}

# 6. Configuration Git
Write-Host "📦 Préparation Git..." -ForegroundColor Cyan

if (-not (Test-Path ".git")) {
    Write-Host "🔧 Initialisation Git..." -ForegroundColor Yellow
    git init
}

# Ajouter tous les fichiers
git add .

# Créer le commit
git commit -m "Préparation version $VERSION pour publication"

# Créer le tag
git tag "v$VERSION"

Write-Host "✅ Tag v$VERSION créé" -ForegroundColor Green

# 7. Instructions finales
Write-Host ""
Write-Host "🎯 PRÊT POUR PUBLICATION !" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes :" -ForegroundColor Cyan
Write-Host "1. Créer un repo GitHub et pousser:"
Write-Host "   git remote add origin https://github.com/VOTRE_USERNAME/tarot-app.git"
Write-Host "   git push -u origin main"
Write-Host "   git push origin v$VERSION"
Write-Host ""
Write-Host "2. Configurer les secrets GitHub (voir STORE_DEPLOYMENT.md)"
Write-Host ""
Write-Host "3. GitHub Actions va automatiquement compiler et publier"
Write-Host ""
Write-Host "📱 Résumé :" -ForegroundColor Yellow
Write-Host "   - Version: $VERSION"
Write-Host "   - Tag Git: v$VERSION"
Write-Host "   - Prêt pour GitHub Actions"
Write-Host ""
Write-Host "🚀 Bonne chance pour votre publication !" -ForegroundColor Green

# Optionnel: Ouvrir le navigateur sur GitHub
$openGitHub = Read-Host "Ouvrir GitHub pour créer le repo ? (y/N)"
if ($openGitHub -eq "y" -or $openGitHub -eq "Y") {
    Start-Process "https://github.com/new"
}
