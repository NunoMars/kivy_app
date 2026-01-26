# Architecture du Rituel Quotidien - Vue d'ensemble

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                         TarotApp                            │
│                       (main.py)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────┐        │
│  │      DailyRitualManager (daily_ritual.py)      │        │
│  ├────────────────────────────────────────────────┤        │
│  │  • can_draw_today()                            │        │
│  │  • set_intention(type, text)                   │        │
│  │  • record_draw(card_name)                      │        │
│  │  • get_streak()                                │        │
│  │  • reset_today_if_needed()                     │        │
│  └────────────────────────────────────────────────┘        │
│                         ↕                                    │
│  ┌────────────────────────────────────────────────┐        │
│  │         daily_ritual.json (stockage)           │        │
│  ├────────────────────────────────────────────────┤        │
│  │  last_draw_date: "2026-01-26"                  │        │
│  │  current_streak: 5                             │        │
│  │  today_intention: "love"                       │        │
│  │  draw_completed: true                          │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flux de Navigation

```
┌──────────────────────────────────────────────────────────┐
│                    Démarrage App                         │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│                   CardScreen                             │
│  ┌────────────────────────────────────────────────┐      │
│  │  📱 Bienvenue dans le tarot divinatoire        │      │
│  │                                                │      │
│  │           🃏 [Image carte dos]                 │      │
│  │                                                │      │
│  │  ✨ Votre carte du jour vous attend            │      │
│  │     (ou "Jour X de guidance" si tiré)          │      │
│  └────────────────────────────────────────────────┘      │
└────────────────────────┬─────────────────────────────────┘
                         │ tap sur carte
                         ↓
              ┌──────────────────┐
              │ can_draw_today()?│
              └─────────┬────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
          NON                       OUI
           │                         │
           ↓                         ↓
    ┌─────────────┐      ┌──────────────────────┐
    │   Popup     │      │  IntentionScreen     │
    │ "Déjà tiré" │      │                      │
    │   + streak  │      │  [4 boutons]         │
    └─────────────┘      │  💕 Amour            │
                         │  💼 Travail          │
                         │  🌟 Intérieur        │
                         │  ✍️ Question libre   │
                         │                      │
                         │  [Valider]           │
                         └──────────┬───────────┘
                                    │
                                    ↓
                         ┌──────────────────────┐
                         │ set_intention()      │
                         │ LoadingPopup         │
                         └──────────┬───────────┘
                                    │
                                    ↓ 5s
                         ┌──────────────────────┐
                         │ perform_card_draw()  │
                         │ record_draw()        │
                         └──────────┬───────────┘
                                    │
                                    ↓
                         ┌──────────────────────┐
                         │  ResponseScreen      │
                         │                      │
                         │  🃏 [Carte révélée]  │
                         │                      │
                         │  💕 Dans le domaine  │
                         │  de l'amour...       │
                         │  [Message adapté]    │
                         │                      │
                         │  [Nouveau tirage]    │
                         └──────────┬───────────┘
                                    │
                                    ↓
                         ┌──────────────────────┐
                         │    CardScreen        │
                         │  ✨ Jour X de        │
                         │     guidance         │
                         └──────────────────────┘
```

---

## ⏰ Timeline d'une Journée

