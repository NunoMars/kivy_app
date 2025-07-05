# Script PowerShell pour automatiser les tâches de développement Kivy Tarot App
# Usage: .\dev-helper.ps1 [command] [options]

param(
    [string]$Command = "help",
    [string]$Message = "",
    [string]$File = "",
    [switch]$Force
)

# Configuration
$PROJECT_ROOT = $PSScriptRoot
$GITHUB_REPO = "votre-username/kivy_app"  # À modifier

function Show-Help {
    Write-Host "🎮 Kivy Tarot App - Assistant de Développement" -ForegroundColor Cyan
    Write-Host "=" * 50
    Write-Host ""
    Write-Host "COMMANDES DISPONIBLES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Développement:"
    Write-Host "  test-local      - Tester l'app localement"
    Write-Host "  check-triggers  - Vérifier les déclenchements CI/CD"
    Write-Host "  validate        - Valider le code avant commit"
    Write-Host ""
    Write-Host "🔄 Git & CI/CD:"
    Write-Host "  quick-commit    - Commit rapide avec message"
    Write-Host "  push-feature    - Push avec build conditionnelle"
    Write-Host "  create-release  - Créer une nouvelle release"
    Write-Host ""
    Write-Host "🔧 Maintenance:"
    Write-Host "  clean           - Nettoyer le projet"
    Write-Host "  check-deps      - Vérifier les dépendances"
    Write-Host "  setup-env       - Configurer l'environnement"
    Write-Host ""
    Write-Host "📊 Monitoring:"
    Write-Host "  build-status    - Status des builds GitHub"
    Write-Host "  download-aab    - Télécharger dernier AAB"
    Write-Host ""
    Write-Host "EXEMPLES:"
    Write-Host '  .\dev-helper.ps1 quick-commit -Message "fix: corriger bug affichage"'
    Write-Host '  .\dev-helper.ps1 test-local'
    Write-Host '  .\dev-helper.ps1 create-release'
}

function Test-LocalApp {
    Write-Host "🧪 Test de l'application en local..." -ForegroundColor Green
    
    # Vérifier Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion"
    } catch {
        Write-Host "❌ Python non trouvé! Installer Python d'abord." -ForegroundColor Red
        return
    }
    
    # Vérifier les dépendances
    Write-Host "📦 Vérification des dépendances..."
    pip install -r requirements.txt --quiet
    
    # Tester l'import des modules
    Write-Host "🔍 Test d'import des modules..."
    $testScript = @"
import sys
sys.path.append('.')
try:
    import main
    import signification
    print('✅ Tous les modules importés avec succès')
except ImportError as e:
    print(f'❌ Erreur d\'import: {e}')
    sys.exit(1)
"@
    
    $testScript | python
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test d'import réussi"
    } else {
        Write-Host "❌ Échec du test d'import" -ForegroundColor Red
        return
    }
    
    # Lancer l'app (optionnel)
    $response = Read-Host "Lancer l'application ? (o/N)"
    if ($response -eq "o" -or $response -eq "O") {
        Write-Host "🚀 Lancement de l'application..."
        python main.py
    }
}

function Test-Triggers {
    Write-Host "🔍 Test des déclenchements CI/CD..." -ForegroundColor Green
    
    if (Test-Path "test_workflow_triggers.py") {
        python test_workflow_triggers.py
    } else {
        Write-Host "❌ Script de test des triggers non trouvé!" -ForegroundColor Red
    }
}

function Invoke-Validation {
    Write-Host "✅ Validation du code..." -ForegroundColor Green
    
    # Vérification syntaxe Python
    Write-Host "🐍 Vérification syntaxe Python..."
    $pythonFiles = Get-ChildItem -Filter "*.py" | Where-Object { $_.Name -notlike "*test*" }
    
    foreach ($file in $pythonFiles) {
        python -m py_compile $file.Name
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $($file.Name): Syntaxe OK"
        } else {
            Write-Host "❌ $($file.Name): Erreur de syntaxe!" -ForegroundColor Red
        }
    }
    
    # Vérifier buildozer.spec
    if (Test-Path "buildozer.spec") {
        Write-Host "✅ buildozer.spec trouvé"
        $content = Get-Content "buildozer.spec"
        if ($content -match "title\s*=") {
            Write-Host "✅ Titre configuré"
        } else {
            Write-Host "⚠️ Titre manquant dans buildozer.spec" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ buildozer.spec manquant!" -ForegroundColor Red
    }
    
    # Vérifier images
    if (Test-Path "tarot_img") {
        $imageCount = (Get-ChildItem "tarot_img" -Recurse -Include "*.jpg", "*.png", "*.gif").Count
        Write-Host "✅ $imageCount images trouvées"
    } else {
        Write-Host "❌ Dossier tarot_img manquant!" -ForegroundColor Red
    }
}

function Invoke-QuickCommit {
    if (-not $Message) {
        $Message = Read-Host "Message du commit"
    }
    
    Write-Host "💾 Commit rapide: $Message" -ForegroundColor Green
    
    # Status git
    git status --porcelain
    
    # Confirmation
    $response = Read-Host "Confirmer le commit ? (o/N)"
    if ($response -ne "o" -and $response -ne "O") {
        Write-Host "❌ Commit annulé"
        return
    }
    
    # Commit
    git add .
    git commit -m $Message
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Commit réussi!"
        
        # Proposer de push
        $pushResponse = Read-Host "Push vers origin ? (o/N)"
        if ($pushResponse -eq "o" -or $pushResponse -eq "O") {
            git push
            Write-Host "🚀 Push effectué!"
        }
    } else {
        Write-Host "❌ Échec du commit" -ForegroundColor Red
    }
}

