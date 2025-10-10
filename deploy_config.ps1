# Script PowerShell pour déployer config.json sur Android
# Usage: .\deploy_config.ps1 [test|prod]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('test','prod')]
    [string]$Mode = 'test'
)

$APP_PACKAGE = "org.tarot.macartedetarot"
$CONFIG_FILE = "config.json"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  AdMob Config Deployer" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que ADB est disponible
try {
    $null = adb version
} catch {
    Write-Host "❌ Erreur: ADB non trouvé dans PATH" -ForegroundColor Red
    Write-Host "   Installe Android SDK Platform Tools" -ForegroundColor Yellow
    exit 1
}

# Vérifier qu'un appareil est connecté
$devices = adb devices | Select-String "device$"
if ($devices.Count -eq 0) {
    Write-Host "❌ Aucun appareil Android connecté" -ForegroundColor Red
    Write-Host "   Connecte un appareil via USB et active le débogage USB" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Appareil détecté" -ForegroundColor Green

# Créer config.json selon le mode
if ($Mode -eq 'test') {
    Write-Host "📝 Création config.json (MODE TEST)..." -ForegroundColor Yellow
    $config = @{
        ads_enabled = $true
        ads_test_mode = $true
        admob_app_id = "ca-app-pub-3940256099942544~3347511713"
        admob_banner_id = "ca-app-pub-3940256099942544/6300978111"
        admob_interstitial_id = "ca-app-pub-3940256099942544/1033173712"
        ads_frequency = 3
        banner_position = "bottom"
        banner_enabled = $true
        interstitial_enabled = $true
        remote_config_url = ""
    }
} else {
    Write-Host "📝 Utilisation de config.production.json..." -ForegroundColor Yellow
    
    # Vérifier si config.production.json existe
    if (Test-Path "config.production.json") {
        $config = Get-Content "config.production.json" -Raw | ConvertFrom-Json
        Write-Host "✅ Config production chargée depuis config.production.json" -ForegroundColor Green
    } else {
        Write-Host "⚠️  config.production.json non trouvé, demande interactive..." -ForegroundColor Yellow
        
        # Demander les IDs AdMob
        Write-Host ""
        Write-Host "Entre tes IDs AdMob (depuis https://apps.admob.com/):" -ForegroundColor Cyan
        Write-Host ""
        
        $appId = Read-Host "AdMob App ID (ca-app-pub-5749803259882370~1482612480)"
        if ([string]::IsNullOrWhiteSpace($appId)) {
            $appId = "ca-app-pub-5749803259882370~1482612480"
        }
        
        $bannerId = Read-Host "Banner ID (ca-app-pub-5749803259882370/8646786637)"
        if ([string]::IsNullOrWhiteSpace($bannerId)) {
            $bannerId = "ca-app-pub-5749803259882370/8646786637"
        }
        
        $interstitialId = Read-Host "Interstitial ID (ou Enter pour IDs Google de test)"
        if ([string]::IsNullOrWhiteSpace($interstitialId)) {
            $interstitialId = "ca-app-pub-3940256099942544/1033173712"
            Write-Host "ℹ️  Utilisation IDs Google de test pour interstitielle" -ForegroundColor Cyan
        }
        
        Write-Host ""
        $frequency = Read-Host "Fréquence des pubs (nombre de tirages entre chaque pub, ex: 5)"
        if ([string]::IsNullOrWhiteSpace($frequency)) {
            $frequency = 5
        }
        
        $config = @{
            ads_enabled = $true
            ads_test_mode = $false
            admob_app_id = $appId
            admob_banner_id = $bannerId
            admob_interstitial_id = $interstitialId
            ads_frequency = [int]$frequency
            banner_position = "bottom"
            banner_enabled = $true
            interstitial_enabled = $false
            remote_config_url = ""
        }
    }
}

# Convertir en JSON
$json = $config | ConvertTo-Json -Depth 10

# Sauvegarder localement
$json | Out-File -FilePath $CONFIG_FILE -Encoding utf8
Write-Host "✅ Fichier $CONFIG_FILE créé localement" -ForegroundColor Green

# Afficher le contenu
Write-Host ""
Write-Host "📋 Contenu de config.json:" -ForegroundColor Cyan
Get-Content $CONFIG_FILE | Write-Host -ForegroundColor White
Write-Host ""

# Demander confirmation
$confirmation = Read-Host "Déployer sur l'appareil ? (O/N)"
if ($confirmation -ne 'O' -and $confirmation -ne 'o') {
    Write-Host "❌ Déploiement annulé" -ForegroundColor Yellow
    exit 0
}

# Pousser sur Android
Write-Host ""
Write-Host "📱 Déploiement sur Android..." -ForegroundColor Yellow

# Étape 1: Pousser sur /sdcard/
Write-Host "   1/4 Push vers /sdcard/..." -ForegroundColor Gray
adb push $CONFIG_FILE /sdcard/$CONFIG_FILE 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du push" -ForegroundColor Red
    exit 1
}

# Étape 2: Copier dans le dossier de l'app
Write-Host "   2/4 Copie dans /data/data/$APP_PACKAGE/files/..." -ForegroundColor Gray
adb shell "run-as $APP_PACKAGE cp /sdcard/$CONFIG_FILE /data/data/$APP_PACKAGE/files/$CONFIG_FILE" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la copie (app installée ?)" -ForegroundColor Red
    exit 1
}

# Étape 3: Nettoyer /sdcard/
Write-Host "   3/4 Nettoyage /sdcard/..." -ForegroundColor Gray
adb shell "rm /sdcard/$CONFIG_FILE" 2>&1 | Out-Null

# Étape 4: Vérifier
Write-Host "   4/4 Vérification..." -ForegroundColor Gray
$deployed = adb shell "run-as $APP_PACKAGE cat /data/data/$APP_PACKAGE/files/$CONFIG_FILE"
if ($deployed) {
    Write-Host "✅ Config déployée avec succès !" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur: Config non trouvée sur l'appareil" -ForegroundColor Red
    exit 1
}

# Redémarrer l'app
Write-Host ""
$restart = Read-Host "Redémarrer l'app pour appliquer la config ? (O/N)"
if ($restart -eq 'O' -or $restart -eq 'o') {
    Write-Host "🔄 Redémarrage de l'app..." -ForegroundColor Yellow
    adb shell "am force-stop $APP_PACKAGE" 2>&1 | Out-Null
    Start-Sleep -Seconds 1
    adb shell "am start -n $APP_PACKAGE/.MainActivity" 2>&1 | Out-Null
    Write-Host "✅ App redémarrée" -ForegroundColor Green
    
    # Afficher les logs
    Write-Host ""
    Write-Host "📊 Logs AdMob (appuie CTRL+C pour quitter):" -ForegroundColor Cyan
    Write-Host ""
    adb logcat -s "AdMob:* TarotApp:* Python:*"
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ✅ Déploiement terminé" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