```
00:00 ─────────────────────────────────────────────────────────── 23:59
  │                                                                  │
  ├─ Minuit : reset_today_if_needed()                              │
  │  • draw_completed → false                                       │
  │  • today_intention → null                                       │
  │  • Vérification streak (cassé si jour manqué)                  │
  │                                                                  │
  │                                                                  │
  ├─ 08:00 : Utilisateur ouvre l'app                               │
  │  • Badge : "Carte du jour vous attend"                          │
  │  • Tap → IntentionScreen                                        │
  │                                                                  │
  │                                                                  │
  ├─ 08:05 : Utilisateur effectue tirage                           │
  │  • Intention : "love"                                           │
  │  • record_draw() → draw_completed = true                        │
  │  • Streak +1                                                    │
  │  • Badge : "Jour X de guidance"                                 │
  │                                                                  │
  │                                                                  │
  ├─ 09:30 : Utilisateur rouvre l'app                              │
  │  • Badge toujours "Jour X"                                      │
  │  • Tap → Popup "Déjà tiré aujourd'hui"                         │
  │                                                                  │
  │                                                                  │
  ├─ 11:00 : _maybe_notify_draw_reminder()                         │
  │  • Si draw_completed = true → Pas de notification              │
  │  • Si draw_completed = false → Notification                    │
  │                                                                  │
  │                                                                  │
  ├─ 23:59 : Fin de journée                                        │
  │  • Données conservées pour demain                               │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────
```

---

## 🔐 Gestion du Streak

```
Jour 1 (26 jan)
┌────────────────────────────────────┐
│ last_draw_date: "2026-01-26"       │
│ current_streak: 1                  │
│ best_streak: 1                     │
│ draw_completed: true               │
└────────────────────────────────────┘
          │
          ↓ Utilisateur tire le 27 (consécutif)
Jour 2 (27 jan)
┌────────────────────────────────────┐
│ last_draw_date: "2026-01-27"       │
│ current_streak: 2 ← +1             │
│ best_streak: 2                     │
│ draw_completed: true               │
└────────────────────────────────────┘
          │
          ↓ Utilisateur ne tire PAS le 28 (manqué)
Jour 3 (29 jan)
┌────────────────────────────────────┐
│ last_draw_date: "2026-01-27"       │
│ current_streak: 0 ← RESET          │
│ best_streak: 2 ← Conservé          │
│ draw_completed: false              │
└────────────────────────────────────┘
          │
          ↓ Utilisateur tire le 29 (nouveau départ)
Jour 3 (29 jan)
┌────────────────────────────────────┐
│ last_draw_date: "2026-01-29"       │
│ current_streak: 1 ← Redémarre      │
│ best_streak: 2 ← Toujours conservé │
│ draw_completed: true               │
└────────────────────────────────────┘
```

---

## 🎨 États du Badge

```
État 1 : AVANT TIRAGE
┌───────────────────────────────────┐
│ ✨ Votre carte du jour vous       │
│    attend                          │
│                                    │
│ Couleur : Or [1, 0.85, 0.2, 1]    │
│ Opacité : 1                        │
└───────────────────────────────────┘

État 2 : APRÈS TIRAGE (streak = 1)
┌───────────────────────────────────┐
│ ✨ Jour 1 de guidance             │
│                                    │
│ Couleur : Vert [0.2, 1, 0.4, 1]   │
│ Opacité : 1                        │
└───────────────────────────────────┘

État 3 : APRÈS TIRAGE (streak = 5)
┌───────────────────────────────────┐
│ ✨ Jour 5 de guidance             │
│                                    │
│ Couleur : Vert [0.2, 1, 0.4, 1]   │
│ Opacité : 1                        │
└───────────────────────────────────┘

État 4 : PAS VISIBLE (erreur)
┌───────────────────────────────────┐
│                                    │
│                                    │
│ Opacité : 0                        │
└───────────────────────────────────┘
```

---

## 🎬 Diagramme d'Animations

```
CardScreen
   │
   │ tap sur carte
   │
   ↓
fade out (700ms)
   │
   │ opacity: 1.0 → 0.0
   │
   ↓
IntentionScreen
   │
   │ fade in (700ms)
   │ opacity: 0.0 → 1.0
   │
   ↓
[Sélection intention]
   │
   │ validation
   │
   ↓
LoadingPopup (5s)
   │
   │ perform_card_draw()
   │
   ↓
ResponseScreen
   │
   │ fade in (800ms)
   │ opacity: 0.0 → 1.0
   │
   ↓
[Lecture carte]
   │
   │ retour
   │
   ↓
CardScreen
   │
   │ badge mis à jour
   │
   ↓
[Fin]

Total : ~8.2 secondes (transitions + chargement)
```

