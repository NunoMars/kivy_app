# Guide de Test - Rituel Quotidien

## 🧪 Tests à effectuer

### Test 1 : Premier lancement
**Objectif** : Vérifier l'initialisation du système

1. Lancer l'application
2. **Vérifications** :
   - Badge visible : "✨ Votre carte du jour vous attend"
   - Fichier créé : `~/.kivy/app_data/daily_ritual.json`
   - Console : "✅ DailyRitualManager initialisé (streak: 0)"

---

### Test 2 : Flux de tirage complet
**Objectif** : Tester le parcours intention → tirage → révélation

1. Taper sur la carte
2. **Vérifications** :
   - ✅ Transition fade vers IntentionScreen (700ms)
   - ✅ 4 boutons d'intention visibles
   - ✅ Bouton "Recevoir ma guidance" désactivé (grisé)

3. Sélectionner "💕 Amour & Relations"
4. **Vérifications** :
   - ✅ Bouton devient violet
   - ✅ Bouton de validation s'active (vert)

5. Cliquer sur "Recevoir ma guidance"
6. **Vérifications** :
   - ✅ Popup "Chargement..."
   - ✅ Tirage automatique après ~5s
   - ✅ Transition fade vers ResponseScreen (800ms)
   - ✅ Message de la carte contient "💕 Dans le domaine de l'amour..."

7. Revenir à l'écran principal
8. **Vérifications** :
   - ✅ Badge change : "✨ Jour 1 de guidance" (en vert)
   - ✅ Fichier `daily_ritual.json` mis à jour avec streak=1

---

### Test 3 : Verrouillage du tirage unique
**Objectif** : Vérifier qu'on ne peut pas tirer deux fois

1. Après avoir tiré une carte aujourd'hui
2. Taper à nouveau sur la carte
3. **Vérifications** :
   - ✅ Popup immédiat (pas d'écran d'intention)
   - ✅ Message : "Vous avez déjà tiré votre carte aujourd'hui"
   - ✅ Affichage du streak : "🔥 1 jour consécutif"
   - ✅ Bouton "D'accord" pour fermer

---

### Test 4 : Question personnalisée
**Objectif** : Tester l'intention "Question libre"

1. Supprimer `daily_ritual.json` pour réinitialiser
2. Lancer l'app, taper sur la carte
3. Sélectionner "✍️ Question personnelle"
4. **Vérifications** :
   - ✅ Champ texte apparaît (fade in)
   - ✅ Placeholder : "Formulez votre question..."

5. Taper "Vais-je réussir mon examen ?"
6. Valider
7. **Vérifications** :
   - ✅ Message de la carte contient : "Concernant votre question : 'Vais-je réussir mon examen ?'"

---

### Test 5 : Streak consécutif
**Objectif** : Vérifier le compteur de jours

1. **Simuler plusieurs jours** en modifiant `daily_ritual.json` :

```json
{
  "last_draw_date": "2026-01-25",
  "current_streak": 3,
  "best_streak": 3,
  "total_draws": 3,
  "draw_completed": false
}
```

2. Relancer l'app
3. Effectuer un tirage
4. **Vérifications** :
   - ✅ Streak passe à 4
   - ✅ Badge : "✨ Jour 4 de guidance"

---

### Test 6 : Streak cassé
**Objectif** : Vérifier la réinitialisation si jour manqué

1. Modifier `daily_ritual.json` :

```json
{
  "last_draw_date": "2026-01-24",
  "current_streak": 5,
  "best_streak": 5,
  "total_draws": 10,
  "draw_completed": true
}
```

2. Relancer l'app (date actuelle : 26/01)
3. **Vérifications** :
   - ✅ Console : "📉 Streak réinitialisé (dernier tirage: 2026-01-24)"
   - ✅ `current_streak` = 0 dans le JSON
   - ✅ Badge : "✨ Votre carte du jour vous attend"

4. Effectuer un nouveau tirage
5. **Vérifications** :
   - ✅ Streak repart à 1
   - ✅ `best_streak` reste à 5 (conservé)

