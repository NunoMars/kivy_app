# -*- coding: utf-8 -*-
"""
Module de gestion du rituel quotidien.
Gère : tirage unique, streak, intention utilisateur.
"""
from __future__ import annotations
import os
import json
import datetime
from typing import Optional, Dict, Any


class DailyRitualManager:
    """Gestionnaire du rituel quotidien pour l'application Tarot."""
    
    def __init__(self, user_data_dir: str):
        self.user_data_dir = user_data_dir
        self.data_file = os.path.join(user_data_dir, "daily_ritual.json")
        self.data: Dict[str, Any] = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Charge les données du rituel depuis le fichier JSON."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement daily_ritual: {e}")
        
        # Données par défaut
        return {
            "last_draw_date": None,
            "current_streak": 0,
            "best_streak": 0,
            "total_draws": 0,
            "today_intention": None,
            "today_intention_text": None,
            "today_card": None,
            "draw_completed": False
        }
    
    def _save_data(self) -> None:
        """Sauvegarde les données du rituel dans le fichier JSON."""
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde daily_ritual: {e}")
    
    def _today_str(self) -> str:
        """Retourne la date du jour au format ISO (YYYY-MM-DD)."""
        return datetime.date.today().isoformat()
    
    def _update_streak(self) -> None:
        """Met à jour le compteur de jours consécutifs (streak)."""
        today = self._today_str()
        last_date = self.data.get("last_draw_date")
        
        if not last_date:
            # Premier tirage
            self.data["current_streak"] = 1
        else:
            try:
                last_dt = datetime.date.fromisoformat(last_date)
                today_dt = datetime.date.today()
                delta = (today_dt - last_dt).days
                
                if delta == 1:
                    # Jour consécutif
                    self.data["current_streak"] = self.data.get("current_streak", 0) + 1
                elif delta == 0:
                    # Même jour (ne devrait pas arriver avec tirage unique)
                    pass
                else:
                    # Streak cassé
                    self.data["current_streak"] = 1
            except Exception as e:
                print(f"⚠️ Erreur calcul streak: {e}")
                self.data["current_streak"] = 1
        
        # Mise à jour du meilleur streak
        current = self.data.get("current_streak", 0)
        best = self.data.get("best_streak", 0)
        if current > best:
            self.data["best_streak"] = current
    
    def can_draw_today(self) -> bool:
        """Vérifie si l'utilisateur peut faire un tirage aujourd'hui."""
        today = self._today_str()
        last_date = self.data.get("last_draw_date")
        draw_completed = self.data.get("draw_completed", False)
        
        # Si le tirage a été fait et complété aujourd'hui, on bloque
        if last_date == today and draw_completed:
            return False
        return True
    
    def unlock_bonus_draw(self) -> bool:
        """
        Débloque un tirage bonus après une rewarded video.
        Réinitialise draw_completed pour permettre un nouveau tirage.
        
        Returns:
            True si le déblocage a réussi, False sinon
        """
        today = self._today_str()
        last_date = self.data.get("last_draw_date")
        
        # Vérifier qu'on est bien aujourd'hui et que le tirage était bloqué
        if last_date == today and self.data.get("draw_completed", False):
            self.data["draw_completed"] = False
            self.data["bonus_draw_unlocked"] = True
            self._save()
            Logger.info("DailyRitualManager: Tirage bonus débloqué")
            return True
        
        Logger.warning("DailyRitualManager: Impossible de débloquer (pas de tirage fait aujourd'hui)")
        return False
    
    def set_intention(self, intention_type: str, custom_text: Optional[str] = None) -> None:
        """
        Enregistre l'intention choisie par l'utilisateur.
        
        Args:
            intention_type: "love", "work", "inner" ou "custom"
            custom_text: Texte libre si intention_type == "custom"
        """
        today = self._today_str()
        
        # Si c'est un nouveau jour, on réinitialise les données du jour
        if self.data.get("last_draw_date") != today:
            self.data["today_intention"] = None
            self.data["today_intention_text"] = None
            self.data["today_card"] = None
            self.data["draw_completed"] = False
        
        self.data["today_intention"] = intention_type
        self.data["today_intention_text"] = custom_text
        self._save_data()
    
    def get_intention(self) -> tuple[Optional[str], Optional[str]]:
        """
        Récupère l'intention du jour.
        
        Returns:
            (intention_type, custom_text)
        """
        today = self._today_str()
        if self.data.get("last_draw_date") == today:
            return (
                self.data.get("today_intention"),
                self.data.get("today_intention_text")
            )
        return (None, None)
    
    def record_draw(self, card_name: Optional[str] = None) -> None:
        """
        Enregistre qu'un tirage a été effectué aujourd'hui.
        Met à jour le streak et le compteur total.
        
        Args:
            card_name: Nom de la carte tirée (optionnel)
        """
        today = self._today_str()
        
        # Mise à jour du streak
        self._update_streak()
        
        # Enregistrement du tirage
        self.data["last_draw_date"] = today
        self.data["draw_completed"] = True
        self.data["total_draws"] = self.data.get("total_draws", 0) + 1
        
        if card_name:
            self.data["today_card"] = card_name
        
        self._save_data()
    
    def reset_today_if_needed(self) -> None:
        """
        Réinitialise les données du jour si on est un nouveau jour.
        Appelé au démarrage de l'app.
        """
        today = self._today_str()
        last_date = self.data.get("last_draw_date")
        
        if last_date and last_date != today:
            # Nouveau jour : on réinitialise les données temporaires
            self.data["today_intention"] = None
            self.data["today_intention_text"] = None
            self.data["today_card"] = None
            self.data["draw_completed"] = False
            
            # Vérifier si le streak est cassé
            try:
                last_dt = datetime.date.fromisoformat(last_date)
                today_dt = datetime.date.today()
                delta = (today_dt - last_dt).days
                
                if delta > 1:
                    # Streak cassé
                    self.data["current_streak"] = 0
                    print(f"📉 Streak réinitialisé (dernier tirage: {last_date})")
            except Exception as e:
                print(f"⚠️ Erreur vérification streak: {e}")
            
            self._save_data()
    
    def get_streak(self) -> int:
        """Retourne le nombre de jours consécutifs."""
        return self.data.get("current_streak", 0)
    
    def get_best_streak(self) -> int:
        """Retourne le meilleur streak."""
        return self.data.get("best_streak", 0)
    
    def get_total_draws(self) -> int:
        """Retourne le nombre total de tirages."""
        return self.data.get("total_draws", 0)
    
    def get_today_card(self) -> Optional[str]:
        """Retourne la carte tirée aujourd'hui si elle existe."""
        today = self._today_str()
        if self.data.get("last_draw_date") == today:
            return self.data.get("today_card")
        return None
    
    def is_draw_completed_today(self) -> bool:
        """Vérifie si le tirage du jour a été complété (carte révélée)."""
        today = self._today_str()
        return (
            self.data.get("last_draw_date") == today and
            self.data.get("draw_completed", False)
        )