---

## 📊 Structure de Données

```
daily_ritual.json
{
  "last_draw_date": string,      // "2026-01-26" (ISO format)
  "current_streak": int,          // 0, 1, 2, 3, ...
  "best_streak": int,             // Maximum atteint
  "total_draws": int,             // Compteur total
  "today_intention": string,      // "love"|"work"|"inner"|"custom"|null
  "today_intention_text": string, // Texte libre ou null
  "today_card": string,           // "major_00", "cups_03", etc.
  "draw_completed": bool,         // true si carte révélée
  "last_notification_date": string // "2026-01-26" ou null
}
```

---

## 🔔 Système de Notifications

```
┌─────────────────────────────────────────────────────┐
│            Scheduler (_schedule_daily_draw_reminder) │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Calcul délai jusqu'à 11h :                        │
│    now = datetime.now()                             │
│    target = now.replace(hour=11, minute=0)          │
│    if target <= now:                                │
│        target += 1 day                              │
│    delay = (target - now).total_seconds()           │
│                                                     │
│  Clock.schedule_once(_fire, delay)                  │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓ Tous les jours à 11h
┌─────────────────────────────────────────────────────┐
│              _maybe_notify_draw_reminder()          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Vérifier si draw_completed = true               │
│     → OUI : return (pas de notification)            │
│                                                     │
│  2. Vérifier last_notification_date == today        │
│     → OUI : return (déjà notifié)                   │
│                                                     │
│  3. Envoyer notification :                          │
│     "Une carte vous attend aujourd'hui ✨"          │
│                                                     │
│  4. Enregistrer last_notification_date = today      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🌍 Support Multilingue

```
i18n/lang/
├── fr.json
│   ├── "daily_badge": "✨ Votre carte du jour vous attend"
│   ├── "intention_title": "Choisissez votre intention"
│   ├── "intention_love": "💕 Amour & Relations"
│   └── ...
│
├── en.json
│   ├── "daily_badge": "✨ Your daily card awaits"
│   ├── "intention_title": "Choose Your Intention"
│   ├── "intention_love": "💕 Love & Relationships"
│   └── ...
│
├── es.json
│   ├── "daily_badge": "✨ Tu carta del día te espera"
│   ├── "intention_title": "Elige tu intención"
│   ├── "intention_love": "💕 Amor y Relaciones"
│   └── ...
│
└── pt.json
    ├── "daily_badge": "✨ Sua carta do dia espera por você"
    ├── "intention_title": "Escolha sua intenção"
    ├── "intention_love": "💕 Amor e Relacionamentos"
    └── ...
```

---

## 🎯 Points d'Entrée Clés

### Pour déboguer
```python
# main.py
TarotApp.__init__()  # Ligne ~216 : Initialisation DailyRitualManager

# screens.py
CardScreen.draw_card()  # Ligne ~217 : Vérification can_draw_today()
IntentionScreen._on_validate()  # Ligne ~1754 : Enregistrement intention
CardScreen.perform_card_draw()  # Ligne ~390 : Enregistrement tirage

# daily_ritual.py
DailyRitualManager.can_draw_today()  # Ligne ~86 : Logique verrouillage
DailyRitualManager.record_draw()  # Ligne ~134 : Mise à jour streak
```

### Pour modifier comportement
```python
# Heure notification : main.py:510
target = now.replace(hour=11, minute=0, second=0, microsecond=0)

# Durées animations : screens.py
Animation(opacity=0, duration=0.7)  # Ligne ~285
Animation(opacity=1, duration=0.8)  # Ligne ~423

# Couleurs badge : screens.py:329-333
self.daily_badge.color = [1, 0.85, 0.2, 1]  # Or
self.daily_badge.color = [0.2, 1, 0.4, 1]   # Vert
```

---

*Diagrammes créés le 26 janvier 2026*
*Voir README_RITUEL.md pour résumé complet*
