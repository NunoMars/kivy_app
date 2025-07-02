# Script PowerShell pour créer une clé de signature Android de production
# Usage: .\create_signing_key.ps1

param(
    [string]$KeystoreFile = "release.keystore",
    [string]$KeyAlias = "release",
    [int]$ValidityDays = 10000
)

Write-Host "🔐 Création de la clé de signature Android pour Ma Carte de Tarot" -ForegroundColor Cyan
Write-Host ""

# Vérifications préliminaires
try {
    $null = Get-Command keytool -ErrorAction Stop
    Write-Host "✅ Java keytool trouvé" -ForegroundColor Green
} catch {
    Write-Host "❌ keytool n'est pas installé. Installez Java JDK." -ForegroundColor Red
    Write-Host "Téléchargez Java depuis: https://adoptium.net/" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Informations de la clé :" -ForegroundColor Yellow
Write-Host "   Fichier keystore : $KeystoreFile"
Write-Host "   Alias de la clé  : $KeyAlias"
Write-Host "   Validité         : $ValidityDays jours"
Write-Host ""

# Vérifier si la clé existe déjà
if (Test-Path $KeystoreFile) {
    Write-Host "⚠️  Le fichier $KeystoreFile existe déjà !" -ForegroundColor Yellow
    $replace = Read-Host "Voulez-vous le remplacer ? (y/N)"
    if ($replace -notmatch '^[Yy]$') {
        Write-Host "❌ Annulé par l'utilisateur" -ForegroundColor Red
        exit 1
    }
    Remove-Item $KeystoreFile -Force
}

Write-Host "🔨 Génération de la clé de signature..." -ForegroundColor Green
Write-Host "   Vous allez devoir saisir des informations personnelles et un mot de passe." -ForegroundColor Yellow
Write-Host "   IMPORTANT: Notez bien le mot de passe, vous en aurez besoin pour les secrets GitHub !" -ForegroundColor Red
Write-Host ""

# Génération de la clé
$keyToolArgs = @(
    "-genkey", "-v",
    "-keystore", $KeystoreFile,
    "-alias", $KeyAlias,
    "-keyalg", "RSA",
    "-keysize", "2048",
    "-validity", $ValidityDays
)

try {
    & keytool @keyToolArgs
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "❌ Erreur lors de l'exécution de keytool: $_" -ForegroundColor Red
    exit 1
}

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ Clé de signature créée avec succès !" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Fichier généré : $KeystoreFile" -ForegroundColor Cyan
    Write-Host "🔑 Alias de la clé : $KeyAlias" -ForegroundColor Cyan
    Write-Host ""
    
    # Afficher les infos de la clé
    Write-Host "ℹ️  Informations de la clé :" -ForegroundColor Yellow
    & keytool -list -v -keystore $KeystoreFile -alias $KeyAlias
    
    Write-Host ""
    Write-Host "🔒 Configuration des secrets GitHub :" -ForegroundColor Magenta
    
    # Encoder en base64 pour GitHub (Windows)
    try {
        $keystoreBytes = [System.IO.File]::ReadAllBytes((Get-Item $KeystoreFile).FullName)
        $keystoreBase64 = [System.Convert]::ToBase64String($keystoreBytes)
        
        Write-Host "   1. ANDROID_KEYSTORE        : $keystoreBase64" -ForegroundColor White
        Write-Host "   2. ANDROID_KEYSTORE_PASSWORD: [mot de passe du keystore saisi]" -ForegroundColor White
        Write-Host "   3. ANDROID_KEY_ALIAS       : $KeyAlias" -ForegroundColor White
        Write-Host "   4. ANDROID_KEY_PASSWORD    : [mot de passe de la clé saisi]" -ForegroundColor White
    } catch {
        Write-Host "   ⚠️  Erreur encodage base64: $_" -ForegroundColor Yellow
        Write-Host "   Utilisez: [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('$KeystoreFile'))" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "📖 Voir SECRETS_SETUP.md pour la configuration complète" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  IMPORTANT :" -ForegroundColor Red
    Write-Host "   - Sauvegardez cette clé en lieu sûr" -ForegroundColor Yellow
    Write-Host "   - Ne la commitez JAMAIS dans Git" -ForegroundColor Yellow
    Write-Host "   - Utilisez la même clé pour toutes les versions de l'app" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "❌ Erreur lors de la création de la clé (code: $exitCode)" -ForegroundColor Red
    exit 1
}
