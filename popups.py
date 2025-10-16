# -*- coding: utf-8 -*-
"""
Module des popups pour l'application Kivy.
Contient toutes les classes de fenêtres modales (AdPopup, FullScreenCardPopup, LoadingPopup, MmeTChatPopup, AdsPopup).
"""

from __future__ import annotations

import os
import random
import threading
import uuid
import json

# Kivy imports
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from kivy.core.window import Window

# Third-party
import requests

# Local modules
from i18n_loader import (
    MESSAGES,
    tr,
    get_system_language,
)

# Ads manager (local) — import sécurisé car peut échouer en environnement non-Android
try:
    from ads_manager import load_config, AdsManager, maybe_fetch_remote_config
except Exception:
    def load_config():
        return {}

    class AdsManager:  # simple fallback stub
        def __init__(self, cfg):
            self.cfg = cfg

    def maybe_fetch_remote_config(cfg):
        return None

# Gradio client removed for mobile optimization; always use REST fallback via requests
GRADIO_CLIENT_AVAILABLE = False

# Billing manager
try:
    from billing import InAppPurchaseManager
except ImportError:
    InAppPurchaseManager = None

# Constants
DEFAULT_MME_T_SPACE = "https://loupy222-mme-t.hf.space"
MME_T_BACKEND_URL = os.environ.get("MME_T_BACKEND_URL", DEFAULT_MME_T_SPACE)
MME_T_DEFAULT_MODEL = os.environ.get("MME_T_DEFAULT_MODEL", "gpt-3.5-turbo")


class ChatBubble(BoxLayout):
    """Simple chat bubble with rounded background."""

    def __init__(self, text: str, from_user: bool = False, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("spacing", dp(2))
        super().__init__(**kwargs)

        self.from_user = from_user
        self.max_width = dp(260)
        self.padding = (
            [dp(14), dp(9), dp(10), dp(9)] if from_user else [dp(10), dp(9), dp(14), dp(9)]
        )

        # Couleurs style Messenger
        bubble_color = [0.92, 0.92, 0.95, 1]  # Gris clair pour Mme T
        text_color = [0.2, 0.2, 0.2, 1]  # Texte noir
        if from_user:
            bubble_color = [0.35, 0.15, 0.55, 1]  # Violet pour utilisateur
            text_color = [1, 1, 1, 1]  # Texte blanc

        with self.canvas.before:
            self._bg_color = Color(*bubble_color)
            self._bg_rect = RoundedRectangle(radius=[dp(18)] * 4)

        self.label = Label(
            text="",
            font_size="19sp",  # Agrandir la police des messages
            color=text_color,
            halign="left",
            valign="top",
            size_hint=(None, None),
        )
        self.label.bind(texture_size=lambda *_: self._refresh())
        self.add_widget(self.label)

        self.bind(pos=self._update_bg, size=self._update_bg)
        self.set_text(text)

    def set_text(self, text: str) -> None:
        self.label.text = text
        self.label.texture_update()
        self._refresh()

    def set_max_width(self, width: float) -> None:
        try:
            width = float(width)
        except Exception:
            width = self.max_width
        self.max_width = max(dp(160), min(width, dp(360)))
        self._refresh()

    def _refresh(self) -> None:
        self.label.text_size = (self.max_width, None)
        self.label.texture_update()
        label_width, label_height = self.label.texture_size
        self.label.size = (min(label_width, self.max_width), label_height)
        left, top, right, bottom = self.padding
        self.width = self.label.width + left + right
        self.height = self.label.height + top + bottom
        self._update_bg()

    def _update_bg(self, *_args) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class AdPopup(Popup):
    """Popup de publicité"""

    def __init__(self, **kwargs):
        super(AdPopup, self).__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        self.separator_height = 0

        layout = BoxLayout(orientation="vertical", spacing=20, padding=[20, 20, 20, 20])

        # Background
        with layout.canvas.before:
            Color(0.1, 0.15, 0.3, 0.95)
            self.bg_rect = RoundedRectangle(
                pos=layout.pos,
                size=layout.size,
                radius=[15, 15, 15, 15]
            )
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # Titre publicité
        ad_title = Label(
            text=tr("support_app"),  # "Soutenez l'application"
            font_size="20sp",
            color=[0.9, 0.7, 0.3, 1],
            size_hint_y=0.2,
            bold=True,
            halign='center',
            valign='middle',
        )
        ad_title.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.9, None)))
        layout.add_widget(ad_title)

        # Message
        ad_message = Label(
            text=tr("ad_message"),  # Message de soutien
            font_size="16sp",
            color=[1, 1, 1, 1],
            size_hint_y=0.4,
            halign='center',
            valign='middle',
        )
        ad_message.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.85, None)))
        layout.add_widget(ad_message)

        # Zone boutons
        button_layout = BoxLayout(orientation="horizontal", spacing=dp(16), size_hint_y=None, height=dp(50), pos_hint={'center_x': 0.5})

        # Bouton "Plus tard"
        later_btn = Button(
            text=tr("later"),  # "Plus tard"
            size_hint=(0.5, 1),
            font_size="16sp",
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1]
        )
        with later_btn.canvas.before:
            Color(0.5, 0.5, 0.5, 0.8)
            later_btn_bg = RoundedRectangle(pos=later_btn.pos, size=later_btn.size, radius=[25])
        later_btn.bind(pos=lambda i, v: setattr(later_btn_bg, 'pos', v), size=lambda i, v: setattr(later_btn_bg, 'size', v))
        later_btn.bind(on_press=self.close_ad)

        # Bouton "Soutenir"
        support_btn = Button(
            text=tr("support"),  # "Soutenir"
            size_hint=(0.5, 1),
            font_size="16sp",
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            bold=True
        )
        with support_btn.canvas.before:
            Color(0.2, 0.7, 0.2, 1)
            support_btn_bg = RoundedRectangle(pos=support_btn.pos, size=support_btn.size, radius=[25])
        support_btn.bind(pos=lambda i, v: setattr(support_btn_bg, 'pos', v), size=lambda i, v: setattr(support_btn_bg, 'size', v))
        support_btn.bind(on_press=self.open_support)

        button_layout.add_widget(later_btn)
        button_layout.add_widget(support_btn)
        layout.add_widget(button_layout)

        self.content = layout

        # Animation d'entrée
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.3)
        entrance_anim.start(self)

        # Auto-fermeture après 10 secondes
        Clock.schedule_once(self.auto_close, 10)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def close_ad(self, instance):
        print("🎯 Publicité fermée")
        exit_anim = Animation(opacity=0, duration=0.2)
        exit_anim.bind(on_complete=lambda *args: self.dismiss())
        exit_anim.start(self)

    def open_support(self, instance):
        print("💝 Ouverture page de soutien")
        # Ici vous pouvez ajouter le lien vers votre page de soutien
        self.close_ad(instance)

    def auto_close(self, dt):
        print("⏰ Auto-fermeture publicité")
        self.close_ad(None)