---

### Test 7 : Notifications (Android uniquement)
**Objectif** : Tester les notifications à 11h

1. **Simuler heure < 11h** en modifiant l'heure système ou en testant avant 11h
2. Lancer l'app puis la fermer (pas de tirage)
3. Attendre 11h
4. **Vérifications** :
   - ✅ Notification reçue : "Une carte vous attend aujourd'hui ✨"
   - ✅ Tap sur la notification ouvre l'app

5. Relancer l'app manuellement
6. Attendre quelques minutes
7. **Vérifications** :
   - ✅ **Aucune** seconde notification (limite 1/jour)

---

### Test 8 : Traductions
**Objectif** : Vérifier les traductions en/es/pt

1. Modifier la langue système ou forcer via config
2. Lancer l'app
3. **Vérifier dans chaque langue** :
   - ✅ Badge principal traduit
   - ✅ Écran d'intention traduit
   - ✅ Boutons d'intention traduits
   - ✅ Messages de personnalisation traduits

**Langues à tester** :
- Français (par défaut)
- Anglais
- Espagnol
- Portugais

---

### Test 9 : Animations
**Objectif** : Vérifier la fluidité

1. Effectuer un tirage complet
2. **Observer** :
   - ✅ Transition CardScreen → IntentionScreen : lente, fluide (~700ms)
   - ✅ Transition IntentionScreen → ResponseScreen : lente, fluide (~800ms)
   - ✅ Pas de clignotement
   - ✅ Ambiance calme et contemplative

---

### Test 10 : Persistance après redémarrage
**Objectif** : Vérifier que les données survivent

1. Effectuer un tirage (streak = 1)
2. **Fermer complètement l'app**
3. **Relancer**
4. **Vérifications** :
   - ✅ Badge affiche toujours "Jour 1 de guidance"
   - ✅ Impossible de tirer à nouveau
   - ✅ Fichier JSON intact

---

## 🛠️ Outils de débogage

### Afficher le contenu de daily_ritual.json
```bash
cat ~/.kivy/app_data/daily_ritual.json | python3 -m json.tool
```

### Réinitialiser complètement
```bash
rm ~/.kivy/app_data/daily_ritual.json
```

### Simuler un jour spécifique
Modifier manuellement `last_draw_date` dans le JSON :
```json
{
  "last_draw_date": "2026-01-20",
  ...
}
```

### Logs à surveiller
- `✅ DailyRitualManager initialisé (streak: X)`
- `📉 Streak réinitialisé (dernier tirage: ...)`
- `IntentionScreen: intention enregistrée - love/work/inner/custom`
- `CardScreen: tirage enregistré - major_XX`
- `🔔 Notification tirage envoyée`

---

## ✅ Checklist finale

Avant validation en production :

- [ ] Tous les tests ci-dessus passent
- [ ] Aucune régression sur les fonctionnalités existantes
- [ ] AdMob fonctionne toujours (interstitielles après tirage)
- [ ] Pas de crash au premier lancement
- [ ] Traductions complètes pour les 4 langues principales
- [ ] Badge visible et mis à jour correctement
- [ ] Animations fluides sur tous les appareils testés
- [ ] Notifications ne spam pas (max 1/jour)
- [ ] Fichier JSON créé et persistant
- [ ] Streak calculé correctement
- [ ] Messages personnalisés selon l'intention

---

## 🐛 Problèmes connus potentiels

### Problème : Badge ne s'affiche pas
**Solution** : Vérifier que `_update_daily_badge()` est bien appelé dans `on_enter()`

### Problème : Streak ne se réinitialise pas
**Solution** : Vérifier que `reset_today_if_needed()` est appelé dans `TarotApp.__init__()`

### Problème : Transitions saccadées
**Solution** : Tester sur appareil réel (pas émulateur). Réduire durée à 500ms si nécessaire.

### Problème : Notifications non reçues
**Solution** : Vérifier permissions Android 13+ (POST_NOTIFICATIONS)

---

*Document de test créé le 26 janvier 2026*
