@echo off
echo 🔑 SIGNATURE AAB SIMPLIFIEE POUR GOOGLE PLAY
echo ===============================================

echo 📋 Vérification des fichiers...
if not exist "macartedetarot-release.keystore" (
    echo ❌ Clé de signature non trouvée
    pause
    exit /b 1
)

if not exist "macartedetarot-production.aab" (
    echo ❌ Fichier AAB non trouvé
    pause
    exit /b 1
)

echo ✅ Fichiers détectés

echo 📋 Copie de l'AAB...
copy "macartedetarot-production.aab" "macartedetarot-final.aab"

echo 🔑 Signature avec jarsigner...
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 ^
    -keystore "macartedetarot-release.keystore" ^
    -storepass "BkRbqu&DK6KIYg@r" ^
    -keypass "WdQ#CV^frVQfa#Zd" ^
    "macartedetarot-final.aab" ^
    "macartedetarot"

if %ERRORLEVEL% equ 0 (
    echo ✅ Signature réussie !
    echo 🔍 Vérification...
    jarsigner -verify -verbose "macartedetarot-final.aab"
    if %ERRORLEVEL% equ 0 (
        echo ✅ AAB vérifié avec succès !
        echo 🎯 FICHIER PRÊT : macartedetarot-final.aab
        echo.
        echo 📋 UPLOADEZ CE FICHIER SUR GOOGLE PLAY CONSOLE
    ) else (
        echo ❌ Vérification échouée
    )
) else (
    echo ❌ Signature échouée
)

pause