class FullScreenCardPopup(Popup):
    """Popup plein écran pour afficher la carte"""

    def __init__(self, card_image_source, card_name, card_state, **kwargs):
        super(FullScreenCardPopup, self).__init__(**kwargs)

        self.title = ""
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.separator_height = 0

        layout = BoxLayout(orientation="vertical", spacing=0)

        with layout.canvas.before:
            Color(0, 0, 0, 0.95)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # Header avec nom et état
        header = BoxLayout(orientation="vertical", size_hint_y=0.15, padding=[20, 10])

        title_label = Label(
            text=card_name,
            font_size="24sp",
            color=[0.9, 0.7, 0.3, 1],
            halign='center',
            valign='middle',
            bold=True
        )
        title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.9, None)))
        header.add_widget(title_label)

        state_label = Label(
            text=card_state,
            font_size="17sp",
            color=[0.8, 0.6, 0.4, 1],
            halign='center',
            valign='middle',
            bold=True
        )
        state_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.9, None)))
        header.add_widget(state_label)
        layout.add_widget(header)

        # Zone carte cliquable
        card_container = FloatLayout(size_hint_y=0.7)

        self.fullscreen_image = Image(
            source=card_image_source,
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )

        close_button = Button(
            text="",
            background_color=[0, 0, 0, 0],
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        close_button.bind(on_press=self.close_fullscreen)

        card_container.add_widget(self.fullscreen_image)
        card_container.add_widget(close_button)
        layout.add_widget(card_container)

        # Footer
        footer = BoxLayout(orientation="vertical", size_hint_y=0.2, padding=[20, 10], spacing=dp(8))
        instruction = Label(
            text=tr("tap_to_return"),  # Au lieu de "Touchez la carte pour revenir"
            font_size="16sp",
            color=[0.7, 0.7, 0.7, 1],
            halign='center',
            valign='middle',
            italic=True
        )
        instruction.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        footer.add_widget(instruction)
        banner_text = random.choice([
            tr("crystals_ad"),
            tr("love_ad"),
            tr("tarot_course_ad"),
        ])
        ad_label = Label(
            text=banner_text,
            font_size="14sp",
            color=[1, 0.85, 0.3, 1],
            halign='center',
            valign='middle',
        )
        ad_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0] * 0.95, None)))
        footer.add_widget(ad_label)
        layout.add_widget(footer)

        self.content = layout

        # Animation d'entrée
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.3)
        entrance_anim.start(self)

    def on_open(self):
        """Masquer les bannières AdMob quand le popup s'ouvre"""
        super().on_open()
        print("📱 FullScreenCardPopup: on_open - Affichage bannière AdMob en bas")

        app = App.get_running_app()
        if hasattr(app, 'ads') and hasattr(app.ads, 'show_banner'):
            app.ads.show_banner()

    def on_dismiss(self):
        """Garder la bannière visible sur ResponseScreen"""
        super().on_dismiss()
        print("📱 FullScreenCardPopup: on_dismiss - Bannière reste visible")

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def close_fullscreen(self, instance):
        exit_anim = Animation(opacity=0, duration=0.2)
        exit_anim.bind(on_complete=lambda *args: self.dismiss())
        exit_anim.start(self)


class LoadingPopup(Popup):
    """Popup de chargement avec animation d'images de dos de cartes"""
    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        self.title = ""
        self.size_hint = (0.7, 0.5)
        self.auto_dismiss = False
        self.separator_height = 0

        layout = BoxLayout(orientation="vertical", spacing=10, padding=[20, 20, 20, 20])

        # Label de chargement
        self.loading_label = Label(
            text=tr("concentrating"),
            font_size="17sp",
            color=[0.9, 0.7, 0.3, 1],
            halign='center',
            valign='middle',
        )
        self.loading_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] * 0.95, None)))
        layout.add_widget(self.loading_label)

        # Zone animation
        self.anim_zone = FloatLayout(size_hint_y=0.8)
        layout.add_widget(self.anim_zone)

        # Deux tas fixes
        self.left_stack = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.05, 'center_y': 0.5},
            opacity=1
        )
        self.right_stack = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.7, 'center_y': 0.5},
            opacity=1
        )
        self.anim_zone.add_widget(self.left_stack)
        self.anim_zone.add_widget(self.right_stack)

        # Carte animée (au départ sur le tas de gauche)
        self.animated_card = Image(
            source="tarot_img/Back.jpg",
            size_hint=(0.25, 0.7),
            pos_hint={'x': 0.05, 'center_y': 0.5},
            opacity=1
        )
        self.anim_zone.add_widget(self.animated_card)

        self.content = layout

        # Lance l'animation
        self.shuffle_direction = "right"
        self.shuffle_anim = None
        self.start_shuffle_animation()

        # Bannière publicitaire pendant le brassage
        ad_choices = ["crystals_ad", "love_ad", "tarot_course_ad"]
        chosen_ad = tr(random.choice(ad_choices))
        self.ad_banner = Label(
            text=chosen_ad,
            font_size="14sp",
            color=[1, 0.82, 0.35, 1],
            size_hint_y=None,
            height=dp(40),
            halign="center",
            valign="middle",
        )
        self.ad_banner.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0] * 0.95, None)))
        layout.add_widget(self.ad_banner)

        Clock.schedule_once(lambda dt: self.update_message(tr("preparing_arcana")), 1.5)
        Clock.schedule_once(lambda dt: self.update_message(tr("drawing_card")), 3)

    def start_shuffle_animation(self):
        # Animation de gauche à droite ou droite à gauche
        if self.shuffle_direction == "right":
            anim = Animation(pos_hint={'x': 0.7, 'center_y': 0.5}, duration=0.4)
            anim.bind(on_complete=lambda *a: self.switch_shuffle_direction())
            anim.start(self.animated_card)
        else:
            anim = Animation(pos_hint={'x': 0.05, 'center_y': 0.5}, duration=0.4)
            anim.bind(on_complete=lambda *a: self.switch_shuffle_direction())
            anim.start(self.animated_card)

    def switch_shuffle_direction(self):
        # Change de direction et relance l'animation
        self.shuffle_direction = "left" if self.shuffle_direction == "right" else "right"
        self.start_shuffle_animation()

    def update_message(self, message):
        self.loading_label.text = message

    def on_dismiss(self):
        # Stoppe l'animation si besoin (optionnel)
        if self.shuffle_anim:
            self.shuffle_anim.cancel_all(self.animated_card)


