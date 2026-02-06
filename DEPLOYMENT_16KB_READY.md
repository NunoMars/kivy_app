# 🚀 AAB Prêt pour Déploiement - Support 16KB

**Date de signature**: 6 février 2026  
**Fichier final**: `bin/macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab`  
**Statut**: ✅ **PRÊT POUR GOOGLE PLAY STORE**

## Caractéristiques de l'AAB

- **Nom**: macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab
- **Taille**: 58 MB
- **Version**: 2.41 (versionCode: 2941000)
- **Architecture**: arm64-v8a uniquement
- **Signé avec**: CN=Marcelino Nuno (keystore: upload)
- **Alignement pages**: 16KB (0x4000) ✅
- **Min SDK**: 21 (Android 5.0)
- **Target SDK**: 35 (Android 15)

## Vérification 16KB

Toutes les bibliothèques natives critiques ont un alignement de 16KB :

```
✅ libpython3.11.so: 0x4000
✅ libSDL2.so: 0x4000
✅ libffi.so: 0x4000
✅ libcrypto1.1.so: 0x4000
✅ libssl1.1.so: 0x4000
✅ libsqlite3.so: 0x4000
```

## Étapes de déploiement

### 1. Upload sur Google Play Console

```bash
# Le fichier est prêt à être uploadé :
/home/loupy/kivy_app/bin/macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab
```

**Accès Console**: https://play.google.com/console

**Navigation**:
1. Ouvrir Google Play Console
2. Sélectionner "Ma Carte De Tarot" (org.tarot.macartedetarot)
3. Aller dans "Production" → "Versions"
4. Créer une nouvelle version
5. Uploader `macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab`

### 2. Tests recommandés avant production

#### Test sur appareil 16KB (si disponible)
- Appareil avec Android 15+ et pages 16KB activées
- Vérifier le lancement de l'application
- Tester les fonctionnalités principales

#### Pre-launch reports
- Google Play génère automatiquement des tests
- Vérifier les résultats avant publication complète
- Chercher les crashs liés aux bibliothèques natives

### 3. Notes de version (Changelog)

Suggéré pour v2.41 :
```
🔧 Mise à jour technique importante
- Support natif pour les appareils Android 15+ avec pages mémoire 16KB
- Optimisation des performances sur les nouveaux appareils
- Améliorations de stabilité
```

### 4. Déploiement progressif recommandé

Pour minimiser les risques :
- **Phase 1**: 5% des utilisateurs pendant 2-3 jours
- **Phase 2**: 20% des utilisateurs pendant 2-3 jours
- **Phase 3**: 50% des utilisateurs pendant 2 jours
- **Phase 4**: 100% des utilisateurs

**Surveiller** :
- Taux de crash (devrait rester stable ou diminuer)
- Avis utilisateurs
- Rapports ANR (Application Not Responding)

## Compatibilité

### Appareils supportés
✅ **Android 5.0 - 15+** (API 21-35)  
✅ **Architecture arm64-v8a uniquement**  
✅ **Pages mémoire 4KB** (appareils existants)  
✅ **Pages mémoire 16KB** (nouveaux appareils Android 15+)

### Tests effectués
- ✅ Build réussi sans erreurs
- ✅ Vérification alignment avec `readelf`
- ✅ Signature vérifiée avec `jarsigner`
- ✅ Toutes les bibliothèques natives à 0x4000

## Commandes de vérification

### Vérifier la signature
```bash
jarsigner -verify -verbose bin/macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab
```

### Vérifier l'alignement 16KB
```bash
mkdir -p /tmp/check && cd /tmp/check
unzip -q ~/kivy_app/bin/macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab

# Vérifier toutes les bibliothèques
for lib in base/lib/arm64-v8a/*.so; do
  echo "$(basename $lib): $(readelf -lW $lib | grep 'LOAD.*R' | head -1 | awk '{print $NF}')"
done
```

### Rebuild si nécessaire
```bash
cd /home/loupy/kivy_app
./rebuild_16kb.sh

# Re-signer
jarsigner -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore googleplay.keystore -storepass nunotheboss \
  bin/macartedetarot-2.41-arm64-v8a-release.aab upload

mv bin/macartedetarot-2.41-arm64-v8a-release.aab \
   bin/macartedetarot-2.41-arm64-v8a-release-16KB-signed.aab
```

## Exigences Google Play (16KB)

### Obligatoire à partir de
- **Août 2025**: Nouvelles applications et mises à jour pour arm64-v8a
- **Février 2026**: Toutes les applications arm64-v8a existantes

### Notre conformité
✅ Alignement 16KB implémenté  
✅ Testé et vérifié  
✅ Prêt avant la deadline obligatoire

## Backup et historique

### Versions précédentes
Les AABs précédents sont conservés dans `/home/loupy/kivy_app/bin/`:
- macartedetarot-2.39-arm64-v8a-release-signed.aab (dernière production 4KB)
- macartedetarot-2.41-arm64-v8a-release.aab (16KB non signé)

### Configuration sauvegardée
Toutes les modifications pour le support 16KB sont documentées dans :
- [SOLUTION_16KB_ALIGNMENT.md](SOLUTION_16KB_ALIGNMENT.md) - Documentation technique complète
- [rebuild_16kb.sh](rebuild_16kb.sh) - Script de build avec flags 16KB
- [p4a_recipes/](p4a_recipes/) - Recettes customisées pour chaque bibliothèque
- [p4a_hooks/manifest_receivers.py](p4a_hooks/manifest_receivers.py) - Hooks de build

## Rollback si problème

En cas de problème critique après déploiement :

1. **Google Play Console** → Suspendre le déploiement
2. **Revenir à v2.39** (dernière version stable 4KB)
3. **Analyser les logs** de crash
4. **Corriger et re-tester** avant réessayer

## Support technique

### Documentation de référence
- [Google: 16KB Page Sizes](https://developer.android.com/guide/practices/page-sizes)
- [Python-for-Android: Custom Recipes](https://python-for-android.readthedocs.io/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

### Contacts
- **Développeur**: loupy@kivy_app
- **Build system**: Buildozer 1.5.0 + python-for-android
- **NDK**: r26c
- **Date création**: 6 février 2026

---

## ✅ Checklist finale avant upload

- [x] AAB signé avec le bon keystore
- [x] Signature vérifiée (`jar verified`)
- [x] Alignement 16KB vérifié pour toutes les bibliothèques
- [x] Version incrémentée (2.41 / 2941000)
- [x] Taille AAB raisonnable (58MB)
- [x] Target SDK = 35 (requis)
- [x] Architecture arm64-v8a
- [ ] Notes de version rédigées (à compléter dans Console)
- [ ] Screenshots mis à jour si nécessaire
- [ ] Tests manuels effectués (recommandé)
- [ ] Upload sur Google Play Console
- [ ] Déploiement progressif configuré

---

**🎉 AAB prêt pour production ! Bon déploiement !**
