from __future__ import annotations
# -*- coding: utf-8 -*-

import os
import sys
import random
import json
from typing import Optional, List, Tuple

from kivy.app import App  # type: ignore
from kivy.clock import Clock  # type: ignore
from kivy.graphics import Color, Rectangle, RoundedRectangle  # type: ignore
from kivy.metrics import dp  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.uix.behaviors import ButtonBehavior  # type: ignore
from kivy.uix.floatlayout import FloatLayout  # type: ignore
from kivy.uix.image import Image  # type: ignore
from kivy.uix.label import Label  # type: ignore
from kivy.uix.popup import Popup  # type: ignore
from kivy.uix.screenmanager import ScreenManager, Screen  # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.textinput import TextInput  # type: ignore
from kivy.factory import Factory  # type: ignore
from kivy.animation import Animation  # type: ignore
from kivy.logger import Logger  # type: ignore
from kivy.resources import resource_find  # type: ignore
from kivy.core.window import Window  # type: ignore
from kivy.uix.widget import Widget  # type: ignore

# Popups
from popups import LoadingPopup, FullScreenCardPopup, MmeTChatPopup


READING_COUNT = 0


def _normalize_lang(code: Optional[str]) -> str:
    if not code:
        return "en"
    code = code.lower().replace("_", "-")
    if code.startswith("fr"):
        return "fr"
    if code.startswith("en"):
        return "en"
    if code.startswith("pt"):
        return "pt"
    if code.startswith("es"):
        return "es"
    return code[:2]


def resolve_lang() -> str:
    try:
        app = App.get_running_app()
        cfg = getattr(app, "cfg", None)
        if cfg:
            forced = cfg.get("force_lang") or cfg.get("language")
            if forced:
                return _normalize_lang(forced)
    except Exception:
        pass
    env = os.environ.get("APP_LANG")
    if env:
        return _normalize_lang(env)
    # Récupère la langue depuis App (chargée dans main.py)
    try:
        app = App.get_running_app()
        app_lang = getattr(app, "lang", None)
        if app_lang:
            return _normalize_lang(app_lang)
    except Exception:
        pass
    return "fr"


class RootScreen(ScreenManager):
    pass