class MmeTChatPopup(Popup):
    """Fenetre modale modernisée pour la consultation premium avec Mme T."""


    def __init__(
        self,
        language="fr",
        provider="google",
        price_text=None,
        context_text="",
        drawn_cards=None,
        on_session_complete=None,
        **kwargs,
    ):
        kwargs.setdefault("title", "")
        kwargs.setdefault("size_hint", (1, 1))  # Plein écran
        kwargs.setdefault("separator_height", 0)
        super().__init__(**kwargs)

        # Prefer explicit language param; fallback to detected system language.
        try:
            if language:
                self.language = str(language).lower()
            else:
                self.language = get_system_language() or "fr"
        except Exception:
            self.language = "fr"
        self.provider = provider or "google"
        self.price_text = price_text
        self.session_id = str(uuid.uuid4())
        self.backend_url = self._normalize_mme_t_backend_url(MME_T_BACKEND_URL or DEFAULT_MME_T_SPACE)
        self.is_gradio_space = "hf.space" in (self.backend_url or "")
        self.context_text = context_text or ""
        self.conversation_history = []  # Historique [{"role": "user"/"assistant", "content": "..."}]
        self.model_id = MME_T_DEFAULT_MODEL
        self.awaiting_reply = False
        self.typewriter_event = None
        self._typewriter_index = 0
        self._typewriter_source = ""
        self._typewriter_on_complete = None
        self._active_bubble = None
        self.on_session_complete = on_session_complete
        self._close_reason = None
        self.chat_bubbles = []  # type: list[ChatBubble]

        # Animation de chargement
        self._loading_event = None
        self._loading_index = 0
        self._loading_bubble = None

        main_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(12), dp(12), dp(12)],
            spacing=dp(10),
        )

        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.98, 1)  # Fond blanc/gris clair comme Messenger
            self._panel_bg = RoundedRectangle(radius=[dp(20)] * 4)
        main_layout.bind(pos=self._update_panel_bg, size=self._update_panel_bg)

        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8), padding=[dp(8), dp(4)])

        # Bouton retour (gauche)
        back_btn = Button(
            text="←",
            size_hint=(None, None),
            width=dp(44),
            height=dp(44),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[0.35, 0.15, 0.55, 1],
            font_size="26sp",
            bold=True,
        )
        back_btn.bind(on_release=self._manual_close)

        title_label = Label(
            text="Mme T",
            font_size="17sp",
            color=[0.2, 0.2, 0.2, 1],
            halign="center",
            valign="middle",
            bold=True,
        )
        title_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))

        # Espace vide à droite pour équilibrer
        spacer = Label(size_hint=(None, None), width=dp(6), height=dp(44))

        header.add_widget(back_btn)
        header.add_widget(title_label)
        header.add_widget(spacer)

        main_layout.add_widget(header)

        # Miniatures simples sous le header, centrées
        # Prefer drawn_cards passed explicitly to the popup (ensures the
        # backend receives exactly the intended set of cards). Fallback to
        # app.last_drawn_cards if none provided.
        try:
            app = App.get_running_app()
        except Exception:
            app = None

        drawn = drawn_cards if drawn_cards else None
        if not drawn and app:
            drawn = getattr(app, "last_drawn_cards", None)

        slots = []
        if drawn and isinstance(drawn, (list, tuple)) and len(drawn) > 0:
            for item in drawn[:3]:
                try:
                    cname, cstate = item
                except Exception:
                    cname, cstate = item, None
                slots.append((cname, cstate))
        while len(slots) < 3:
            slots.append((None, None))

        self.content = main_layout

        self.status_label = Label(
            text=self._status_prefix(),
            font_size="11sp",
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height=dp(22),
            halign="center",
            valign="middle",
        )
        self.status_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0] * 0.95, val[1])))
        main_layout.add_widget(self.status_label)

        self.response_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=0)
        self.chat_container = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(4), dp(6), dp(4), dp(6)],
        )
        self.chat_container.bind(minimum_height=self.chat_container.setter("height"))
        self.response_scroll.add_widget(self.chat_container)
        main_layout.add_widget(self.response_scroll)

        # Zone de saisie style Messenger
        input_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52), spacing=dp(10), padding=[dp(10), dp(6)])

        self.question_input = TextInput(
            hint_text=self._label("ask_hint"),
            size_hint=(1, None),
            height=dp(40),
            multiline=False,
            background_normal='',
            background_color=[0.94, 0.94, 0.96, 1],
            foreground_color=[0.2, 0.2, 0.2, 1],
            cursor_color=[0.35, 0.15, 0.55, 1],
            padding=[dp(14), dp(10)],
            font_size="15sp",
        )

        self.send_btn = Button(
            text=self._label("send"),
            size_hint=(None, None),
            width=dp(75),
            height=dp(40),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="14sp",
            bold=True,
        )
        with self.send_btn.canvas.before:
            Color(0.35, 0.15, 0.55, 1)
            self.send_btn_bg = RoundedRectangle(pos=self.send_btn.pos, size=self.send_btn.size, radius=[20])
        self.send_btn.bind(pos=lambda i, v: setattr(self.send_btn_bg, 'pos', v), size=lambda i, v: setattr(self.send_btn_bg, 'size', v))
        self.send_btn.bind(on_press=self.on_send_question)

        input_container.add_widget(self.question_input)
        input_container.add_widget(self.send_btn)
        main_layout.add_widget(input_container)

        # Bouton de fermeture en bas
        close_btn_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(45), padding=[dp(10), dp(4)])
        self.close_btn = Button(
            text="✓ " + self._label("done"),
            size_hint=(1, None),
            height=dp(38),
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="13sp",
        )
        with self.close_btn.canvas.before:
            Color(0.2, 0.6, 0.3, 1)
            self.close_btn_bg = RoundedRectangle(pos=self.close_btn.pos, size=self.close_btn.size, radius=[20])
        self.close_btn.bind(pos=lambda i, v: setattr(self.close_btn_bg, 'pos', v), size=lambda i, v: setattr(self.close_btn_bg, 'size', v))
        self.close_btn.bind(on_press=lambda *_: self.dismiss())
        close_btn_container.add_widget(self.close_btn)
        main_layout.add_widget(close_btn_container)

        self.content = main_layout

        self.bind(size=self._update_bubble_widths)
        self.response_scroll.bind(width=self._update_bubble_widths)

        if not self.backend_url:
            self.send_btn.disabled = True
            self.status_label.text = self._label("no_backend")
        else:
            # Use translated introduction text via translations.tr() with the
            # popup language to ensure Mme T receives the preferred language.
            try:
                intro = tr('mme_t_intro', self.language)
            except Exception:
                # Fallback to English literal if translations not available
                intro = "Hello ✨ I'm Mme T, your card reader. What question is on your mind today? How can I help you?"
            self.start_typewriter(intro, sender="mme_t")

    def on_open(self, *args):
        """S'assure que la barre de miniatures reste bien parentée et centrée au moment
        où le popup devient visible (certains parents peuvent reparenter plus tard)."""
        # Call base implementation and then ensure our card bar is parented.
        try:
            super().on_open()
        except Exception:
            # Not critical; continue with debug logging
            pass

        # Debug léger pour vérifier que l'instance ouverte est bien notre popup
        try:
            print(f"[MME_T DEBUG] MmeTChatPopup.on_open id={id(self)} language={self.language}")
            if hasattr(self, 'card_bar'):
                try:
                    print(
                        f"[MME_T DEBUG] card_bar children={len(self.card_bar.children)} size={getattr(self.card_bar, 'size', None)} pos_hint={getattr(self.card_bar, 'pos_hint', None)}"
                    )
                except Exception:
                    pass
        except Exception:
            pass

        # Faire un reparent court après l'ouverture pour garantir la visibilité
        try:
            Clock.schedule_once(self._ensure_card_bar, 0.02)
        except Exception:
            print("[MME_T DEBUG] Failed to schedule _ensure_card_bar")

    # Pas d'overlay fallback — card_anchor prend la largeur du contenu.

    # overlay fallback removed — centrer dans la popup via card_anchor

    def on_dismiss(self, *_args):
        # appeler le on_dismiss original
        try:
            super().on_dismiss()
        except Exception:
            pass

    def _ensure_card_bar(self, dt):
        """Assure que la barre de miniatures est bien insérée sous le header et centrée.
        Cette méthode est planifiée juste après l'ouverture du popup pour contrer
        d'éventuels reparentings effectués par d'autres parties du code."""
        try:
            print(f"[MME_T DEBUG] _ensure_card_bar called id={id(self)}")
            if not hasattr(self, 'card_bar') or not hasattr(self, 'card_anchor'):
                print("[MME_T DEBUG] No card_bar/card_anchor present")
                return

            # Si content est un BoxLayout, on essaye d'insérer la card_anchor juste après le header
            if hasattr(self, 'content') and isinstance(self.content, BoxLayout):
                try:
                    # Vérifier si card_anchor est déjà dedans
                    if self.card_anchor.parent is not self.content:
                        # Retirer d'un parent précédent si besoin
                        try:
                            if self.card_anchor.parent:
                                self.card_anchor.parent.remove_widget(self.card_anchor)
                        except Exception:
                            pass
                        # Insérer à l'index 1 (après header) si possible
                        try:
                            self.content.add_widget(self.card_anchor, index=1)
                            print("[MME_T DEBUG] card_anchor added at index=1")
                        except Exception:
                            try:
                                self.content.add_widget(self.card_anchor)
                                print("[MME_T DEBUG] card_anchor added at end")
                            except Exception as e:
                                print(f"[MME_T DEBUG] Failed to add card_anchor: {e}")
                except Exception:
                    # Sécurité : ne pas faire échouer l'ensemble si un problème interne survient
                    print("[MME_T DEBUG] exception while handling content/card_anchor")

            # Forcer pos_hint/center pour la barre
            try:
                self.card_bar.pos_hint = {'center_x': 0.5}
            except Exception:
                pass

            # Log final state
            try:
                print(f"[MME_T DEBUG] card_bar parent={getattr(self.card_bar, 'parent', None)} children={len(self.card_bar.children)} size={getattr(self.card_bar, 'size', None)}")
            except Exception:
                pass

            # Schedule a deeper layout dump a tick later when positions are resolved
            try:
                Clock.schedule_once(self._dump_layout_state, 0.01)
            except Exception:
                pass
        except Exception as e:
            print(f"[MME_T DEBUG] _ensure_card_bar exception: {e}")

    def _dump_layout_state(self, dt):
        """Imprime l'état de `self.content` et les positions absolues des widgets clés.
        Utile pour diagnostiquer pourquoi la barre n'apparait pas à l'écran à l'endroit attendu."""
        try:
            if not hasattr(self, 'content'):
                print("[MME_T DEBUG] _dump_layout_state: no content")
                return
            print("[MME_T DEBUG] ---- Dump layout state ----")
            try:
                for idx, child in enumerate(list(self.content.children)):
                    info = f"idx={idx} class={child.__class__.__name__} size={getattr(child, 'size', None)} pos={getattr(child, 'pos', None)}"
                    print(f"[MME_T DEBUG] content_child: {info}")
            except Exception as e:
                print(f"[MME_T DEBUG] error listing content children: {e}")

            # card_anchor and card_bar absolute position
            try:
                if hasattr(self, 'card_anchor'):
                    ca = self.card_anchor
                    print(f"[MME_T DEBUG] card_anchor size={ca.size} pos={ca.pos}")
                    try:
                        wx, wy = ca.to_window(ca.x, ca.y)
                        print(f"[MME_T DEBUG] card_anchor to_window={wx, wy}")
                    except Exception:
                        pass
                if hasattr(self, 'card_bar'):
                    cb = self.card_bar
                    print(f"[MME_T DEBUG] card_bar size={cb.size} pos={cb.pos}")
                    try:
                        wx, wy = cb.to_window(cb.x, cb.y)
                        print(f"[MME_T DEBUG] card_bar to_window={wx, wy}")
                    except Exception:
                        pass
            except Exception as e:
                print(f"[MME_T DEBUG] error dumping positions: {e}")
            print("[MME_T DEBUG] ---- End dump ----")
        except Exception as e:
            print(f"[MME_T DEBUG] _dump_layout_state exception: {e}")

        

    def _status_prefix(self):
        base = {
            "fr": "Merci pour votre soutien",
            "en": "Thank you for your support",
            "es": "Gracias por tu apoyo",
            "pt": "Obrigada pelo teu apoio",
        }.get(self.language, "Merci pour votre soutien")
        provider_label = {
            "google": "Google Play",
            "amazon": "Amazon Appstore",
        }.get(self.provider, "")
        return f"{base}{' - ' + provider_label if provider_label else ''}"

    def _label(self, key, **kwargs):
        # Try centralized translations first (translations.tr)
        try:
            txt = tr(key, **kwargs)
            # tr() may return the key itself when missing; only use if different
            if txt and txt != key:
                return txt
        except Exception:
            pass

        labels = {
            # 'send' short label kept below; long variant removed to avoid duplication
            "ask_hint": {
                "fr": "Ta question...",
                "en": "Your question...",
                "es": "Tu pregunta...",
                "pt": "A tua questao...",
            },
            "send": {
                "fr": "Envoyer",
                "en": "Send",
                "es": "Enviar",
                "pt": "Enviar",
            },
            "sending": {
                "fr": "Connexion...",
                "en": "Connecting...",
                "es": "Conectando...",
                "pt": "A ligar...",
            },
            "connecting": {
                "fr": "Mme T arrive dans quelques instants...",
                "en": "Mme T will be here in a moment...",
                "es": "Mme T llegara en unos momentos...",
                "pt": "Mme T chegara em breve...",
            },
            "no_backend": {
                "fr": "Service indisponible : configurez MME_T_BACKEND_URL.",
                "en": "Service unavailable: configure MME_T_BACKEND_URL.",
            },
            "error": {
                "fr": "Mme T est indisponible. Verifie ta connexion et reessaie.",
                "en": "Mme T is unavailable. Check your connection and try again.",
                "es": "Mme T no esta disponible. Verifica tu conexion e intentalo de nuevo.",
                "pt": "Mme T esta indisponivel. Verifica a tua ligacao e tenta novamente.",
            },
            "done": {
                "fr": "Consultation terminee",
                "en": "Reading complete",
                "es": "Lectura completada",
                "pt": "Consulta concluida",
            },
                # quick controls removed: show_all / copy
            }
        bundle = labels.get(key, {})
        # Prefer French fallback, then English. Returning empty string only as last resort.
        return bundle.get(self.language, bundle.get("fr", bundle.get("en", "")))

    def _on_show_all(self):
        """Afficher immédiatement la réponse complète (arrête l'effet machine à écrire)."""
        # Si une machine à écrire est active, finaliser
        if self.typewriter_event:
            # Forcer la finalisation
            try:
                self.typewriter_event.cancel()
            except Exception:
                pass
            self.typewriter_event = None
            if self._active_bubble:
                self._active_bubble.set_text(self._typewriter_source)
                self._active_bubble = None
    def _on_copy_latest(self):
        """Copie la dernière réponse (assistant) dans le presse-papiers."""
        # Trouver la dernière réponse dans l'historique (assistant)
        last = None
        for entry in reversed(self.conversation_history):
                if entry.get("role") == "assistant":
                    last = entry.get("content")
                    break
        if not last:
            return
        try:
            Clipboard.copy(last)
            print("📋 Réponse copiée dans le presse-papiers")
        except Exception as e:
            print(f"⚠️ Échec copie presse-papiers: {e}")

    def _manual_close(self, *_args):
        self._close_reason = "manual"
        self.dismiss()

    def _update_panel_bg(self, instance, _value):
        if hasattr(self, "_panel_bg") and self._panel_bg:
            self._panel_bg.pos = instance.pos
            self._panel_bg.size = instance.size

    def _bubble_max_width(self) -> float:
        available = self.response_scroll.width - dp(56) if self.response_scroll else self.width * 0.7
        if available <= 0:
            available = self.width * 0.72
        return max(dp(180), min(available, self.width * 0.85))

    def _update_bubble_widths(self, *_args):
        if not self.chat_bubbles:
            return
        max_width = self._bubble_max_width()
        for bubble in self.chat_bubbles:
            bubble.set_max_width(max_width)

    def start_typewriter(self, text: str, sender: str = "mme_t", speed: float = 0.02, on_complete=None):
        if self.typewriter_event:
            self.typewriter_event.cancel()
            self.typewriter_event = None
        self._typewriter_source = text or ""
        self._typewriter_index = 0
        self._typewriter_on_complete = on_complete
        self._active_bubble = self._create_message_bubble("", sender)
        self._update_bubble_widths()
        # Do not scroll immediately; we'll scroll once when typing finishes.
        self._typewriter_scroll_throttle = 6
        if not self._typewriter_source:
            self._finalize_typewriter()
            return
        self.typewriter_event = Clock.schedule_interval(lambda dt: self._advance_typewriter(), speed)

    def add_message(self, text: str, sender: str) -> None:
        bubble = self._create_message_bubble(text, sender)
        bubble.set_text(text)
        self._update_bubble_widths()
        # Scroll to completed message
        self._scroll_to_widget(bubble)

    def _advance_typewriter(self):
        if self._typewriter_index >= len(self._typewriter_source):
            self._finalize_typewriter()
            return False
        self._typewriter_index += 1
        if self._active_bubble:
            self._active_bubble.set_text(self._typewriter_source[: self._typewriter_index])
            # Avoid scrolling while typing; final scroll happens in _finalize_typewriter
        return True

    def _finalize_typewriter(self):
        if self.typewriter_event:
            self.typewriter_event.cancel()
            self.typewriter_event = None
        if self._active_bubble:
            self._active_bubble.set_text(self._typewriter_source)
            try:
                self._scroll_to_widget(self._active_bubble)
            except Exception:
                pass
            self._active_bubble = None
        if self._typewriter_on_complete:
            callback = self._typewriter_on_complete
            self._typewriter_on_complete = None
            Clock.schedule_once(lambda _dt: callback(), 0)
        return False

    def _create_message_bubble(self, text: str, sender: str):
        from_user = sender == "user"
        anchor = AnchorLayout(
            size_hint=(1, None),
            anchor_x="right" if from_user else "left",
            anchor_y="center",
            padding=[dp(6), 0, dp(6), 0],
        )
        bubble = ChatBubble(text, from_user=from_user)
        bubble.set_max_width(self._bubble_max_width())
        anchor.add_widget(bubble)
        anchor.height = bubble.height + dp(4)
        bubble.bind(size=lambda _inst, val: setattr(anchor, "height", val[1] + dp(4)))
        # Add widget but do not force a scroll here; callers decide when to scroll
        self.chat_container.add_widget(anchor)
        self.chat_bubbles.append(bubble)
        return bubble

    def _scroll_to_widget(self, widget):
        # Debounced scroll: cancel any pending scroll and schedule a single
        # scroll shortly after. This helps avoid the chat area jumping up and
        # down when many updates occur rapidly (typewriter, loading messages, etc.).
        if not self.response_scroll:
            return
        try:
            if hasattr(self, '_pending_scroll_event') and self._pending_scroll_event:
                try:
                    self._pending_scroll_event.cancel()
                except Exception:
                    pass
            self._pending_scroll_event = Clock.schedule_once(lambda _dt: self.response_scroll.scroll_to(widget), 0.12)
        except Exception:
            try:
                Clock.schedule_once(lambda _dt: self.response_scroll.scroll_to(widget), 0.12)
            except Exception:
                pass

    def _start_loading_animation(self):
        """Démarre l'animation de chargement avec messages rotatifs"""
        self._loading_index = 0

        # Récupérer les messages de chargement selon la langue
        loading_messages = MESSAGES.get(self.language, MESSAGES["fr"]).get("loading_messages", [
            "🔮 Je me concentre sur ta question...",
            "🃏 Mélange des cartes en cours...",
            "✨ Les énergies s'alignent...",
            "🌙 Consultation des astres...",
            "💫 Interprétation des arcanes...",
        ])

        # Créer la bulle de chargement
        self._loading_bubble = self._create_message_bubble(loading_messages[0], sender="mme_t")

        def _update_loading_message(dt):
            if not self._loading_bubble or not self.awaiting_reply:
                return False  # Arrêter l'animation

            self._loading_index = (self._loading_index + 1) % len(loading_messages)
            new_text = loading_messages[self._loading_index]

            # Mettre à jour le texte de la bulle
            if hasattr(self._loading_bubble, 'label'):
                self._loading_bubble.label.text = new_text

            return True  # Continuer l'animation

        # Changer le message toutes les 2 secondes
        self._loading_event = Clock.schedule_interval(_update_loading_message, 2.0)

    def _stop_loading_animation(self):
        """Arrête et supprime l'animation de chargement"""
        if self._loading_event:
            self._loading_event.cancel()
            self._loading_event = None

        # Supprimer la bulle de chargement
        if self._loading_bubble:
            # Trouver le parent (anchor) de la bulle
            for child in self.chat_container.children:
                if isinstance(child, AnchorLayout):
                    for bubble_widget in child.children:
                        if bubble_widget == self._loading_bubble:
                            self.chat_container.remove_widget(child)
                            if self._loading_bubble in self.chat_bubbles:
                                self.chat_bubbles.remove(self._loading_bubble)
                            break
            self._loading_bubble = None

    def on_send_question(self, *_args):
        if self.awaiting_reply or not self.backend_url:
            return
        question = self.question_input.text.strip()
        if not question:
            return

        # LOG: Afficher la question dans le terminal
        print(f"\n{'='*60}")
        print("👤 QUESTION UTILISATEUR:")
        print(f"   {question}")
        print(f"{'='*60}\n")

        # Afficher le message utilisateur
        self.add_message(question, sender="user")
        self.question_input.text = ""
        self.question_input.disabled = True
        self.send_btn.disabled = True

        # Afficher "Mme T arrive dans quelques instants..."
        self.status_label.text = self._label("connecting")

        # Démarrer l'animation de chargement
        self._start_loading_animation()

        # Attendre 2.5 secondes avant de vraiment envoyer (effet humain)
        def _delayed_send():
            self.awaiting_reply = True
            self.send_btn.text = "..."

            # Ajouter la question à l'historique
            self.conversation_history.append({"role": "user", "content": question})

            # Construire le contexte complet avec l'historique
            full_context = self.context_text
            if len(self.conversation_history) > 1:  # Si on a déjà des échanges
                history_text = "\n\nHistorique de la conversation:\n"
                # Prendre tous les échanges sauf la question actuelle
                for entry in self.conversation_history[:-1]:
                    role = "Vous" if entry["role"] == "user" else "Mme T"
                    history_text += f"{role}: {entry['content']}\n"
                full_context = full_context + history_text

            print(f"[MME T DEBUG] Contexte envoyé (avec historique):\n{full_context}\n")

            payload = {
                "message": question,
                "language": self.language,
                "session_id": self.session_id,
                "model": self.model_id,
                "context": full_context,
            }
            threading.Thread(target=self._perform_request, args=(payload,), daemon=False).start()

        Clock.schedule_once(lambda dt: _delayed_send(), 2.5)

    def _perform_request(self, payload):
        try:
            if self.is_gradio_space:
                reply = self._call_gradio_backend(payload["message"], payload.get("context") or "")
            else:
                url = self.backend_url.rstrip("/") + "/chat"
                response = requests.post(url, json=payload, timeout=15)  # Réduit de 25 à 15s
                response.raise_for_status()
                data = response.json()
                reply = (data.get("reply") or "").strip()
                if not reply:
                    raise ValueError("Réponse vide")

            # LOG: Afficher la réponse dans le terminal
            print(f"\n{'='*60}")
            print("🔮 RÉPONSE MME T:")
            print(f"   {reply}")
            print(f"{'='*60}\n")

            Clock.schedule_once(lambda dt: self._on_success(reply), 0)
        except Exception as e:
            print(f"\n{'='*60}")
            print("❌ ERREUR MME T:")
            print(f"   {str(e)}")
            print(f"{'='*60}\n")
            Clock.schedule_once(lambda dt: self._on_error(), 0)

    def _on_success(self, reply_text):
        # Arrêter l'animation de chargement
        self._stop_loading_animation()

        # Ajouter la réponse à l'historique
        self.conversation_history.append({"role": "assistant", "content": reply_text})

        self.awaiting_reply = False
        # Réactiver les champs pour permettre la conversation continue
        self.question_input.disabled = False
        self.send_btn.disabled = False
        self.send_btn.text = self._label("send")
        # Message encourageant à continuer la discussion
        continue_texts = {
            "fr": "Tu peux me poser d'autres questions sur cette lecture...",
            "en": "You can ask me more about this reading...",
            "es": "Puedes preguntarme más sobre esta lectura...",
            "pt": "Podes perguntar-me mais sobre esta leitura...",
            "de": "Du kannst mich mehr über diese Legung fragen...",
            "it": "Puoi chiedermi di più su questa lettura...",
        }
        self.status_label.text = continue_texts.get(self.language, continue_texts["fr"])
        self.start_typewriter(reply_text, sender="mme_t")

    def _schedule_session_close(self):
        # Cette fonction n'est plus appelée automatiquement
        # L'utilisateur ferme manuellement ou via un bouton
        if self._close_reason == "completed":
            return
        self._close_reason = "completed"
        Clock.schedule_once(lambda _dt: self.dismiss(), 1.5)

    def _on_error(self):
        # Arrêter l'animation de chargement
        self._stop_loading_animation()

        self.awaiting_reply = False
        self.send_btn.disabled = False
        self.send_btn.text = self._label("send")
        self.question_input.disabled = False
        self.status_label.text = self._label("error")
        self.start_typewriter(self._label("error"), sender="mme_t")

    def _call_gradio_backend(self, message: str, context_text: str) -> str:
        """Appelle le backend Gradio avec le client officiel ou REST en fallback"""

        # LOG: Afficher les paramètres envoyés
        print(f"\n{'='*60}")
        print("📤 ENVOI AU BACKEND:")
        print(f"   Message: {message}")
        print(f"   Contexte: {context_text or '(vide)'}")
        print(f"   URL: {self.backend_url}")
        print(f"{'='*60}\n")

        # Méthode 1: REST API (Gradio moderne avec SSE)
        base_url = (self.backend_url or "").rstrip("/")
        print(f"🔗 Tentative de connexion REST à: {base_url}")

        # Réveil du backend (requis pour Hugging Face Spaces)
        try:
            wake_response = requests.get(base_url, timeout=15)
            print(f"✅ Backend réveillé : {wake_response.status_code}")
        except Exception as wake_exc:
            print(f"⚠️ Réveil backend échoué: {wake_exc}")

        # Payload Gradio pour la fonction consulter_madame_t(message, contexte)
        payload = {
            "data": [message, context_text or ""]
        }

        print("🔄 Utilisation de l'API Gradio moderne avec SSE...")

        try:
            # Endpoint Gradio moderne
            api_url = f"{base_url}/gradio_api/call/predict"
            print(f"📡 Requête vers: {api_url}")

            # Envoyer la requête
            response = requests.post(api_url, json=payload, timeout=30)
            response.raise_for_status()

            event_data = response.json()
            event_id = event_data.get("event_id")
            if not event_id:
                raise ValueError("Aucun event_id reçu")

            print(f"📋 Event ID: {event_id}")

            # Écouter les événements SSE
            sse_url = f"{api_url}/{event_id}"
            print(f"🎧 Écoute SSE: {sse_url}")

            sse_response = requests.get(sse_url, stream=True, timeout=60)

            full_response = ""
            for line in sse_response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    print(f"SSE: {line_str}")  # Debug
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Enlever 'data: '
                            if isinstance(data, list) and data:
                                result = data[0]
                                if isinstance(result, str) and result.strip():
                                    full_response = result.strip()
                                    print(f"✅ Réponse SSE reçue ({len(full_response)} caractères)")
                                    return full_response
                        except json.JSONDecodeError:
                            continue
                    elif line_str == 'event: complete':
                        print("🔄 Événement complete reçu, attente de données...")
                        continue  # Continue reading for data

            if full_response:
                return full_response
            else:
                raise ValueError("Aucune réponse valide reçue via SSE")

        except Exception as sse_exc:
            print(f"⚠️ Échec SSE: {sse_exc}")
            print("🔄 Basculement vers anciens endpoints REST...")

        # Méthode 3: Anciens endpoints REST (fallback)
        endpoints = [
            "/predict",
            "/call/consulter_btn",
            "/api/consulter_madame_t",
            "/api/predict",
            "/run/predict",
        ]

        for endpoint in endpoints:
            try:
                full_url = f"{base_url}{endpoint}"
                print(f"📡 Tentative {endpoint}: {full_url}")

                response = requests.post(full_url, json=payload, timeout=20)
                print(f"📊 Status: {response.status_code}")

                if response.status_code == 404:
                    print(f"❌ Endpoint {endpoint} non trouvé, passage au suivant...")
                    continue

                response.raise_for_status()
                data = response.json()
                print(f"📥 Réponse reçue: {str(data)[:300]}")

                # Gradio retourne {"data": [result]}
                if isinstance(data, dict):
                    outputs = data.get("data")
                    if isinstance(outputs, list) and outputs:
                        result = outputs[0]
                        if isinstance(result, str) and result.strip():
                            print(f"✅ Réponse valide de Mme T ({len(result)} caractères)")
                            return result.strip()

                print(f"⚠️ Format de réponse inattendu: {type(data)}")

            except requests.exceptions.Timeout:
                print(f"⏰ Timeout sur {endpoint} après 20s, passage au suivant...")
                continue
            except requests.exceptions.ConnectionError:
                print(f"🌐 Erreur de connexion sur {endpoint}, passage au suivant...")
                continue
            except requests.exceptions.HTTPError as http_err:
                print(f"✗ HTTP Error sur {endpoint}: {http_err}")
                if response.status_code != 404:
                    raise
            except Exception as exc:
                print(f"✗ Erreur sur {endpoint}: {type(exc).__name__}: {exc}")
                if endpoint == endpoints[-1]:  # Dernier essai
                    raise

        raise RuntimeError(f"Aucun endpoint Gradio valide trouvé sur {base_url}")

    def _extract_space_id(self, url: str) -> str:
        """Extrait l'ID du Space depuis l'URL (ex: Loupy222/mme_t)"""
        if not url:
            return ""

        # Format: https://loupy222-mme-t.hf.space -> Loupy222/mme_t
        if ".hf.space" in url:
            domain = url.split("//")[-1].split(".hf.space")[0]
            parts = domain.split("-", 1)
            if len(parts) >= 2:
                owner = parts[0].capitalize()
                space = parts[1].replace("-", "_")
                return f"{owner}/{space}"

        # Format direct: Loupy222/mme_t
        if "/" in url and "http" not in url:
            return url.strip()

        return ""

    def _normalize_mme_t_backend_url(self, url: str) -> str:
        """Normalise l'URL du backend Mme T"""
        if not url:
            return ""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def on_dismiss(self, *_args):
        if self.typewriter_event:
            self.typewriter_event.cancel()
            self.typewriter_event = None
        self._active_bubble = None
        self._typewriter_on_complete = None
        self.chat_bubbles.clear()
        if self._close_reason == "completed" and self.on_session_complete:
            Clock.schedule_once(lambda _dt: self.on_session_complete(), 0)
        self._close_reason = None