function Invoke-PushFeature {
    Write-Host "🚀 Push avec build conditionnelle..." -ForegroundColor Green
    
    # Vérifier les fichiers modifiés
    $changedFiles = git diff --name-only HEAD~1..HEAD
    
    if ($changedFiles) {
        Write-Host "📁 Fichiers modifiés:"
        $changedFiles | ForEach-Object { Write-Host "  - $_" }
        
        # Prédire les builds
        Write-Host "🔮 Builds prédites:"
        python test_workflow_triggers.py
    }
    
    git push
}

function New-Release {
    Write-Host "🏷️ Création d'une nouvelle release..." -ForegroundColor Green
    
    # Vérifier si gh CLI est installé
    try {
        gh --version | Out-Null
    } catch {
        Write-Host "❌ GitHub CLI non installé! Installer gh CLI d'abord." -ForegroundColor Red
        return
    }
    
    # Obtenir la dernière version
    try {
        $lastTag = git describe --tags --abbrev=0 2>$null
        Write-Host "🏷️ Dernière version: $lastTag"
    } catch {
        $lastTag = "v0.0.0"
        Write-Host "🏷️ Aucune version précédente trouvée"
    }
    
    # Demander la nouvelle version
    $newVersion = Read-Host "Nouvelle version (ex: v1.2.0)"
    if (-not $newVersion.StartsWith("v")) {
        $newVersion = "v$newVersion"
    }
    
    # Confirmation
    Write-Host "🚀 Créer release $newVersion ?" -ForegroundColor Yellow
    $response = Read-Host "(o/N)"
    
    if ($response -eq "o" -or $response -eq "O") {
        # Créer le tag
        git tag $newVersion
        git push --tags
        
        # Créer la release GitHub
        gh release create $newVersion --generate-notes
        
        Write-Host "✅ Release $newVersion créée!" -ForegroundColor Green
        Write-Host "🏗️ Build automatique en cours sur GitHub Actions..."
    }
}

function Invoke-Clean {
    Write-Host "🧹 Nettoyage du projet..." -ForegroundColor Green
    
    # Cache Python
    if (Test-Path "__pycache__") {
        Remove-Item "__pycache__" -Recurse -Force
        Write-Host "✅ Cache Python supprimé"
    }
    
    # Fichiers .pyc
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
    Write-Host "✅ Fichiers .pyc supprimés"
    
    # Build artifacts locaux
    $buildDirs = @(".buildozer", "bin", "dist")
    foreach ($dir in $buildDirs) {
        if (Test-Path $dir) {
            Remove-Item $dir -Recurse -Force
            Write-Host "✅ $dir supprimé"
        }
    }
    
    Write-Host "🎉 Nettoyage terminé!"
}

function Test-Dependencies {
    Write-Host "📦 Vérification des dépendances..." -ForegroundColor Green
    
    # Python
    try {
        $pythonVersion = python --version
        Write-Host "✅ $pythonVersion"
    } catch {
        Write-Host "❌ Python manquant"
    }
    
    # Pip packages
    Write-Host "📋 Packages Python:"
    $requirements = Get-Content "requirements.txt"
    foreach ($req in $requirements) {
        if ($req -and -not $req.StartsWith("#")) {
            $package = $req.Split("==")[0].Split(">=")[0].Split("<=")[0]
            try {
                pip show $package | Out-Null
                Write-Host "✅ $package"
            } catch {
                Write-Host "❌ $package manquant" -ForegroundColor Red
            }
        }
    }
}

function Get-BuildStatus {
    Write-Host "📊 Status des builds GitHub..." -ForegroundColor Green
    
    try {
        gh run list --limit 5
    } catch {
        Write-Host "❌ Impossible de récupérer le status. Vérifier gh CLI." -ForegroundColor Red
    }
}

function Get-LatestAAB {
    Write-Host "📱 Téléchargement du dernier AAB..." -ForegroundColor Green
    
    try {
        $runs = gh run list --status=success --limit 5 --json databaseId,name
        $buildRun = $runs | ConvertFrom-Json | Where-Object { $_.name -like "*Build*" } | Select-Object -First 1
        
        if ($buildRun) {
            gh run download $buildRun.databaseId
            Write-Host "✅ AAB téléchargé!"
        } else {
            Write-Host "❌ Aucun build réussi trouvé" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Erreur de téléchargement. Vérifier gh CLI." -ForegroundColor Red
    }
}

# Router vers la fonction appropriée
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "test-local" { Test-LocalApp }
    "check-triggers" { Test-Triggers }
    "validate" { Invoke-Validation }
    "quick-commit" { Invoke-QuickCommit }
    "push-feature" { Invoke-PushFeature }
    "create-release" { New-Release }
    "clean" { Invoke-Clean }
    "check-deps" { Test-Dependencies }
    "build-status" { Get-BuildStatus }
    "download-aab" { Get-LatestAAB }
    default {
        Write-Host "❌ Commande inconnue: $Command" -ForegroundColor Red
        Write-Host "Utiliser: .\dev-helper.ps1 help"
    }
}