class CardScreen(Screen):
    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)
        app = App.get_running_app()
        self.tr = getattr(app, 'tr', lambda k: k)
        self.lang = getattr(app, 'lang', 'fr')
        self.font_body = getattr(app, 'font_body', 'Body')
        # Utiliser font_body pour les titres également si font_title n'existe pas
        self.font_title = getattr(app, 'font_title', self.font_body)
        # Bind pour rafraîchir dynamiquement si l'app met à jour la police ou la fonction tr
        try:
            app.fbind('font_body', self._refresh_fonts)
        except Exception:
            pass
        try:
            app.fbind('tr', self.apply_i18n)
        except Exception:
            pass
        Logger.info(f"CardScreen: init lang={self.lang} font_body={self.font_body}")
        self.loading_popup = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        with layout.canvas.before:
            bg_path = resource_find("tarot_img/bg.jpg")
            if bg_path:
                self.bg = Rectangle(pos=layout.pos, size=layout.size, source=bg_path)
            else:
                Color(0.2, 0.1, 0.3, 1)
                self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        self.title_label = Label(
            text=self.tr("messages.app_title"),
            font_size="22sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.15,
            bold=True,
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None)))
        layout.add_widget(self.title_label)
        # Badge quotidien (carte non tirée)
        self.daily_badge = Label(
            text=self.tr("messages.daily_badge") if callable(getattr(self, 'tr', None)) else "Carte du jour à tirer",
            font_size="12sp",
            color=[1, 0.85, 0.2, 1],
            size_hint_y=None,
            height=dp(20),
            halign='center',
            valign='middle',
            font_name="Body",
            opacity=0,
        )
        self.daily_badge.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        layout.add_widget(self.daily_badge)
        try:
            self._update_daily_badge()
        except Exception:
            pass

        # === ZONE PRINCIPALE : CONSULTATION MME T EN PRIORITÉ + TIRAGE ===
        main_choices_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.7,
            spacing=dp(12),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # --- BOUTON MME T EN PREMIER (PRIORITÉ) ---
        mme_t_container = FloatLayout(size_hint=(1, 0.32))
        
        # Bouton icône Mme T cliquable (comme la carte)
        self.mme_t_icon_button = Button(
            size_hint=(None, None),
            size=(dp(180), dp(180)),
            pos_hint={'center_x': 0.5, 'center_y': 0.58},
            background_normal='tarot_img/icon.png',
            background_down='tarot_img/icon.png',
            border=(0, 0, 0, 0)
        )
        self.mme_t_icon_button.bind(on_press=self.open_mme_t_entry)
        
        # Titre principal sous l'icône
        mme_t_instruction = Label(
            text=self.tr("messages.consultation_mme_t"),
            font_size='16sp',
            bold=True,
            color=[0.9, 0.8, 0.4, 1],
            size_hint=(1, None),
            height=dp(24),
            pos_hint={'center_x': 0.5, 'y': 0.12},
            halign='center',
            valign='middle',
            font_name=self.font_title
        )
        mme_t_instruction.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        
        # Sous-titre descriptif
        mme_t_subtitle = Label(
            text=self.tr("messages.consultation_mme_t_desc"),
            font_size='12sp',
            color=[0.85, 0.75, 0.95, 0.9],
            size_hint=(0.9, None),
            height=dp(32),
            pos_hint={'center_x': 0.5, 'y': 0.0},
            halign='center',
            valign='top',
            font_name=self.font_body
        )
        mme_t_subtitle.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        
        mme_t_container.add_widget(self.mme_t_icon_button)
        mme_t_container.add_widget(mme_t_instruction)
        mme_t_container.add_widget(mme_t_subtitle)
        main_choices_container.add_widget(mme_t_container)
        
        # --- CARTE CENTRALE POUR TIRAGE (EN DESSOUS) ---
        card_container = FloatLayout(size_hint=(1, 0.65))
        
        # Bouton transparent avec image de carte en fond
        self.card_button = Button(
            size_hint=(None, None),
            size=(dp(180), dp(310)),
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            background_normal='tarot_img/Back.jpg',
            background_down='tarot_img/Back.jpg',
            border=(0, 0, 0, 0)
        )
        self.card_button.bind(on_press=self.draw_card)
        
        # Titre principal sous la carte
        card_instruction = Label(
            text=self.tr("messages.card_reading"),
            font_size='16sp',
            bold=True,
            color=[0.9, 0.8, 0.4, 1],
            size_hint=(1, None),
            height=dp(24),
            pos_hint={'center_x': 0.5, 'y': 0.09},
            halign='center',
            valign='middle',
            font_name=self.font_title
        )
        card_instruction.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        
        # Sous-titre descriptif
        card_subtitle = Label(
            text=self.tr("messages.card_reading_desc"),
            font_size='12sp',
            color=[0.85, 0.75, 0.95, 0.9],
            size_hint=(0.9, None),
            height=dp(32),
            pos_hint={'center_x': 0.5, 'y': 0.0},
            halign='center',
            valign='top',
            font_name=self.font_body
        )
        card_subtitle.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        
        card_container.add_widget(self.card_button)
        card_container.add_widget(card_instruction)
        card_container.add_widget(card_subtitle)
        main_choices_container.add_widget(card_container)
        
        layout.add_widget(main_choices_container)

        # === ESPACE POUR BANNIÈRE PUB ===
        self.ad_banner_placeholder = BoxLayout(size_hint_y=0.08)
        layout.add_widget(self.ad_banner_placeholder)

        # === SPACER ===
        layout.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # === PETIT BOUTON "À PROPOS" EN BAS (DISCRET) ===
        about_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=[dp(20), dp(0), dp(20), dp(4)]
        )
        
        about_btn = Button(
            text=self.tr("messages.about") if callable(self.tr) else "À propos",
            size_hint=(1, 1),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[0.7, 0.6, 0.5, 0.8],
            font_size="13sp",
            font_name=self.font_body
        )
        with about_btn.canvas.before:
            Color(0.25, 0.18, 0.15, 0.5)  # Brun très discret
            about_bg = RoundedRectangle(
                pos=about_btn.pos,
                size=about_btn.size,
                radius=[20, 20, 20, 20]
            )
        about_btn.bind(
            pos=lambda i, v: setattr(about_bg, 'pos', v),
            size=lambda i, v: setattr(about_bg, 'size', v)
        )
        def _go_about(*_):
            if self.manager:
                self.manager.current = "about_screen"
        about_btn.bind(on_press=_go_about)
        about_container.add_widget(about_btn)
        
        layout.add_widget(about_container)

        self.add_widget(layout)

        # debug overlay removed

    def _update_bg(self, instance, value):
        try:
            self.bg.pos = instance.pos
            self.bg.size = instance.size
        except Exception:
            pass

    def draw_card(self, _instance):
        """
        Gère le tirage de carte avec vérification du tirage unique quotidien.
        Si le tirage a déjà été fait aujourd'hui, affiche un message.
        Sinon, redirige vers l'écran de sélection d'intention.
        """
        try:
            app = App.get_running_app()
            ritual_mgr = getattr(app, 'ritual_manager', None)
            
            Logger.info("CardScreen: draw_card() appelé")
            
            # Vérifier si le tirage unique est déjà fait
            if ritual_mgr and not ritual_mgr.can_draw_today():
                Logger.info("CardScreen: tirage déjà effectué aujourd'hui")
                self._show_already_drawn_message()
                return
            
            # Si on peut tirer, on va vers l'écran d'intention
            Logger.info("CardScreen: transition vers IntentionScreen")
            self._transition_to_intention_screen()
        except Exception as e:
            Logger.error(f"CardScreen: erreur dans draw_card - {e}")
            import traceback
            traceback.print_exc()
    
    def _show_already_drawn_message(self):
        """Affiche un message moderne indiquant que le tirage du jour a été effectué, avec option de déblocage."""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.graphics import Color, RoundedRectangle
            from kivy.metrics import dp
            from kivy.clock import Clock
            
            app = App.get_running_app()
            ritual_mgr = getattr(app, 'ritual_manager', None)
            
            # Traductions
            title = self.tr("messages.daily_draw_done_title")
            message = self.tr("messages.daily_draw_done_message")
            unlock_btn_text = self.tr("messages.unlock_extra_draw")
            unlock_info = self.tr("messages.unlock_draw_info")
            close_text = self.tr("messages.close")
            
            # Ajoute info sur le streak si disponible
            streak_display = ""
            if ritual_mgr:
                streak = ritual_mgr.get_streak()
                if streak > 0:
                    streak_display = f"\\n\\n🔥 Série actuelle : {streak} jour{'s' if streak > 1 else ''}"
            
            # Layout principal avec fond moderne arrondi
            layout = BoxLayout(
                orientation='vertical',
                spacing=dp(16),
                padding=[dp(20), dp(18), dp(20), dp(20)]
            )
            with layout.canvas.before:
                Color(0.08, 0.04, 0.12, 0.98)  # Fond violet foncé moderne
                bg = RoundedRectangle(
                    pos=layout.pos,
                    size=layout.size,
                    radius=[18, 18, 18, 18]
                )
            layout.bind(
                pos=lambda i, v: setattr(bg, 'pos', v),
                size=lambda i, v: setattr(bg, 'size', v)
            )
            
            # Titre élégant
            title_lbl = Label(
                text=title,
                size_hint_y=None,
                height=dp(40),
                bold=True,
                font_size='20sp',
                color=(0.95, 0.85, 0.50, 1),  # Or doux
                halign='center',
                font_name=self.font_title
            )
            layout.add_widget(title_lbl)
            
            # Message principal avec streak
            main_msg = message + streak_display
            msg_lbl = Label(
                text=main_msg,
                size_hint_y=None,
                height=dp(80),
                font_size='15sp',
                color=(0.95, 0.95, 0.95, 1),
                halign='center',
                valign='middle',
                font_name=self.font_body
            )
            msg_lbl.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None))
            )
            layout.add_widget(msg_lbl)
            
            # Séparateur visuel
            separator = BoxLayout(size_hint_y=None, height=dp(1))
            with separator.canvas.before:
                Color(0.3, 0.2, 0.4, 0.5)
                sep_rect = RoundedRectangle(pos=separator.pos, size=separator.size)
            separator.bind(
                pos=lambda i, v: setattr(sep_rect, 'pos', v),
                size=lambda i, v: setattr(sep_rect, 'size', v)
            )
            layout.add_widget(separator)
            
            # Info déblocage
            info_lbl = Label(
                text=unlock_info,
                size_hint_y=None,
                height=dp(70),
                font_size='13sp',
                color=(0.85, 0.75, 0.90, 1),
                halign='center',
                valign='middle',
                font_name=self.font_body
            )
            info_lbl.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None))
            )
            layout.add_widget(info_lbl)
            
            # Conteneur pour les boutons
            btn_container = BoxLayout(
                orientation='vertical',
                spacing=dp(10),
                size_hint_y=None,
                height=dp(100)
            )
            
            # Bouton "Débloquer" moderne
            unlock_btn = Button(
                text=unlock_btn_text,
                size_hint=(1, None),
                height=dp(48),
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=[1, 1, 1, 1],
                font_size='16sp',
                bold=True,
                font_name=self.font_body
            )
            with unlock_btn.canvas.before:
                Color(0.45, 0.25, 0.65, 1)  # Violet premium
                unlock_bg = RoundedRectangle(
                    pos=unlock_btn.pos,
                    size=unlock_btn.size,
                    radius=[24, 24, 24, 24]
                )
            unlock_btn.bind(
                pos=lambda i, v: setattr(unlock_bg, 'pos', v),
                size=lambda i, v: setattr(unlock_bg, 'size', v)
            )
            
            # Bouton "Fermer" discret
            close_btn = Button(
                text=close_text,
                size_hint=(1, None),
                height=dp(42),
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=[0.7, 0.7, 0.7, 1],
                font_size='14sp',
                font_name=self.font_body
            )
            with close_btn.canvas.before:
                Color(0.15, 0.1, 0.2, 0.6)  # Gris foncé
                close_bg = RoundedRectangle(
                    pos=close_btn.pos,
                    size=close_btn.size,
                    radius=[21, 21, 21, 21]
                )
            close_btn.bind(
                pos=lambda i, v: setattr(close_bg, 'pos', v),
                size=lambda i, v: setattr(close_bg, 'size', v)
            )
            
            btn_container.add_widget(unlock_btn)
            btn_container.add_widget(close_btn)
            layout.add_widget(btn_container)
            
            # Création du popup sans titre (titre intégré)
            popup = Popup(
                title='',
                content=layout,
                size_hint=(0.90, None),
                height=dp(420),
                background='',
                separator_height=0,
                auto_dismiss=True
            )
            
            # Callback déblocage
            def on_unlock(*_):
                popup.dismiss()
                self._unlock_bonus_draw_with_ad()
            
            unlock_btn.bind(on_press=on_unlock)
            close_btn.bind(on_press=popup.dismiss)
            
            popup.open()
            Logger.info("CardScreen: popup moderne 'déjà tiré' affiché avec option déblocage")
            
        except Exception as e:
            Logger.error(f"CardScreen: erreur affichage popup moderne - {e}")
            import traceback
            traceback.print_exc()
    
    def _unlock_bonus_draw_with_ad(self):
        """Lance une rewarded video pour débloquer un tirage bonus."""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.graphics import Color, RoundedRectangle
            from kivy.metrics import dp
            from kivy.clock import Clock
            
            app = App.get_running_app()
            ads_mgr = getattr(app, 'ads', None)
            ritual_mgr = getattr(app, 'ritual_manager', None)
            
            if not ads_mgr or not ritual_mgr:
                Logger.warning("CardScreen: ads_mgr ou ritual_mgr non disponible")
                return
            
            # Popup de chargement
            loading_layout = BoxLayout(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(12)
            )
            with loading_layout.canvas.before:
                Color(0.08, 0.04, 0.12, 0.98)
                loading_bg = RoundedRectangle(
                    pos=loading_layout.pos,
                    size=loading_layout.size,
                    radius=[18, 18, 18, 18]
                )
            loading_layout.bind(
                pos=lambda i, v: setattr(loading_bg, 'pos', v),
                size=lambda i, v: setattr(loading_bg, 'size', v)
            )
            
            loading_lbl = Label(
                text=self.tr("messages.unlocking_draw"),
                font_size='16sp',
                color=(0.95, 0.85, 0.50, 1),
                font_name=self.font_body
            )
            loading_layout.add_widget(loading_lbl)
            
            loading_popup = Popup(
                title='',
                content=loading_layout,
                size_hint=(0.7, None),
                height=dp(120),
                background='',
                separator_height=0,
                auto_dismiss=False
            )
            loading_popup.open()
            
            def on_reward_received():
                """Appelé quand la vidéo est complétée."""
                try:
                    loading_popup.dismiss()
                    
                    # Débloquer le tirage
                    if ritual_mgr.unlock_bonus_draw():
                        # Popup de succès
                        self._show_success_popup(
                            self.tr("messages.draw_unlocked"),
                            self.tr("messages.draw_unlocked_message")
                        )
                        # Mettre à jour le badge
                        self._update_daily_badge()
                        # Rediriger vers l'écran d'intention après 1.5 seconde
                        Clock.schedule_once(lambda dt: self._transition_to_intention_screen(), 1.5)
                    else:
                        Logger.error("CardScreen: échec déblocage tirage")
                        
                except Exception as e:
                    Logger.error(f"CardScreen: erreur callback reward - {e}")
            
            def on_ad_dismiss():
                """Appelé si la pub n'est pas disponible ou fermée."""
                try:
                    loading_popup.dismiss()
                    self._show_error_popup(
                        self.tr("messages.ad_not_ready"),
                        self.tr("messages.ad_not_ready_message")
                    )
                except Exception as e:
                    Logger.error(f"CardScreen: erreur callback dismiss - {e}")
            
            # Lancer la rewarded video
            Clock.schedule_once(
                lambda dt: ads_mgr.show_rewarded_video(
                    on_reward=on_reward_received,
                    on_dismiss=on_ad_dismiss
                ),
                0.5
            )
            
        except Exception as e:
            Logger.error(f"CardScreen: erreur _unlock_bonus_draw_with_ad - {e}")
            import traceback
            traceback.print_exc()
    
    def _show_success_popup(self, title, message):
        """Affiche un popup de succès moderne."""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.graphics import Color, RoundedRectangle
            from kivy.metrics import dp
            
            layout = BoxLayout(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(15)
            )
            with layout.canvas.before:
                Color(0.08, 0.15, 0.08, 0.98)  # Vert foncé
                bg = RoundedRectangle(
                    pos=layout.pos,
                    size=layout.size,
                    radius=[18, 18, 18, 18]
                )
            layout.bind(
                pos=lambda i, v: setattr(bg, 'pos', v),
                size=lambda i, v: setattr(bg, 'size', v)
            )
            
            title_lbl = Label(
                text=title,
                size_hint_y=None,
                height=dp(40),
                bold=True,
                font_size='20sp',
                color=(0.4, 0.95, 0.4, 1),
                halign='center',
                font_name=self.font_title
            )
            layout.add_widget(title_lbl)
            
            msg_lbl = Label(
                text=message,
                size_hint_y=None,
                height=dp(60),
                font_size='15sp',
                color=(0.95, 0.95, 0.95, 1),
                halign='center',
                valign='middle',
                font_name=self.font_body
            )
            msg_lbl.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None))
            )
            layout.add_widget(msg_lbl)
            
            ok_btn = Button(
                text=self.tr("messages.ok"),
                size_hint=(None, None),
                size=(dp(140), dp(44)),
                pos_hint={'center_x': 0.5},
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=[1, 1, 1, 1],
                font_size='16sp',
                bold=True,
                font_name=self.font_body
            )
            with ok_btn.canvas.before:
                Color(0.3, 0.7, 0.3, 1)
                ok_bg = RoundedRectangle(
                    pos=ok_btn.pos,
                    size=ok_btn.size,
                    radius=[22, 22, 22, 22]
                )
            ok_btn.bind(
                pos=lambda i, v: setattr(ok_bg, 'pos', v),
                size=lambda i, v: setattr(ok_bg, 'size', v)
            )
            layout.add_widget(ok_btn)
            
            popup = Popup(
                title='',
                content=layout,
                size_hint=(0.80, None),
                height=dp(220),
                background='',
                separator_height=0,
                auto_dismiss=True
            )
            
            ok_btn.bind(on_press=popup.dismiss)
            popup.open()
            
        except Exception as e:
            Logger.error(f"CardScreen: erreur _show_success_popup - {e}")
    
    def _show_error_popup(self, title, message):
        """Affiche un popup d'erreur moderne."""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.graphics import Color, RoundedRectangle
            from kivy.metrics import dp
            
            layout = BoxLayout(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(15)
            )
            with layout.canvas.before:
                Color(0.15, 0.05, 0.05, 0.98)  # Rouge foncé
                bg = RoundedRectangle(
                    pos=layout.pos,
                    size=layout.size,
                    radius=[18, 18, 18, 18]
                )
            layout.bind(
                pos=lambda i, v: setattr(bg, 'pos', v),
                size=lambda i, v: setattr(bg, 'size', v)
            )
            
            title_lbl = Label(
                text=title,
                size_hint_y=None,
                height=dp(40),
                bold=True,
                font_size='18sp',
                color=(0.95, 0.5, 0.5, 1),
                halign='center',
                font_name=self.font_title
            )
            layout.add_widget(title_lbl)
            
            msg_lbl = Label(
                text=message,
                size_hint_y=None,
                height=dp(60),
                font_size='14sp',
                color=(0.95, 0.95, 0.95, 1),
                halign='center',
                valign='middle',
                font_name=self.font_body
            )
            msg_lbl.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None))
            )
            layout.add_widget(msg_lbl)
            
            ok_btn = Button(
                text=self.tr("messages.ok"),
                size_hint=(None, None),
                size=(dp(140), dp(44)),
                pos_hint={'center_x': 0.5},
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=[1, 1, 1, 1],
                font_size='16sp',
                bold=True,
                font_name=self.font_body
            )
            with ok_btn.canvas.before:
                Color(0.7, 0.3, 0.3, 1)
                ok_bg = RoundedRectangle(
                    pos=ok_btn.pos,
                    size=ok_btn.size,
                    radius=[22, 22, 22, 22]
                )
            ok_btn.bind(
                pos=lambda i, v: setattr(ok_bg, 'pos', v),
                size=lambda i, v: setattr(ok_bg, 'size', v)
            )
            layout.add_widget(ok_btn)
            
            popup = Popup(
                title='',
                content=layout,
                size_hint=(0.80, None),
                height=dp(220),
                background='',
                separator_height=0,
                auto_dismiss=True
            )
            
            ok_btn.bind(on_press=popup.dismiss)
            popup.open()
            
        except Exception as e:
            Logger.error(f"CardScreen: erreur _show_error_popup - {e}")

    
    def _transition_to_intention_screen(self):
        """Transition fluide et rituelle vers l'écran d'intention."""
        try:
            if not self.manager:
                Logger.error("CardScreen: manager non disponible pour transition")
                return
            
            # Animation de fade out
            anim = Animation(opacity=0, duration=0.7)
            
            def _switch_screen(dt):
                try:
                    self.manager.current = "intention_screen"
                    # Fade in de l'écran suivant
                    intention_screen = self.manager.get_screen("intention_screen")
                    intention_screen.opacity = 0
                    Animation(opacity=1, duration=0.7).start(intention_screen)
                except Exception as e:
                    Logger.error(f"CardScreen: erreur switch vers IntentionScreen - {e}")
                    # Restaurer l'écran en cas d'erreur
                    self.opacity = 1
            
            anim.bind(on_complete=lambda *args: Clock.schedule_once(_switch_screen, 0))
            anim.start(self)
        except Exception as e:
            Logger.error(f"CardScreen: erreur transition - {e}")
            import traceback
            traceback.print_exc()
        anim.start(self)
    
    def _update_daily_badge(self):
        """Met à jour l'affichage du badge quotidien avec le streak."""
        try:
            app = App.get_running_app()
            ritual_mgr = getattr(app, 'ritual_manager', None)
            
            if not ritual_mgr:
                self.daily_badge.opacity = 0
                return
            
            # Vérifie si le tirage a été complété aujourd'hui
            if ritual_mgr.is_draw_completed_today():
                # Tirage déjà fait : afficher le streak
                streak = ritual_mgr.get_streak()
                if streak > 0:
                    self.daily_badge.text = self.tr("messages.streak_badge").format(days=streak)
                    self.daily_badge.color = [0.2, 1, 0.4, 1]  # Vert
                    self.daily_badge.opacity = 1
                else:
                    self.daily_badge.opacity = 0
            else:
                # Tirage non fait : message d'invitation
                self.daily_badge.text = self.tr("messages.daily_badge")
                self.daily_badge.color = [1, 0.85, 0.2, 1]  # Or
                self.daily_badge.opacity = 1
        except Exception as e:
            Logger.warning(f"CardScreen: erreur _update_daily_badge - {e}")
            self.daily_badge.opacity = 0
    
    def on_enter(self):
        """Appelé quand l'écran devient visible."""
        # Restaurer l'opacity au cas où elle serait à 0 après une animation
        self.opacity = 1
        
        # Met à jour le badge à chaque entrée sur l'écran
        try:
            self._update_daily_badge()
        except Exception:
            pass

    def _refresh_fonts(self, *args):
        # Prefer KV ids when present (macartedetarot.kv)
        try:
            if hasattr(self, 'ids') and 'app_title_label' in self.ids:
                self.ids['app_title_label'].font_name = self.font_body
        except Exception:
            pass
        try:
            if hasattr(self, 'title_label'):
                self.title_label.font_name = self.font_body
        except Exception:
            pass
        try:
            if hasattr(self, 'ids') and 'instruction_label' in self.ids:
                self.ids['instruction_label'].font_name = self.font_body
        except Exception:
            pass
        try:
            if hasattr(self, 'instructions_label'):
                self.instructions_label.font_name = self.font_body
        except Exception:
            pass
        try:
            if hasattr(self, 'ids') and 'ad_banner' in self.ids:
                self.ids['ad_banner'].font_name = self.font_body
        except Exception:
            pass
        try:
            if hasattr(self, 'ad_banner'):
                self.ad_banner.font_name = self.font_body
        except Exception:
            pass
        print(f"CardScreen: _refresh_fonts applied font_body={self.font_body}")
        Logger.info(f"CardScreen: _refresh_fonts applied font_body={self.font_body}")

    def apply_i18n(self, *args):
        # Prefer KV ids if the layout comes from macartedetarot.kv
        try:
            title = self.tr("messages.app_title")
            if hasattr(self, 'ids') and 'app_title_label' in self.ids:
                self.ids['app_title_label'].text = title
            elif hasattr(self, 'title_label'):
                self.title_label.text = title
        except Exception:
            pass
        try:
            if hasattr(self, 'daily_badge'):
                self.daily_badge.text = self.tr("messages.daily_badge")
        except Exception:
            pass
        try:
            instr = self.tr("messages.draw_instruction")
            if hasattr(self, 'ids') and 'instruction_label' in self.ids:
                self.ids['instruction_label'].text = instr
            elif hasattr(self, 'instructions_label'):
                self.instructions_label.text = instr
        except Exception:
            pass
        # Retiré: plus de texte mock de bannière
        try:
            # mettre à jour visibilité du badge
            if hasattr(self, '_update_daily_badge'):
                self._update_daily_badge()
        except Exception:
            pass
        if hasattr(self, 'back_btn'):
            label = self.tr("messages.new_reading")
            if not label or not isinstance(label, str) or not label.strip():
                label = "Nouveau tirage"
            self.back_btn.text = label
        if hasattr(self, 'premium_btn'):
            # Bouton Mme T sans suffixe IAP (flux pubs)
            label = self.tr("messages.chat_mme_t") if hasattr(self, 'tr') else None
            self.premium_btn.text = (label or "Chat Mme T")
        # Also update KV back button text if present
        try:
            if hasattr(self, 'ids') and 'back_button' in self.ids:
                self.ids['back_button'].text = self.tr("messages.new_reading")
        except Exception:
            pass
        # Print to stdout to ensure visibility in logcat
        try:
            cur_title = None
            if hasattr(self, 'ids') and 'app_title_label' in self.ids:
                cur_title = self.ids['app_title_label'].text
            elif hasattr(self, 'title_label'):
                cur_title = self.title_label.text
            print(f"CardScreen: apply_i18n -> title={cur_title!r}")
            Logger.info(f"CardScreen: apply_i18n -> title={cur_title!r}")
        except Exception:
            pass

    def perform_card_draw(self, _dt):
        """Effectue le tirage de carte et enregistre dans le système de rituel."""
        try:
            # Tirage basé directement sur les clés fournies par la langue courante
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards_signification = app.get_cards_signification() or {}
            else:
                cards_signification = {}
            cards = list(cards_signification.keys()) if isinstance(cards_signification, dict) else []

            if not cards:
                if self.loading_popup:
                    try:
                        self.loading_popup.dismiss()
                    except Exception:
                        pass
                return

            try:
                count = int(os.environ.get("TAROT_DRAW_COUNT", "3"))
            except Exception:
                count = 3
            count = max(1, min(4, count))

            drawn: List[Tuple[str, str]] = []
            pool = list(cards)
            for _ in range(count):
                if not pool:
                    pool = list(cards)
                pick = random.choice(pool)
                pool.remove(pick)
                state = random.choice(["upright", "reversed"])
                drawn.append((pick, state))

            try:
                app = App.get_running_app()
                app.last_drawn_cards = drawn
                
                # Enregistre le tirage dans le système de rituel
                ritual_mgr = getattr(app, 'ritual_manager', None)
                if ritual_mgr:
                    ritual_mgr.record_draw(drawn[0][0])
                    Logger.info(f"CardScreen: tirage enregistré - {drawn[0][0]}")
            except Exception as e:
                Logger.warning(f"CardScreen: erreur enregistrement tirage - {e}")

            if self.loading_popup:
                try:
                    self.loading_popup.dismiss()
                except Exception:
                    pass

            def _show_with_transition():
                """Transition animée vers l'écran de révélation."""
                if self.manager:
                    resp = self.manager.get_screen("response_screen")
                    resp.setup_card(drawn[0][0], drawn[0][1])
                    if hasattr(resp, "set_full_draw"):
                        try:
                            resp.set_full_draw(drawn)
                        except Exception:
                            pass
                    
                    # Animation de fade vers ResponseScreen
                    resp.opacity = 0
                    self.manager.current = "response_screen"
                    Animation(opacity=1, duration=0.8).start(resp)

            # Interstitielle AdMob (non bloquante)
            try:
                app = App.get_running_app()
                if hasattr(app, 'ads') and getattr(app.ads, 'enabled', False):
                    app.ads.on_card_drawn()
            except Exception:
                pass

            _show_with_transition()
        except Exception as exc:
            print(f"Erreur perform_card_draw: {exc}")
            if self.loading_popup:
                try:
                    self.loading_popup.dismiss()
                except Exception:
                    pass

    def open_mme_t_entry(self, *_):
        """Ouvre le chat Mme T avec popup d'info publicitaire."""
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.graphics import Color, RoundedRectangle
            from kivy.metrics import dp
            
            # Titre et corps du popup
            title = "Mme T – Soutenir le projet"
            body = (
                "Discutez avec Mme T et posez-lui toutes vos questions.\n"
                "Pour garder cette application gratuite et sans abonnement,\n"
                "une courte publicité sera affichée avant le chat, puis une publicité\n"
                "plein écran toutes les 3 questions posées.\n\n"
                "Merci de votre soutien 💜"
            )
            
            # Localisation si possible
            try:
                if hasattr(self, 'tr') and callable(self.tr):
                    title = "Mme T – " + (self.tr("messages.support_app") or "Soutenir le projet")
                    body = self.tr("messages.mme_t_ads_info") or body
            except Exception:
                pass
            
            # Layout principal avec fond arrondi
            layout = BoxLayout(
                orientation='vertical', 
                spacing=dp(12), 
                padding=[dp(18), dp(14), dp(18), dp(18)]
            )
            with layout.canvas.before:
                Color(0.06, 0.03, 0.09, 0.98)
                bg = RoundedRectangle(
                    pos=layout.pos, 
                    size=layout.size, 
                    radius=[14, 14, 14, 14]
                )
            layout.bind(
                pos=lambda i, v: setattr(bg, 'pos', v),
                size=lambda i, v: setattr(bg, 'size', v)
            )
            
            # Titre
            title_lbl = Label(
                text=title,
                size_hint_y=None,
                height=dp(36),
                bold=True,
                font_size='18sp',
                color=(0.92, 0.78, 0.4, 1),
                halign='center'
            )
            layout.add_widget(title_lbl)
            
            # Corps du message
            body_lbl = Label(
                text=body,
                size_hint_y=None,
                height=dp(160),
                font_size='14sp',
                color=(0.95, 0.95, 0.95, 1),
                halign='center',
                valign='middle'
            )
            body_lbl.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None))
            )
            layout.add_widget(body_lbl)
            
            # Bouton de confirmation
            confirm_btn = Button(
                text="Continuer",
                size_hint=(None, None),
                size=(dp(160), dp(44)),
                pos_hint={'center_x': 0.5},
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=[1, 1, 1, 1],
                font_size='16sp',
                bold=True
            )
            with confirm_btn.canvas.before:
                Color(0.35, 0.15, 0.55, 1)
                confirm_bg = RoundedRectangle(
                    pos=confirm_btn.pos,
                    size=confirm_btn.size,
                    radius=[22, 22, 22, 22]
                )
            confirm_btn.bind(
                pos=lambda i, v: setattr(confirm_bg, 'pos', v),
                size=lambda i, v: setattr(confirm_bg, 'size', v)
            )
            
            # Création du popup
            popup = Popup(
                title='',
                content=layout,
                size_hint=(0.88, None),
                height=dp(340),
                background='',
                separator_height=0,
                auto_dismiss=True
            )
            
            def on_confirm(*_):
                popup.dismiss()
                # D'abord tirer les 3 cartes, puis ouvrir le chat
                self._draw_cards_for_mme_t()
            
            confirm_btn.bind(on_press=on_confirm)
            layout.add_widget(confirm_btn)
            
            popup.open()
            
        except Exception as e:
            Logger.error(f"Erreur open_mme_t_entry (CardScreen): {e}")
            # Fallback : tirer les cartes et ouvrir directement
            self._draw_cards_for_mme_t()
    
    def _draw_cards_for_mme_t(self):
        """Tire 3 cartes puis ouvre le chat Mme T."""
        try:
            from kivy.clock import Clock
            
            # Tirage des 3 cartes (même logique que perform_card_draw)
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards_signification = app.get_cards_signification() or {}
            else:
                cards_signification = {}
            
            cards = list(cards_signification.keys()) if isinstance(cards_signification, dict) else []
            
            if not cards:
                Logger.error("CardScreen: Aucune carte disponible pour le tirage Mme T")
                return
            
            # Tirer 3 cartes
            count = 3
            drawn: List[Tuple[str, str]] = []
            pool = list(cards)
            for _ in range(count):
                if not pool:
                    pool = list(cards)
                pick = random.choice(pool)
                pool.remove(pick)
                state = random.choice(["upright", "reversed"])
                drawn.append((pick, state))
            
            # Sauvegarder les cartes dans l'app
            app.last_drawn_cards = drawn
            Logger.info(f"CardScreen: 3 cartes tirées pour Mme T: {[c[0] for c in drawn]}")
            
            # Ouvrir le chat Mme T après un court délai
            def delayed_open(*_):
                if self.manager:
                    resp = self.manager.get_screen("response_screen")
                    if hasattr(resp, 'open_mme_t_chat'):
                        resp.open_mme_t_chat(provider="ads")
            
            Clock.schedule_once(delayed_open, 0.3)
            
        except Exception as e:
            Logger.error(f"CardScreen: erreur _draw_cards_for_mme_t - {e}")
            import traceback
            traceback.print_exc()


