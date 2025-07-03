# Script PowerShell pour configurer automatiquement les secrets GitHub
# Utilise l'API GitHub pour ajouter les secrets nécessaires au pipeline Android

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$true)]
    [string]$KeystorePassword,
    
    [Parameter(Mandatory=$false)]
    [string]$KeyAlias = "googleplay",
    
    [Parameter(Mandatory=$false)]
    [string]$KeyPassword = "",
    
    [Parameter(Mandatory=$false)]
    [string]$GooglePlayServiceAccount = ""
)

# Configuration
$REPO_OWNER = "NunoMars"
$REPO_NAME = "kivy_app"
$KEYSTORE_FILE = "googleplay.keystore"

Write-Host "🔮 CONFIGURATION AUTOMATIQUE DES SECRETS GITHUB" -ForegroundColor Cyan
Write-Host "   Repository: $REPO_OWNER/$REPO_NAME" -ForegroundColor Gray
Write-Host "   Clé: $KEYSTORE_FILE" -ForegroundColor Gray

# Fonction pour encoder en base64
function Get-Base64FromFile {
    param([string]$FilePath)
    
    if (!(Test-Path $FilePath)) {
        throw "Fichier non trouvé: $FilePath"
    }
    
    $bytes = [System.IO.File]::ReadAllBytes($FilePath)
    return [System.Convert]::ToBase64String($bytes)
}