class AdsPopup(Popup):
    def __init__(self, on_close_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.size_hint = (1, 1)  # Plein écran
        self.auto_dismiss = False
        self.separator_height = 0
        self.on_close_callback = on_close_callback

        layout = BoxLayout(orientation="vertical", spacing=dp(20), padding=dp(30))

        # Fond sombre pour publicité
        with layout.canvas.before:
            Color(0.12, 0.08, 0.18, 0.98)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda i, v: setattr(self.bg_rect, 'pos', v), size=lambda i, v: setattr(self.bg_rect, 'size', v))

        # Bandeau promotion traduit
        ad_choices = [
            tr("crystals_ad"),
            tr("love_ad"),
            tr("tarot_course_ad"),
        ]
        chosen_ad = random.choice(ad_choices)

        promo = Label(
            text=chosen_ad,
            font_size="22sp",
            color=[1, 0.88, 0.4, 1],
            halign="center",
            valign="middle",
            size_hint=(1, 0.5),
            bold=True,
        )
        promo.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val * 0.85, None))
        )
        layout.add_widget(promo)

        self.countdown_seconds = 30
        btn_text = tr("new_reading_countdown", seconds=self.countdown_seconds)
        self.next_btn = Button(
            text=btn_text,
            size_hint=(0.75, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=[0, 0, 0, 0],
            color=[1, 1, 1, 1],
            font_size="17sp",
            bold=True,
            disabled=True
        )
        with self.next_btn.canvas.before:
            Color(0.6, 0.4, 0.2, 1.0)
            self.btn_bg = RoundedRectangle(
                pos=self.next_btn.pos,
                size=self.next_btn.size,
                radius=[25, 25, 25, 25]
            )
        self.next_btn.bind(pos=self.update_btn_canvas, size=self.update_btn_canvas)
        self.next_btn.bind(on_press=self.close_popup)
        layout.add_widget(self.next_btn)

        self.content = layout
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

    def update_btn_canvas(self, instance, value):
        self.btn_bg.pos = instance.pos
        self.btn_bg.size = instance.size

    def update_countdown(self, dt):
        self.countdown_seconds -= 1
        if self.countdown_seconds > 0:
            self.next_btn.text = tr("new_reading_countdown", seconds=self.countdown_seconds)
        else:
            self.next_btn.text = tr("new_reading")
            self.next_btn.disabled = False
            if self.countdown_event:
                self.countdown_event.cancel()

    def close_popup(self, instance):
        self.dismiss()
        if self.on_close_callback:
            self.on_close_callback()