class ResponseScreen(Screen):
    def refresh_translations(self):
        # Met à jour le texte du bouton retour avec fallback et lecture JSON fr si besoin
        if hasattr(self, 'back_btn'):
            label = self.tr("messages.new_reading") if hasattr(self, 'tr') else None
            # Si la traduction est absente ou brute, fallback sur fr.json
            if not label or not isinstance(label, str) or not label.strip() or label == "messages.new_reading":
                try:
                    fr_path = resource_find("i18n/lang/fr.json")
                    if fr_path and os.path.exists(fr_path):
                        with open(fr_path, "r", encoding="utf-8") as f:
                            fr_data = json.load(f)
                        label = fr_data.get("messages", {}).get("new_reading", "Nouveau tirage")
                    else:
                        label = "Nouveau tirage"
                except Exception:
                    label = "Nouveau tirage"
            self.back_btn.text = label
        # Met à jour le bouton premium si besoin
        if hasattr(self, 'premium_btn'):
            # Rafraîchir le bouton Mme T sans mention d'achat
            label = self.tr("messages.chat_mme_t") if hasattr(self, 'tr') else None
            self.premium_btn.text = (label or "Chat Mme T")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.tr = getattr(app, 'tr', lambda k: k)
        self.lang = getattr(app, 'lang', 'fr')
        self.font_body = getattr(app, 'font_body', 'Body')
        app.fbind('font_body', self._refresh_fonts)
        app.fbind('tr', self.apply_i18n)
        try:
            app.fbind('last_drawn_cards', self.refresh_drawn_cards)
        except Exception:
            pass
        self.current_card_name = ""
        self.current_card_state = ""
        self.current_card_image_path = "tarot_img/Back.jpg"

        self.typewriter_event = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.chat_popup = None

        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(15), dp(20), dp(15)],
            spacing=dp(6),
        )
        with main_layout.canvas.before:
            Color(0.12, 0.07, 0.18, 1)
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
            bg_path = resource_find("tarot_img/bg.jpg")
            if bg_path:
                self.bg.source = bg_path
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # Nom de la carte
        self.card_name_label = Label(
            text="",
            font_size="32sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=None,
            height=dp(48),
            bold=True,
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.card_name_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.card_name_label)

        # Espace
        main_layout.add_widget(Label(size_hint_y=None, height=dp(6)))

        self.card_state_label = Label(
            text="",
            font_size="22sp",
            color=[0.8, 0.6, 0.4, 1],
            size_hint_y=None,
            height=dp(32),
            bold=True,
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.card_state_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.card_state_label)

        # Espace
        main_layout.add_widget(Label(size_hint_y=None, height=dp(4)))

        self.keywords_label = Label(
            text="",
            font_size="18sp",
            color=[0.7, 0.7, 0.9, 1],
            size_hint_y=None,
            height=dp(28),
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.keywords_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        main_layout.add_widget(self.keywords_label)

        # Espace sous-titre (réduit pour laisser de la place au texte)
        main_layout.add_widget(Label(size_hint_y=None, height=dp(8)))

        # Container image cliquable
        # Hauteur d'image responsive pour éviter de masquer le texte sur petits écrans
        def _compute_image_h():
            try:
                return int(max(dp(220), min(Window.height * 0.35, dp(340))))
            except Exception:
                return int(dp(300))

        image_container = FloatLayout(size_hint_y=None, height=_compute_image_h())

        self.card_image = Image(
            source="tarot_img/Back.jpg",
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )

        self.image_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.image_button.bind(on_press=self.show_fullscreen_card)

        overlay_label = Label(
            text=self.tr("messages.touch_to_enlarge"),
            font_size="14sp",
            color=[1, 1, 1, 0.7],
            size_hint=(1, None),
            height=dp(22),
            pos_hint={'center_x': 0.5, 'bottom': 1},
            halign='center',
            valign='middle',
            font_name="Body"
        )
        overlay_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))

        image_container.add_widget(self.card_image)
        image_container.add_widget(self.image_button)
        image_container.add_widget(overlay_label)
        main_layout.add_widget(image_container)

        # Espace réduit au-dessus du texte pour conserver de la place au ScrollView
        main_layout.add_widget(Label(size_hint_y=None, height=dp(8)))

        # Signification avec scroll
        scroll = ScrollView(size_hint_y=1)
        # Utilise AutoScrollLabel si disponible (défini dans main.py)
        try:
            self.signification_label = Factory.AutoScrollLabel(
                text=self.tr("messages.loading"),
                font_size="20sp",
                color=[1, 1, 1, 1],
                halign='left',
                valign='top',
                size_hint_y=None,
                padding=[dp(10), dp(5)],
                font_name="Body"
            )
        except Exception:
            self.signification_label = Label(
            text=self.tr("messages.loading"),
            font_size="20sp",
            color=[1, 1, 1, 1],
            halign='left',
            valign='top',
            size_hint_y=None,
            padding=[dp(10), dp(5)],
            font_name="Body"
            )
        self.signification_label.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val * 0.92, None))
        )
        self.signification_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1] + dp(10))
        )
        scroll.add_widget(self.signification_label)
        main_layout.add_widget(scroll)

        # Bas
        bottom_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[0, dp(6), 0, 0],
            spacing=dp(6),
        )
        bottom_container.bind(minimum_height=bottom_container.setter('height'))

        # Bouton premium
        self.premium_btn = Button(
            text=self.tr("messages.premium_button_base"),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="12sp",
            bold=True,
            font_name="Body"
        )
        with self.premium_btn.canvas.before:
            self.premium_btn_color = Color(0.35, 0.15, 0.55, 1)
            self.premium_btn_bg = RoundedRectangle(
                pos=self.premium_btn.pos,
                size=self.premium_btn.size,
                radius=[20, 20, 20, 20]
            )
        self.premium_btn.opacity = 0.5
        # Remplace l'IAP par le flux publicitaire Mme T
        self.premium_btn.bind(on_press=self.open_mme_t_entry)
        self.premium_btn.bind(pos=self.update_premium_btn_canvas, size=self.update_premium_btn_canvas)
        bottom_container.add_widget(self.premium_btn)

        self.premium_status_label = Label(
            text=self.tr("messages.store_preparing"),
            font_size="9sp",
            color=[0.9, 0.8, 0.95, 1],
            size_hint_y=None,
            height=dp(12),
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.premium_status_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        bottom_container.add_widget(self.premium_status_label)

        # Bouton retour
        self.back_btn = Button(
            text=self.tr("messages.new_reading"),
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="14sp",
            bold=True,
            font_name="Body"
        )

        with self.back_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.back_btn_bg = RoundedRectangle(
                pos=self.back_btn.pos,
                size=self.back_btn.size,
                radius=[20, 20, 20, 20]
            )

        self.back_btn.bind(pos=self.update_back_btn_canvas, size=self.update_back_btn_canvas)
        self.back_btn.bind(on_press=self.go_back)
        bottom_container.add_widget(self.back_btn)

        # Ajouter le conteneur bas
        main_layout.add_widget(bottom_container)

        # Bannière pub (cachée)
        self.ad_banner = Label(
            text=self.tr("messages.crystals_ad"),
            font_size="16sp",
            color=[1, 0.8, 0.2, 1],
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle',
            font_name="Body"
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        self.ad_banner.opacity = 0
        main_layout.add_widget(self.ad_banner)

        self.add_widget(main_layout)

    # Méthodes suivantes...

    # ------------------------------------------------------------
    def on_kv_post(self, base_widget):
        # Widgets from KV are ready; schedule application of i18n/fonts
        Logger.info("ResponseScreen: on_kv_post")
        app = App.get_running_app()
        Clock.schedule_once(lambda dt: self._apply_all(app), 0)
    def on_pre_enter(self, *args):
        Logger.info("ResponseScreen: on_pre_enter")
        app = App.get_running_app()
        try:
            self._apply_all(app)
        except Exception:
            pass

    def _apply_all(self, app):
        try:
            if not app or not hasattr(app, 'tr'):
                Logger.warning("ResponseScreen: tr manquant dans _apply_all")
                return
            # apply translations and fonts in an idempotent way
            try:
                if hasattr(self, 'apply_i18n'):
                    self.apply_i18n()
            except Exception as e:
                Logger.exception(f"ResponseScreen: apply_i18n error: {e}")
            try:
                if hasattr(self, '_refresh_fonts'):
                    self._refresh_fonts()
            except Exception as e:
                Logger.exception(f"ResponseScreen: _refresh_fonts error: {e}")
            Logger.info("ResponseScreen: i18n + fonts applied")
        except Exception as e:
            Logger.exception(f"ResponseScreen: _apply_all fatal: {e}")

    def on_enter(self, *args):
        """Afficher la bannière AdMob en bas sur l'écran de résultat.

        La bannière est gérée côté Java (AdManager) et ancrée en bas
        de l'Activity; ici on ne fait qu'en demander l'affichage.
        """
        try:
            app = App.get_running_app()
            ads = getattr(app, 'ads', None)
            if ads and hasattr(ads, 'show_banner'):
                ads.show_banner()
        except Exception:
            pass

    def on_leave(self, *args):
        """Cacher la bannière lorsqu'on quitte l'écran de résultat."""
        try:
            app = App.get_running_app()
            ads = getattr(app, 'ads', None)
            if ads and hasattr(ads, 'hide_banner'):
                ads.hide_banner()
        except Exception:
            pass

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def _update_bg(self, instance, value):
        try:
            self.bg.pos = instance.pos
            self.bg.size = instance.size
        except Exception:
            pass

    def show_fullscreen_card(self, *_):
        # Récupérer le nom localisé depuis les données de la carte
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards = app.get_cards_signification() or {}
            else:
                cards = {}
            info = cards.get(self.current_card_name, {}) if isinstance(cards, dict) else {}
            display_name = info.get("name", self.current_card_name)
        except Exception as e:
            display_name = self.current_card_name

        # Utiliser l'état déjà traduit affiché dans le label si possible
        card_state_text = (self.card_state_label.text or "").strip()

        popup = FullScreenCardPopup(
            card_image_source=self.current_card_image_path or self.card_image.source,
            card_name=display_name
        )
        popup.open()

    def setup_card(self, card_name: str, state: str):
        self.current_card_name = card_name or ""
        self.current_card_state = state or "upright"
        
        # Récupérer les données de la carte
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'get_cards_signification'):
                cards = app.get_cards_signification() or {}
            else:
                cards = {}
        except Exception:
            cards = {}

        info = cards.get(card_name, {}) if isinstance(cards, dict) else {}

        # Utiliser le nom localisé pour l'affichage
        display_name = info.get("name", card_name)
        self.card_name_label.text = display_name
        self.card_state_label.text = self.tr("messages.reversed") if self.current_card_state == "reversed" else self.tr("messages.upright")

        image_path = info.get("image_reversed") if self.current_card_state == "reversed" else info.get("image")
        self.current_card_image_path = image_path or "tarot_img/Back.jpg"
        self.card_image.source = self.current_card_image_path
        try:
            self.card_image.reload()
        except Exception:
            pass

        keywords = info.get("upright") if self.current_card_state == "upright" else info.get("reversed")
        detail = info.get(f"signification upright") if self.current_card_state == "upright" else info.get(f"signification reversed")

        self.keywords_label.text = f"💫 {str(keywords).upper()} 💫" if keywords else ""
        
        # Personnaliser le message selon l'intention
        if detail:
            personalized_detail = self._personalize_message_by_intention(str(detail))
            self.start_typewriter(personalized_detail)
        else:
            self.signification_label.text = self.tr("messages.no_description")
            try:
                if hasattr(self.signification_label, 'start_auto_scroll'):
                    Clock.schedule_once(lambda dt: self.signification_label.start_auto_scroll(reset=True), 0.1)
            except Exception:
                pass

        # Ajuste le wrapping après un petit délai pour que les layouts soient évalués
        try:
            Clock.schedule_once(self.setup_text_wrapping, 0.05)
        except Exception:
            pass
    
    def _personalize_message_by_intention(self, original_message: str) -> str:
        """
        Personnalise le message de la carte en fonction de l'intention choisie.
        Ajoute une phrase d'introduction contextuelle.
        """
        try:
            app = App.get_running_app()
            ritual_mgr = getattr(app, 'ritual_manager', None)
            
            if not ritual_mgr:
                return original_message
            
            intention_type, custom_text = ritual_mgr.get_intention()
            
            if not intention_type:
                return original_message
            
            # Phrases d'introduction selon l'intention
            intro_phrases = {
                "love": self.tr("messages.intention_intro_love"),
                "work": self.tr("messages.intention_intro_work"),
                "inner": self.tr("messages.intention_intro_inner"),
                "custom": self.tr("messages.intention_intro_custom")
            }
            
            intro = intro_phrases.get(intention_type, "")
            
            # Si question personnalisée, on l'inclut
            if intention_type == "custom" and custom_text:
                intro = intro.format(question=custom_text)
            
            # Combine l'introduction avec le message original
            if intro:
                return f"{intro}\n\n{original_message}"
            
            return original_message
        except Exception as e:
            Logger.warning(f"ResponseScreen: erreur personnalisation message - {e}")
            return original_message

    def _refresh_fonts(self, *args):
        self.card_name_label.font_name = self.font_body
        self.card_state_label.font_name = self.font_body
        self.keywords_label.font_name = self.font_body
        if hasattr(self, 'signification_label'):
            self.signification_label.font_name = self.font_body
        if hasattr(self, 'back_btn'):
            self.back_btn.font_name = self.font_body

    def apply_i18n(self, *args):
        # Ne pas écraser le nom de la carte si déjà présent
        if hasattr(self, 'current_card_name') and self.current_card_name:
            # Utilise le nom localisé si possible
            app = App.get_running_app()
            cards = app.get_cards_signification() if app and hasattr(app, 'get_cards_signification') else {}
            info = cards.get(self.current_card_name, {}) if isinstance(cards, dict) else {}
            display_name = info.get("name", self.current_card_name)
            self.card_name_label.text = display_name
        else:
            self.card_name_label.text = self.tr("messages.app_title")
        # Affiche l’état réel de la carte (upright ou reversed)
        if hasattr(self, 'current_card_state') and self.current_card_state == "reversed":
            self.card_state_label.text = self.tr("messages.reversed")
        else:
            self.card_state_label.text = self.tr("messages.upright")
        self.keywords_label.text = ""
        if hasattr(self, 'signification_label'):
            # Ne pas écraser le texte de signification si le typewriter est en cours
            try:
                loading_text = self.tr("messages.loading")
            except Exception:
                loading_text = "Chargement..."
            cur_text = (getattr(self, 'signification_label').text or "").strip()
            typewriter_active = bool(getattr(self, 'typewriter_event', None))
            if not typewriter_active:
                # On ne remplace que si le label est vide ou déjà en état de chargement
                if not cur_text or cur_text == loading_text:
                    self.signification_label.text = loading_text
                    try:
                        if hasattr(self.signification_label, 'stop_auto_scroll'):
                            self.signification_label.stop_auto_scroll()
                            if self.signification_label.parent:
                                Clock.schedule_once(lambda dt: setattr(self.signification_label.parent, 'scroll_y', 1), 0)
                    except Exception:
                        pass
        if hasattr(self, 'back_btn'):
            self.back_btn.text = self.tr("messages.new_reading")

    def start_typewriter(self, text: str, speed: float = 0.02):
        if self.typewriter_event:
            try:
                self.typewriter_event.cancel()
            except Exception:
                pass
        self.typewriter_full_text = text
        self.typewriter_index = 0
        self.signification_label.text = ""
        self.typewriter_event = Clock.schedule_interval(lambda dt: self.typewriter_step(speed), speed)

    def typewriter_step(self, speed: float):
        if self.typewriter_index < len(self.typewriter_full_text):
            self.signification_label.text += self.typewriter_full_text[self.typewriter_index]
            self.typewriter_index += 1
            if self.signification_label.parent:
                try:
                    self.signification_label.parent.scroll_y = 1
                except Exception:
                    pass
            return True
        else:
            if self.typewriter_event:
                try:
                    self.typewriter_event.cancel()
                except Exception:
                    pass
                self.typewriter_event = None
            # Démarrer l'auto-scroll quand tout le texte est affiché
            try:
                if hasattr(self.signification_label, 'start_auto_scroll'):
                    Clock.schedule_once(lambda dt: self.signification_label.start_auto_scroll(reset=True), 0.1)
            except Exception:
                pass
            return False

    def go_back(self, *_):
        if self.manager:
            # Revenir au screen de tirage (nom tolérant)
            try:
                self.manager.current = "card_screen"
            except Exception:
                self.manager.current = "main_screen"

    def purchase_chat_luna(self, *_):
        app = App.get_running_app()
        billing = getattr(app, 'billing', None)
        import sys
        # Simulation achat in-app en mode desktop
        if not hasattr(sys, 'getandroidapilevel'):
            # Toujours tenter d'ouvrir la popup Mme T, même si on_purchase_success échoue ou n'existe pas
            try:
                if hasattr(app, 'on_purchase_success') and callable(getattr(app, 'on_purchase_success')):
                    try:
                        app.on_purchase_success("premium_chat_luna", "simulation")
                    except Exception as e:
                        print(f"⚠️ on_purchase_success hook failed: {e}")
                else:
                    print("ℹ️ on_purchase_success hook not present on App (desktop). Continuing simulation.")
            except Exception as e:
                print(f"⚠️ Exception in on_purchase_success simulation: {e}")
            # Ouvrir la popup Mme T dans tous les cas
            try:
                self.open_mme_t_chat(provider="simulation", price_text="Achat in-app")
            except Exception as e:
                print(f"⚠️ Échec ouverture popup Mme T après achat simulé: {e}")
            return

        # --- ANDROID réel ---
        try:
            app = App.get_running_app()
            billing = getattr(app, 'billing', None)
            if billing and billing.is_ready():
                billing.purchase_product("premium_features")
            else:
                # informe l'utilisateur que la boutique n'est pas prête
                self.update_premium_button(False, None, "disabled")
                self._open_purchase_popup(
                    title=self.tr("messages.store_preparing"),
                    message=self.tr("messages.store_mobile_only")
                )
        except Exception as e:
            print(f"⚠️ Exception achat Android: {e}")
            self._open_purchase_popup(
                title=self.tr("messages.purchase_error_title"),
                message=str(e)
            )

    def _open_purchase_popup(self, title: str, message: str):
        layout = BoxLayout(orientation='vertical', padding=16, spacing=12)
        lbl = Label(text=message)
        btn = Button(text=self.tr("messages.close"), size_hint_y=None, height=dp(40))
        popup = Popup(title=title, content=layout, size_hint=(0.9, 0.5))
        btn.bind(on_release=popup.dismiss)
        layout.add_widget(lbl)
        layout.add_widget(btn)
        popup.open()

    def update_back_btn_canvas(self, instance, value):
        try:
            if hasattr(self, 'back_btn_bg'):
                self.back_btn_bg.pos = instance.pos
                self.back_btn_bg.size = instance.size
        except Exception:
            pass

    def update_premium_btn_canvas(self, instance, value):
        try:
            if hasattr(self, 'premium_btn_bg'):
                self.premium_btn_bg.pos = instance.pos
                self.premium_btn_bg.size = instance.size
        except Exception:
            pass

    def update_premium_button(self, available, price_text, mode):
        # Refonte: bouton devient l'entrée gratuite vers Mme T (monétisation pubs)
        try:
            label = self.tr("messages.chat_mme_t") if hasattr(self, 'tr') else None
            text = (label or "Discuter avec Mme T")
            self.premium_btn.text = text
            self.premium_btn.disabled = False
            self.premium_btn.opacity = 1.0
            if hasattr(self, 'premium_btn_color'):
                self.premium_btn_color.rgba = (0.45, 0.25, 0.65, 1)
            if hasattr(self, 'premium_status_label'):
                self.premium_status_label.text = ""
                self.premium_status_label.opacity = 0
                self.premium_status_label.height = 0
        except Exception:
            pass

    # ------------------------------------------------------------
    # Flux Mme T basé pubs: popup d'information + interstitielle d'entrée
    # ------------------------------------------------------------
    def open_mme_t_entry(self, *_):
        try:
            self._open_mme_t_info_popup()
        except Exception as e:
            # En cas d'échec, ouvrir directement le chat
            try:
                self.open_mme_t_chat(provider="ads")
            except Exception:
                Logger.warning(f"open_mme_t_entry fallback error: {e}")

    def _open_mme_t_info_popup(self):
        from kivy.uix.popup import Popup  # type: ignore
        # Build a themed, rounded popup (no native title bar) so it matches the app
        title = "Mme T – Soutenir le projet"
        # Corps localisé si disponible
        body = None
        try:
            if hasattr(self, 'tr') and callable(self.tr):
                body = self.tr("messages.mme_t_ads_info")
        except Exception:
            pass
        if not body:
            body = (
                "Discutez avec Mme T et posez-lui toutes vos questions.\n"
                "Pour garder cette application gratuite et sans abonnement,\n"
                "une courte publicité sera affichée avant le chat, puis une publicité\n"
                "plein écran toutes les 3 questions posées.\n\n"
                "Merci de votre soutien 💜"
            )
        try:
            # Localisation si possible
            if hasattr(self, 'tr') and callable(self.tr):
                title = "Mme T – " + (self.tr("messages.support_app") or "Soutenir le projet")
        except Exception:
            pass

        # Root container with rounded background so popup looks integrated
        layout = BoxLayout(orientation='vertical', spacing=dp(12), padding=[dp(18), dp(14), dp(18), dp(18)])
        with layout.canvas.before:
            Color(0.06, 0.03, 0.09, 0.98)
            bg = RoundedRectangle(pos=layout.pos, size=layout.size, radius=[14, 14, 14, 14])
        layout.bind(pos=lambda i, v: setattr(bg, 'pos', v), size=lambda i, v: setattr(bg, 'size', v))

        # Custom title bar (integrated) to match theme
        title_lbl = Label(text=title, size_hint_y=None, height=dp(36), bold=True, font_size='18sp')
        title_lbl.color = (0.92, 0.78, 0.4, 1)
        title_lbl.halign = 'center'
        title_lbl.valign = 'middle'
        title_lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0]*0.95, None)))

        # Thin divider under title
        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            Color(0.25, 0.12, 0.35, 1)
            dr = RoundedRectangle(pos=divider.pos, size=divider.size, radius=[1, 1, 1, 1])
        divider.bind(pos=lambda i, v: setattr(dr, 'pos', v), size=lambda i, v: setattr(dr, 'size', v))

        # Body message
        lbl = Label(text=body, halign='center', valign='middle', font_size='15sp')
        lbl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0]*0.95, None)))

        # Buttons row
        btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(12))

        # Cancel button (muted)
        btn_cancel = Button(text=(self.tr("messages.cancel") if hasattr(self, 'tr') and callable(self.tr) else "Annuler"),
                            background_normal='', background_color=[0, 0, 0, 0], color=[1,1,1,1])
        with btn_cancel.canvas.before:
            Color(0.18, 0.18, 0.2, 1)
            cancel_bg = RoundedRectangle(pos=btn_cancel.pos, size=btn_cancel.size, radius=[10, 10, 10, 10])
        btn_cancel.bind(pos=lambda i, v: setattr(cancel_bg, 'pos', v), size=lambda i, v: setattr(cancel_bg, 'size', v))

        # Continue button (accent)
        btn_ok = Button(text=(self.tr("messages.continue") if hasattr(self, 'tr') and callable(self.tr) else "Continuer"),
                        background_normal='', background_color=[0, 0, 0, 0], color=[1,1,1,1])
        with btn_ok.canvas.before:
            Color(0.40, 0.15, 0.55, 1)
            ok_bg = RoundedRectangle(pos=btn_ok.pos, size=btn_ok.size, radius=[10, 10, 10, 10])
        btn_ok.bind(pos=lambda i, v: setattr(ok_bg, 'pos', v), size=lambda i, v: setattr(ok_bg, 'size', v))

        # Assemble
        layout.add_widget(title_lbl)
        layout.add_widget(divider)
        layout.add_widget(lbl)
        btns.add_widget(btn_cancel)
        btns.add_widget(btn_ok)
        layout.add_widget(btns)

        popup = Popup(title='', content=layout, size_hint=(0.92, None), height=dp(300), auto_dismiss=False)
        btn_cancel.bind(on_release=lambda *_: popup.dismiss())
        btn_ok.bind(on_release=lambda *_: (popup.dismiss(), self._start_mme_t_with_ad()))
        popup.open()

    def _start_mme_t_with_ad(self):
        try:
            app = App.get_running_app()
            ads = getattr(app, 'ads', None)
        except Exception:
            ads = None

        def _open_chat():
            try:
                # schedule on the main loop to avoid race with activity focus changes
                Clock.schedule_once(lambda dt: self.open_mme_t_chat(provider="ads"), 0.06)
            except Exception:
                pass

        if ads and hasattr(ads, 'show_interstitial'):
            # Ne pas bloquer la navigation: on ouvre derrière
            try:
                ads.show_interstitial(callback=_open_chat)
            except Exception:
                # ensure consistent scheduling even if show_interstitial fails
                Clock.schedule_once(lambda dt: self.open_mme_t_chat(provider="ads"), 0.06)
        else:
            _open_chat()

    def show_purchase_success(self, provider="google", price_text=None):
        # Si pas de backend Mme T configuré, afficher un message remerciant le soutien
        try:
            if not getattr(__import__("main"), 'MME_T_BACKEND_URL', None):
                provider_label = self.tr("messages.provider_google") if provider == "google" else (self.tr("messages.provider_amazon") if provider == "amazon" else "")
                message = self.tr("messages.thanks_for_support")
                if provider_label:
                    message = self.tr("messages.thanks_for_support_via", provider=provider_label)
                message += "\n" + self.tr("messages.configure_backend_hint")
                self._open_purchase_popup(self.tr("messages.thanks_title"), message)
                return
        except Exception:
            pass
        self.open_mme_t_chat(provider=provider, price_text=price_text)

    def show_purchase_error(self, message):
        self._open_purchase_popup(self.tr("messages.purchase_error_title"), message)

    def open_mme_t_chat(self, provider="google", price_text=None):
        # Ouvre le popup MmeTChat avec jusqu'à 3 cartes
        try:
            if self.chat_popup and getattr(self.chat_popup, 'parent', None):
                self.chat_popup.dismiss()
        except Exception:
            pass
        try:
            app = App.get_running_app()
            drawn = getattr(app, 'last_drawn_cards', None) or []
        except Exception:
            drawn = []
        drawn_three = list(drawn)[:3]
        while len(drawn_three) < 3:
            drawn_three.append((None, None))

        self.chat_popup = MmeTChatPopup(
            language=self.lang,
            provider=provider,
            price_text=price_text,
            context_text=self._build_mme_t_context(),
            drawn_cards=drawn_three,
            on_session_complete=self._on_chat_complete,
            tr=self.tr,
        )
        try:
            self.chat_popup.bind(on_dismiss=lambda *_: setattr(self, 'chat_popup', None))
            self.chat_popup.open()
        except Exception:
            pass

    def _build_mme_t_context(self):
        parts = []
        parts.append(f"Langue de réponse: {self.lang}")
        try:
            app = App.get_running_app()
            get_cards_signification = getattr(app, 'get_cards_signification', None)
            cards = get_cards_signification() if callable(get_cards_signification) else {}
            drawn = getattr(app, 'last_drawn_cards', None)
            if drawn and isinstance(drawn, (list, tuple)) and len(drawn) > 0:
                def fmt(c, s):
                    info = cards.get(c, {}) if isinstance(cards, dict) else {}
                    display = info.get("name", c) if c else self.tr('messages.your_card')
                    state_label = self.tr('messages.upright') if s == 'upright' else self.tr('messages.reversed')
                    return f"{display} ({state_label})"
                drawn_summary = " | ".join(fmt(c, s) for c, s in drawn)
                parts.append(f"{self.tr('messages.draw_card')} ({len(drawn)}): {drawn_summary}")
        except Exception:
            pass
        card_title = (self.card_name_label.text or "").strip()
        if card_title:
            parts.append(f"{self.tr('messages.your_card')}: {card_title}")
        card_state = (self.card_state_label.text or "").strip()
        if card_state:
            parts.append(f"Position: {card_state}")
        keywords = (self.keywords_label.text or "").strip()
        if keywords:
            parts.append(f"Keywords: {keywords}")
        return " | ".join(parts)

    def _on_chat_complete(self):
        if not self.manager:
            return
        # Afficher une interstitielle quand on quitte Mme T
        try:
            app = App.get_running_app()
            ads = getattr(app, 'ads', None)
            if ads and hasattr(ads, 'show_interstitial'):
                ads.show_interstitial()
        except Exception:
            pass

        def _switch(_dt):
            try:
                self.manager.current = "card_screen"
            except Exception:
                self.manager.current = "main_screen"
        Clock.schedule_once(_switch, 0)

    def _open_purchase_popup(self, title: str, message: str):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        label = Label(text=message)
        btn = Button(text=self.tr('messages.close'))
        popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        layout.add_widget(label)
        layout.add_widget(btn)
        popup.open()

    def show_ad_banner(self):
        try:
            self.ad_banner.opacity = 1
        except Exception:
            pass

    def hide_ad_banner(self):
        try:
            self.ad_banner.opacity = 0
        except Exception:
            pass

    def on_enter(self, *args):
        """Fusion : i18n + fonts + couleurs + pubs + état Billing."""
        super().on_enter(*args)
        # i18n
        try:
            self.refresh_translations()
        except Exception as e:
            print(f"[DEBUG] refresh_translations failed: {e}")

        # Couleurs lisibles (merge de l'ancien on_enter)
        try:
            if hasattr(self, 'card_name_label'):
                self.card_name_label.color = (1, 1, 1, 1)
            if hasattr(self, 'card_state_label'):
                self.card_state_label.color = (1, 1, 1, 1)
            if hasattr(self, 'keywords_label'):
                self.keywords_label.color = (1, 1, 1, 1)
            if hasattr(self, 'signification_label'):
                self.signification_label.color = (1, 1, 1, 1)
        except Exception:
            pass

        # Billing state → bouton premium & prix
        try:
            self.on_billing_state_change()
        except Exception:
            pass

        # Pubs
        try:
            app = App.get_running_app()
            if hasattr(app, 'ads') and hasattr(app.ads, 'show_banner'):
                app.ads.show_banner()
        except Exception:
            pass

    def on_leave(self, *args):
        super().on_leave(*args)
        try:
            app = App.get_running_app()
            if hasattr(app, 'ads') and hasattr(app.ads, 'hide_banner'):
                app.ads.hide_banner()
        except Exception:
            pass

    def setup_text_wrapping(self, dt):
        try:
            if self.signification_label and self.parent:
                self.signification_label.text_size = (self.width * 0.9, None)
                self.signification_label.height = self.signification_label.texture_size[1]
        except Exception:
            pass

    def refresh_drawn_cards(self, *args):
        app = App.get_running_app()
        drawn = getattr(app, 'last_drawn_cards', [])
        if drawn:
            self.setup_card(drawn[0][0], drawn[0][1])
            if hasattr(self, "set_full_draw"):
                self.set_full_draw(drawn)

    # ─────────────────────────────────────────────────────────
    # Billing listener hook (MAJ UI quand prêt / prix récupéré)
    # ─────────────────────────────────────────────────────────
    def on_billing_state_change(self, *args):
        """Appelé quand le billing est prêt / prix chargé → met à jour le bouton."""
        try:
            app = App.get_running_app()
            billing = getattr(app, 'billing', None)
            if billing and billing.is_ready():
                price_txt = billing.get_product_price()
                self.update_premium_button(True, price_txt, "google")
            else:
                self.update_premium_button(False, None, "disabled")
        except Exception:
            self.update_premium_button(False, None, "disabled")