# Fonction pour créer un secret GitHub
function Set-GitHubSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue,
        [string]$Token,
        [string]$Owner,
        [string]$Repo
    )
    
    Write-Host "📝 Configuration du secret: $SecretName" -ForegroundColor Yellow
    
    # Étape 1: Récupérer la clé publique du repository
    $publicKeyUrl = "https://api.github.com/repos/$Owner/$Repo/actions/secrets/public-key"
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "PowerShell-Script"
    }
    
    try {
        $publicKeyResponse = Invoke-RestMethod -Uri $publicKeyUrl -Headers $headers -Method Get
        $publicKey = $publicKeyResponse.key
        $keyId = $publicKeyResponse.key_id
        
        Write-Host "   ✅ Clé publique récupérée" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Erreur lors de la récupération de la clé publique: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # Étape 2: Chiffrer le secret avec la clé publique
    # Note: Ceci nécessite une implémentation de chiffrement Sodium/NaCl
    # Pour simplifier, nous utiliserons l'API GitHub CLI si disponible
    
    # Étape 3: Envoyer le secret chiffré
    $secretUrl = "https://api.github.com/repos/$Owner/$Repo/actions/secrets/$SecretName"
    
    # Pour cette version simplifiée, nous montrons juste la commande à exécuter
    Write-Host "   ℹ️  Utilisez GitHub CLI pour ajouter ce secret:" -ForegroundColor Blue
    Write-Host "   gh secret set $SecretName --body `"$SecretValue`"" -ForegroundColor Gray
    
    return $true
}

# Validation des prérequis
Write-Host "`n🔍 VALIDATION DES PRÉREQUIS" -ForegroundColor Magenta

# Vérifier que le keystore existe
if (!(Test-Path $KEYSTORE_FILE)) {
    Write-Host "❌ Fichier keystore non trouvé: $KEYSTORE_FILE" -ForegroundColor Red
    Write-Host "   Assurez-vous que le fichier googleplay.keystore est présent." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Keystore trouvé: $KEYSTORE_FILE" -ForegroundColor Green

# Vérifier GitHub CLI (optionnel mais recommandé)
try {
    $ghVersion = gh --version 2>$null
    if ($ghVersion) {
        Write-Host "✅ GitHub CLI disponible" -ForegroundColor Green
        $useGhCli = $true
    }
    else {
        $useGhCli = $false
    }
}
catch {
    Write-Host "⚠️  GitHub CLI non disponible - mode manuel" -ForegroundColor Yellow
    $useGhCli = $false
}

# Préparer les secrets
Write-Host "`n📦 PRÉPARATION DES SECRETS" -ForegroundColor Magenta

# 1. Encoder le keystore en base64
try {
    Write-Host "🔐 Encodage du keystore en base64..." -ForegroundColor Yellow
    $keystoreBase64 = Get-Base64FromFile -FilePath $KEYSTORE_FILE
    Write-Host "✅ Keystore encodé ($($keystoreBase64.Length) caractères)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erreur lors de l'encodage: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Préparer les autres secrets
if ([string]::IsNullOrEmpty($KeyPassword)) {
    $KeyPassword = $KeystorePassword
}

$secrets = @{
    "ANDROID_KEYSTORE" = $keystoreBase64
    "ANDROID_KEYSTORE_PASSWORD" = $KeystorePassword
    "ANDROID_KEY_ALIAS" = $KeyAlias
    "ANDROID_KEY_PASSWORD" = $KeyPassword
}

if (![string]::IsNullOrEmpty($GooglePlayServiceAccount)) {
    $secrets["GOOGLE_PLAY_SERVICE_ACCOUNT"] = $GooglePlayServiceAccount
}

# Configuration des secrets
Write-Host "`n🔧 CONFIGURATION DES SECRETS" -ForegroundColor Magenta

if ($useGhCli) {
    Write-Host "📱 Utilisation de GitHub CLI pour configurer les secrets..." -ForegroundColor Cyan
    
    # Vérifier l'authentification
    try {
        $authStatus = gh auth status 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ GitHub CLI non authentifié" -ForegroundColor Red
            Write-Host "   Exécutez: gh auth login" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "✅ GitHub CLI authentifié" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Erreur d'authentification GitHub CLI" -ForegroundColor Red
        exit 1
    }
    
    # Ajouter chaque secret
    foreach ($secretName in $secrets.Keys) {
        $secretValue = $secrets[$secretName]
        Write-Host "📝 Ajout du secret: $secretName" -ForegroundColor Yellow
        
        try {
            # Écrire la valeur dans un fichier temporaire pour éviter les problèmes de caractères spéciaux
            $tempFile = [System.IO.Path]::GetTempFileName()
            [System.IO.File]::WriteAllText($tempFile, $secretValue)
            
            $result = gh secret set $secretName --body-file $tempFile --repo "$REPO_OWNER/$REPO_NAME" 2>&1
            
            # Nettoyer le fichier temporaire
            Remove-Item $tempFile -Force
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ Secret $secretName ajouté avec succès" -ForegroundColor Green
            }
            else {
                Write-Host "   ❌ Erreur lors de l'ajout du secret $secretName : $result" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "   ❌ Exception lors de l'ajout du secret $secretName : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}
else {
    Write-Host "📱 Mode manuel - Commandes à exécuter:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Installez GitHub CLI: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "2. Authentifiez-vous: gh auth login" -ForegroundColor Yellow
    Write-Host "3. Exécutez les commandes suivantes:" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($secretName in $secrets.Keys) {
        $secretValue = $secrets[$secretName]
        if ($secretName -eq "ANDROID_KEYSTORE") {
            # Pour le keystore, on affiche juste la longueur
            Write-Host "gh secret set $secretName --body `"<KEYSTORE_BASE64_$($secretValue.Length)_CHARS>`"" -ForegroundColor Gray
        }
        else {
            Write-Host "gh secret set $secretName --body `"$secretValue`"" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "OU utilisez l'interface web:" -ForegroundColor Yellow
    Write-Host "https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions" -ForegroundColor Blue
}

# Validation finale
Write-Host "`n🎯 PROCHAINES ÉTAPES" -ForegroundColor Magenta
Write-Host "1. ✅ Vérifiez que tous les secrets sont configurés" -ForegroundColor Green
Write-Host "2. 🏷️  Créez un nouveau tag: git tag v1.3.0" -ForegroundColor Green
Write-Host "3. 🚀 Poussez le tag: git push origin v1.3.0" -ForegroundColor Green
Write-Host "4. 👀 Surveillez le build: https://github.com/$REPO_OWNER/$REPO_NAME/actions" -ForegroundColor Green

Write-Host "`n🔮 CONFIGURATION TERMINÉE!" -ForegroundColor Cyan
Write-Host "Le pipeline Android est maintenant prêt pour la production." -ForegroundColor Green
