# Script PowerShell pour nettoyer le cache buildozer
Write-Host "=== Nettoyage agressif du cache buildozer ===" -ForegroundColor Cyan

# Supprimer tous les builds existants avec différentes architectures
Write-Host "Suppression des builds multi-architectures..." -ForegroundColor Yellow
Remove-Item -Path ".buildozer\android\platform\build-arm64-v8a_armeabi-v7a" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".buildozer\android\platform\build-armeabi-v7a" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".buildozer\android\platform\build-x86" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".buildozer\android\platform\build-x86_64" -Recurse -Force -ErrorAction SilentlyContinue

# Supprimer tous les dossiers de build
Write-Host "Suppression de tous les dossiers de build..." -ForegroundColor Yellow
Get-ChildItem -Path ".buildozer\android\platform\" -Filter "build-*" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Supprimer le dossier bin
Write-Host "Suppression du dossier bin..." -ForegroundColor Yellow
Remove-Item -Path "bin" -Recurse -Force -ErrorAction SilentlyContinue

# Nettoyer avec buildozer
Write-Host "Nettoyage buildozer..." -ForegroundColor Yellow
try {
    & buildozer android clean
} catch {
    Write-Host "Nettoyage buildozer échoué, on continue..." -ForegroundColor Red
}

# Vérifier la configuration
Write-Host "=== Vérification de la configuration ===" -ForegroundColor Cyan

Write-Host "Architecture configurée dans buildozer.spec:" -ForegroundColor White
try {
    Select-String -Path "buildozer.spec" -Pattern "android.archs"
} catch {
    Write-Host "❌ android.archs non trouvé" -ForegroundColor Red
}

Write-Host "API configurée:" -ForegroundColor White
try {
    Select-String -Path "buildozer.spec" -Pattern "android.api"
} catch {
    Write-Host "❌ android.api non trouvé" -ForegroundColor Red
}

Write-Host "NDK configuré:" -ForegroundColor White
try {
    Select-String -Path "buildozer.spec" -Pattern "android.ndk"
} catch {
    Write-Host "❌ android.ndk non trouvé" -ForegroundColor Red
}

Write-Host "✅ Nettoyage terminé!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant lancer: buildozer android debug" -ForegroundColor Green