# ================================================================
# ℹ️ ABOUT SCREEN (Disclaimer)
# ================================================================
class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.tr = getattr(app, 'tr', lambda k: k)
        self.lang = getattr(app, 'lang', 'fr')
        self.font_body = getattr(app, 'font_body', 'Body')

        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        with root.canvas.before:
            Color(0.1, 0.07, 0.14, 1)
            self._about_bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(self._about_bg, 'pos', v), size=lambda i, v: setattr(self._about_bg, 'size', v))

        title = Label(
            text=self.tr("about.title"),
            font_size="24sp",
            color=[0.9, 0.75, 0.35, 1],
            size_hint_y=None,
            height=dp(46),
            bold=True,
            halign='center',
            valign='middle',
            font_name=self.font_body,
        )
        title.bind(size=lambda i, v: setattr(i, 'text_size', (v[0] * 0.95, None)))
        root.add_widget(title)

        scroll = ScrollView(size_hint_y=1)
        disclaimer = Label(
            text=self.tr("about.disclaimer"),
            font_size="17sp",
            color=[1, 1, 1, 1],
            halign='center',
            valign='top',
            size_hint_y=None,
            padding=[dp(10), dp(6)],
            font_name=self.font_body,
        )
        disclaimer.bind(
            width=lambda i, v: setattr(i, 'text_size', (v * 0.96, None)),
            texture_size=lambda i, v: setattr(i, 'height', v[1] + dp(10))
        )
        scroll.add_widget(disclaimer)
        root.add_widget(scroll)

        bottom = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(10))

        support_btn = Button(
            text=self.tr("messages.support") if callable(self.tr) else "Soutenir",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="16sp",
            bold=True,
            font_name=self.font_body,
        )
        with support_btn.canvas.before:
            Color(0.35, 0.15, 0.55, 1)  # violet comme le bouton premium
            support_bg = RoundedRectangle(pos=support_btn.pos, size=support_btn.size, radius=[25, 25, 25, 25])
        support_btn.bind(pos=lambda i, v: setattr(support_bg, 'pos', v), size=lambda i, v: setattr(support_bg, 'size', v))
        def _start_new_reading(*_):
            try:
                if self.manager:
                    try:
                        card = self.manager.get_screen("card_screen")
                    except Exception:
                        card = self.manager.get_screen("main_screen")
                    if hasattr(card, 'perform_card_draw'):
                        card.perform_card_draw(0)
                    else:
                        self.manager.current = getattr(card, 'name', 'card_screen')
            except Exception as e:
                print(f"Erreur nouveau tirage depuis À propos: {e}")

        def _open_support(*_):
            """Tente d'afficher une interstitielle native (AdMob)."""
            try:
                app = App.get_running_app()
                if hasattr(app, 'ads') and hasattr(app.ads, 'show_interstitial'):
                    app.ads.show_interstitial(callback=_start_new_reading)
                    return
            except Exception as e:
                print(f"⚠️ Interstitiel indisponible: {e}")
            _start_new_reading()
        support_btn.bind(on_press=_open_support)
        bottom.add_widget(support_btn)

        new_btn = Button(
            text=self.tr("messages.new_reading"),
            size_hint=(0.5, 1),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="16sp",
            bold=True,
            font_name=self.font_body,
        )
        with new_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            new_btn_bg = RoundedRectangle(pos=new_btn.pos, size=new_btn.size, radius=[25, 25, 25, 25])
        new_btn.bind(pos=lambda i, v: setattr(new_btn_bg, 'pos', v), size=lambda i, v: setattr(new_btn_bg, 'size', v))
        # new_btn réutilise le même comportement que la pub une fois fermée
        # (tirage immédiat)
        new_btn.bind(on_press=_start_new_reading)
        bottom.add_widget(new_btn)

        root.add_widget(bottom)
        # Espace ajouté sous la barre de boutons pour la remonter d'environ
        # la hauteur du conteneur (augmenté pour éviter le recouvrement par la bannière)
        # Espace sous la barre de boutons pour remonter le bouton About au-dessus de la pub
        # Espace sous la barre de boutons pour remonter le bouton About au-dessus de la pub (valeur augmentée)
        root.add_widget(Widget(size_hint_y=None, height=dp(100)))
        self.add_widget(root)


