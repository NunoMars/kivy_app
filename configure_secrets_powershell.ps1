# Script PowerShell pour configurer les secrets GitHub après résolution du problème de keystore

Write-Host "🔮 Configuration des secrets GitHub pour Ma Carte de Tarot" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Vérifier les prérequis
Write-Host "🔍 Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier GitHub CLI
try {
    $ghVersion = & gh --version
    Write-Host "✅ GitHub CLI installé: $($ghVersion[0])" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub CLI n'est pas installé. Installez-le depuis https://cli.github.com/" -ForegroundColor Red
    exit 1
}

# Vérifier l'authentification
try {
    & gh auth status | Out-Null
    Write-Host "✅ Authentification GitHub OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Vous n'êtes pas connecté à GitHub. Exécutez 'gh auth login'" -ForegroundColor Red
    exit 1
}

# Vérifier que nous sommes dans un repo git
try {
    & git status | Out-Null
    Write-Host "✅ Repository Git détecté" -ForegroundColor Green
} catch {
    Write-Host "❌ Vous n'êtes pas dans un repository Git" -ForegroundColor Red
    exit 1
}

# Vérifier l'existence du keystore
if (-not (Test-Path "googleplay.keystore")) {
    Write-Host "❌ Le fichier 'googleplay.keystore' n'existe pas" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Keystore trouvé" -ForegroundColor Green

# Encoder le keystore en base64
Write-Host "🔐 Encodage du keystore..." -ForegroundColor Yellow
$keystoreBytes = [System.IO.File]::ReadAllBytes("googleplay.keystore")
$keystoreBase64 = [System.Convert]::ToBase64String($keystoreBytes)
$keystoreBase64 | Out-File -FilePath "keystore_base64.txt" -Encoding ASCII
Write-Host "✅ Keystore encodé et sauvegardé dans 'keystore_base64.txt'" -ForegroundColor Green

# Demander les informations de signature
Write-Host "🔐 Configuration des secrets de signature..." -ForegroundColor Yellow
Write-Host "Vous devez fournir les informations suivantes :" -ForegroundColor White

$keystorePassword = Read-Host "🔐 Mot de passe du keystore"
if ([string]::IsNullOrEmpty($keystorePassword)) {
    Write-Host "❌ Le mot de passe du keystore est requis" -ForegroundColor Red
    exit 1
}

# Tester le mot de passe
Write-Host "🔍 Test du mot de passe..." -ForegroundColor Yellow
try {
    $testResult = & keytool -list -keystore "googleplay.keystore" -storepass $keystorePassword -v 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Mot de passe correct" -ForegroundColor Green
        
        # Extraire les aliases
        $aliases = $testResult | Where-Object { $_ -match "Alias name:" } | ForEach-Object { 
            ($_ -split "Alias name:")[1].Trim() 
        }
        
        if ($aliases) {
            Write-Host "🔑 Aliases trouvés: $($aliases -join ', ')" -ForegroundColor Green
            $defaultAlias = $aliases[0]
        } else {
            Write-Host "⚠️ Aucun alias trouvé, utilisation de 'upload' par défaut" -ForegroundColor Yellow
            $defaultAlias = "upload"
        }
    } else {
        Write-Host "❌ Mot de passe incorrect" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors du test du mot de passe: $_" -ForegroundColor Red
    exit 1
}

$keyAlias = Read-Host "🔑 Alias de la clé (par défaut '$defaultAlias')"
if ([string]::IsNullOrEmpty($keyAlias)) {
    $keyAlias = $defaultAlias
}

$keyPassword = Read-Host "🔐 Mot de passe de la clé (Entrée pour utiliser le même que le keystore)"
if ([string]::IsNullOrEmpty($keyPassword)) {
    $keyPassword = $keystorePassword
}

# Configurer les secrets
Write-Host "🚀 Configuration des secrets GitHub..." -ForegroundColor Yellow

$secrets = @(
    @{Name="ANDROID_KEYSTORE"; Value=$keystoreBase64},
    @{Name="ANDROID_KEYSTORE_PASSWORD"; Value=$keystorePassword},
    @{Name="ANDROID_KEY_ALIAS"; Value=$keyAlias},
    @{Name="ANDROID_KEY_PASSWORD"; Value=$keyPassword}
)

foreach ($secret in $secrets) {
    try {
        & gh secret set $secret.Name --body $secret.Value
        Write-Host "✅ Secret $($secret.Name) configuré" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur lors de la configuration du secret $($secret.Name): $_" -ForegroundColor Red
        exit 1
    }
}

# Vérifier les secrets configurés
Write-Host "🔍 Vérification des secrets configurés..." -ForegroundColor Yellow
& gh secret list

# Créer un nouveau tag
Write-Host "🏷️ Création d'un nouveau tag..." -ForegroundColor Yellow
$tagName = "v1.3.1"

# Supprimer le tag s'il existe
try {
    & git tag -d $tagName 2>$null
    & git push origin ":refs/tags/$tagName" 2>$null
} catch {
    # Ignorer les erreurs si le tag n'existe pas
}

# Créer et pousser le nouveau tag
try {
    & git tag $tagName
    & git push origin $tagName
    Write-Host "✅ Tag $tagName créé et poussé" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de la création du tag: $_" -ForegroundColor Red
    exit 1
}

Write-Host "🎯 SUCCÈS! Configuration terminée" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Le pipeline va se déclencher automatiquement avec le tag $tagName" -ForegroundColor White
Write-Host "Surveillez l'exécution sur GitHub Actions" -ForegroundColor White

Write-Host "🔗 Liens utiles:" -ForegroundColor Yellow
Write-Host "   - GitHub Actions: https://github.com/your-repo/actions" -ForegroundColor White
Write-Host "   - Google Play Console: https://play.google.com/console/" -ForegroundColor White

Write-Host "🔮 Votre app de tarot sera bientôt prête pour la production! ✨" -ForegroundColor Magenta
