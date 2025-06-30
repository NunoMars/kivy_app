# Guide d'installation Android Studio et émulateur

## 1. Télécharger Android Studio
- Aller sur https://developer.android.com/studio
- Télécharger et installer Android Studio

## 2. Créer un émulateur Android
- Ouvrir Android Studio
- Aller dans Tools > AVD Manager
- Créer un nouvel appareil virtuel (ex: Pixel 6, API 30+)

## 3. Démarrer l'émulateur
- Lancer l'émulateur depuis AVD Manager
- Attendre que Android démarre complètement

## 4. Transférer et installer l'APK
# Une fois que vous avez l'APK compilé:
adb install bin/macartedetarot-0.1-debug.apk

## 5. Alternative: Compilation directe
# Si buildozer fonctionne sur Windows:
buildozer android debug
buildozer android deploy run