class IntentionScreen(Screen):
    """
    Écran de sélection de l'intention avant le tirage quotidien.
    L'utilisateur choisit parmi : Amour, Travail, Intérieur, ou Question libre.
    """
    def __init__(self, **kwargs):
        super(IntentionScreen, self).__init__(**kwargs)
        self.name = "intention_screen"
        
        app = App.get_running_app()
        self.tr = getattr(app, 'tr', lambda k: k)
        self.font_body = getattr(app, 'font_body', 'Body')
        self.selected_intention = None
        self.custom_text = None
        
        # Bind pour rafraîchir dynamiquement
        try:
            app.fbind('font_body', self._refresh_fonts)
        except Exception:
            pass
        try:
            app.fbind('tr', self.apply_i18n)
        except Exception:
            pass
        
        self._build_ui()
    
    def _build_ui(self):
        """Construit l'interface de l'écran d'intention."""
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        
        # Fond
        with layout.canvas.before:
            bg_path = resource_find("tarot_img/bg.jpg")
            if bg_path:
                self.bg = Rectangle(pos=layout.pos, size=layout.size, source=bg_path)
            else:
                Color(0.2, 0.1, 0.3, 1)
                self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self._update_bg, size=self._update_bg)
        
        # Titre principal
        self.title_label = Label(
            text=self.tr("messages.choose_draw_type"),
            font_size="24sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=None,
            height=dp(70),
            bold=True,
            halign='center',
            valign='middle',
            font_name=self.font_body
        )
        self.title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None)))
        layout.add_widget(self.title_label)
        
        # Sous-titre explicatif
        self.subtitle_label = Label(
            text=self.tr("messages.intention_subtitle"),
            font_size="14sp",
            color=[0.95, 0.95, 0.95, 0.9],
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='middle',
            font_name=self.font_body
        )
        self.subtitle_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.92, None)))
        layout.add_widget(self.subtitle_label)
        
        # Espace
        layout.add_widget(Widget(size_hint_y=None, height=dp(30)))
        
        # Conteneur centré pour les boutons d'intention (colonne unique)
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.anchorlayout import AnchorLayout
        
        buttons_anchor = AnchorLayout(
            anchor_x='center',
            anchor_y='top',
            size_hint_y=None,
            height=dp(350)
        )
        
        buttons_container = GridLayout(
            cols=1,
            spacing=dp(15),
            size_hint=(None, None),
            width=dp(320),
            height=dp(350)
        )
        
        # Boutons d'intention (exécution directe)
        self.love_btn = self._create_intention_button("love", self.tr("messages.intention_love"), direct=True)
        self.work_btn = self._create_intention_button("work", self.tr("messages.intention_work"), direct=True)
        self.inner_btn = self._create_intention_button("inner", self.tr("messages.intention_inner"), direct=True)
        self.custom_btn = self._create_intention_button("custom", self.tr("messages.intention_custom"), direct=False)
        
        buttons_container.add_widget(self.love_btn)
        buttons_container.add_widget(self.work_btn)
        buttons_container.add_widget(self.inner_btn)
        buttons_container.add_widget(self.custom_btn)
        
        buttons_anchor.add_widget(buttons_container)
        layout.add_widget(buttons_anchor)
        
        # Champ texte pour question libre (initialement caché)
        self.custom_input = TextInput(
            hint_text=self.tr("messages.intention_custom_hint"),
            font_size="16sp",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            font_name=self.font_body,
            opacity=0,
            disabled=True,
            background_color=[0.2, 0.2, 0.25, 0.95]
        )
        layout.add_widget(self.custom_input)
        
        # Bouton de validation (uniquement pour custom)
        self.validate_btn = Button(
            text=self.tr("messages.intention_validate"),
            font_size="18sp",
            size_hint_y=None,
            height=dp(60),
            font_name=self.font_body,
            background_color=[0.45, 0.25, 0.65, 1],
            disabled=True,
            opacity=0
        )
        self.validate_btn.bind(on_press=self._on_validate)
        layout.add_widget(self.validate_btn)
        
        # Espace flexible
        layout.add_widget(Widget(size_hint_y=0.2))
        
        # Espace pour la bannière pub
        layout.add_widget(Widget(size_hint_y=None, height=dp(60)))
        
        self.add_widget(layout)
    
    def _create_intention_button(self, intention_type: str, text: str, direct: bool = True) -> Button:
        """Crée un bouton d'intention avec le style approprié.
        
        Args:
            intention_type: Type d'intention (love, work, inner, custom)
            text: Texte affiché sur le bouton
            direct: Si True, exécute directement le tirage au clic
        """
        btn = Button(
            text=text,
            font_size="17sp",
            size_hint=(None, None),
            size=(dp(290), dp(70)),
            font_name=self.font_body,
            background_color=[0.3, 0.2, 0.4, 0.95],
            color=[1, 1, 1, 1]
        )
        btn.intention_type = intention_type
        btn.direct_execute = direct
        btn.bind(on_press=self._on_intention_select)
        return btn
    
    def _on_intention_select(self, instance):
        """Gère la sélection d'une intention."""
        from kivy.animation import Animation
        
        # Réinitialise l'apparence de tous les boutons
        for btn in [self.love_btn, self.work_btn, self.inner_btn, self.custom_btn]:
            btn.background_color = [0.3, 0.2, 0.4, 0.95]
        
        # Met en évidence le bouton sélectionné
        instance.background_color = [0.5, 0.3, 0.7, 1]
        self.selected_intention = instance.intention_type
        
        # Si custom, affiche le champ texte + bouton validation
        if instance.intention_type == "custom":
            Animation(opacity=1, duration=0.3).start(self.custom_input)
            self.custom_input.disabled = False
            self.custom_input.focus = True
            
            # Active le bouton de validation pour custom
            self.validate_btn.disabled = False
            Animation(opacity=1, duration=0.3).start(self.validate_btn)
        else:
            # Pour les intentions prédéfinies : exécution directe
            Animation(opacity=0, duration=0.2).start(self.custom_input)
            self.custom_input.disabled = True
            Animation(opacity=0, duration=0.2).start(self.validate_btn)
            self.custom_text = None
            
            # Exécute immédiatement le tirage
            if hasattr(instance, 'direct_execute') and instance.direct_execute:
                Clock.schedule_once(lambda dt: self._on_validate(instance), 0.4)
    
    def _on_validate(self, instance):
        """Valide l'intention et lance le tirage de carte."""
        app = App.get_running_app()
        ritual_mgr = getattr(app, 'ritual_manager', None)
        
        if not ritual_mgr:
            Logger.warning("IntentionScreen: ritual_manager non disponible")
            return
        
        # Récupère le texte personnalisé si applicable
        custom_text = None
        if self.selected_intention == "custom":
            custom_text = self.custom_input.text.strip() or None
        
        # Enregistre l'intention
        ritual_mgr.set_intention(self.selected_intention, custom_text)
        Logger.info(f"IntentionScreen: intention enregistrée - {self.selected_intention}")
        
        # Ouvre le popup de chargement
        self.loading_popup = LoadingPopup()
        self.loading_popup.open()
        
        # Lance le tirage après une animation de transition
        Clock.schedule_once(self._perform_draw, 0.8)
    
    def _perform_draw(self, dt):
        """Effectue le tirage de carte via CardScreen."""
        try:
            card_screen = self.manager.get_screen("card_screen")
            card_screen.loading_popup = self.loading_popup
            card_screen.perform_card_draw(dt)
        except Exception as e:
            Logger.error(f"IntentionScreen: erreur lors du tirage - {e}")
            if hasattr(self, 'loading_popup') and self.loading_popup:
                try:
                    self.loading_popup.dismiss()
                except Exception:
                    pass
    
    def _update_bg(self, instance, value):
        """Met à jour la position du fond."""
        try:
            self.bg.pos = instance.pos
            self.bg.size = instance.size
        except Exception:
            pass
    
    def _refresh_fonts(self, *args):
        """Actualise les polices."""
        try:
            self.title_label.font_name = self.font_body
            self.subtitle_label.font_name = self.font_body
            self.love_btn.font_name = self.font_body
            self.work_btn.font_name = self.font_body
            self.inner_btn.font_name = self.font_body
            self.custom_btn.font_name = self.font_body
            self.custom_input.font_name = self.font_body
            self.validate_btn.font_name = self.font_body
        except Exception:
            pass
    
    def apply_i18n(self, *args):
        """Applique les traductions."""
        try:
            self.title_label.text = self.tr("messages.intention_title")
            self.subtitle_label.text = self.tr("messages.intention_subtitle")
            self.love_btn.text = self.tr("messages.intention_love")
            self.work_btn.text = self.tr("messages.intention_work")
            self.inner_btn.text = self.tr("messages.intention_inner")
            self.custom_btn.text = self.tr("messages.intention_custom")
            self.custom_input.hint_text = self.tr("messages.intention_custom_hint")
            self.validate_btn.text = self.tr("messages.intention_validate")
        except Exception:
            pass
    
    def on_enter(self):
        """Appelé quand l'écran devient visible."""
        # Réinitialise l'écran à chaque visite
        self.selected_intention = None
        self.custom_text = None
        self.custom_input.text = ""
        self.custom_input.opacity = 0
        self.custom_input.disabled = True
        self.validate_btn.disabled = True
        self.validate_btn.opacity = 0.5
        
        # Réinitialise l'apparence des boutons
        for btn in [self.love_btn, self.work_btn, self.inner_btn, self.custom_btn]:
            btn.background_color = [0.3, 0.2, 0.4, 0.9]
        
        # Animation d'entrée
        self.opacity = 1
