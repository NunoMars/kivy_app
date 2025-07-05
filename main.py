__version__ = "0.01"

import os
import random

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.core.window import Window
import math

from signification import cards_signification


class AutoScrollLabel(Label):
    """Label avec scroll automatique au survol/touch"""
    def __init__(self, **kwargs):
        super(AutoScrollLabel, self).__init__(**kwargs)
        self.scroll_animation = None
        self.parent_scroll = None
        
    def on_parent(self, instance, parent):
        """Trouve le ScrollView parent"""
        if parent:
            current = parent
            while current and not isinstance(current, ScrollView):
                current = current.parent
            self.parent_scroll = current
    
    def on_touch_down(self, touch):
        """Démarre le scroll automatique au touch/clic"""
        if self.collide_point(*touch.pos) and self.parent_scroll:
            self.start_auto_scroll()
            return True
        return super(AutoScrollLabel, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Arrête le scroll automatique"""
        if self.scroll_animation:
            self.scroll_animation.cancel(self.parent_scroll)
            self.scroll_animation = None
        return super(AutoScrollLabel, self).on_touch_up(touch)
    
    def start_auto_scroll(self):
        """Démarre l'animation de scroll automatique"""
        if not self.parent_scroll:
            return
            
        # Calculer si on peut scroller
        content_height = self.texture_size[1]
        viewport_height = self.parent_scroll.height
        
        if content_height > viewport_height:
            # Animation de scroll de haut en bas puis retour
            self.scroll_animation = Animation(scroll_y=0, duration=3)
            self.scroll_animation += Animation(scroll_y=1, duration=3)
            self.scroll_animation.repeat = True
            self.scroll_animation.start(self.parent_scroll)


class RootScreen(ScreenManager):
    pass


class CardScreen(Screen):
    """Ecran principal de l'application"""

    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)

    def draw_card(self):
        """Déclenche le tirage d'une carte depuis l'écran d'accueil avec animation"""
        # Animation du bouton avant le tirage
        self.animate_draw_button()
        
        # Récupérer l'écran de réponse
        response_screen = self.manager.get_screen("response_screen")
        
        # Déclencher le chargement des données avec popup après l'animation
        Clock.schedule_once(lambda dt: response_screen.show_loading_popup(), 0.8)
        
        # Changer d'écran après un délai pour permettre au popup de s'afficher
        Clock.schedule_once(lambda dt: self.switch_to_response(), 0.9)
    
    def animate_draw_button(self):
        """Anime le bouton de tirage de carte"""
        # Essayer de trouver le bouton de tirage dans le fichier .kv
        try:
            # Animation de pulsation magique simple
            button = self.ids.get('draw_button')  # Assumons que le bouton a cet ID
            if button:
                # Animation magique : pulsation d'opacité
                magic_pulse = Animation(opacity=0.5, duration=0.2)
                magic_pulse += Animation(opacity=1, duration=0.2)
                magic_pulse += Animation(opacity=0.7, duration=0.2)
                magic_pulse += Animation(opacity=1, duration=0.2)
                
                magic_pulse.start(button)
                
                print("Animation du bouton de tirage lancée")
        except Exception as e:
            print(f"Erreur animation bouton: {e}")
    
    def switch_to_response(self):
        """Change vers l'écran de réponse"""
        self.manager.current = "response_screen"


class LoadingPopup(Popup):
    def __init__(self, show_ad=True, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        self.title = "JE TIRE UNE CARTE..."
        # Style du titre pour correspondre au nom de la carte
        self.title_color = [0.6, 0.4, 0.2, 1.0]  # Marron comme le nom de la carte
        self.title_size = "22sp"  # Même taille que le nom de la carte
        self.background = "tarot_img/bg.jpg"
        
        content_layout = BoxLayout(orientation="vertical", spacing=10, padding=[10, 10, 10, 10])
        
        # Ajout de la pub en haut (si demandée)
        if show_ad:
            ad_layout = self.create_ad_banner()
            if ad_layout:
                content_layout.add_widget(ad_layout)
        
        # GIF de la carte au centre
        gif_path = os.path.join(os.path.dirname(__file__), "tarot_img", "carte-unscreen.gif")
        animated_card = Image(source=gif_path, anim_delay=0.05, size_hint=(1, 0.8))  # Animation plus rapide
        
        # Ajouter une animation de pulsation d'opacité seulement
        pulse_anim = Animation(opacity=0.7, duration=1)
        pulse_anim += Animation(opacity=1, duration=1)
        pulse_anim.repeat = True
        pulse_anim.start(animated_card)
        
        content_layout.add_widget(animated_card)
        
        # Message d'attente en bas avec animation
        waiting_label = Label(
            text="Concentration en cours...",
            size_hint=(1, 0.1),
            font_size="14sp",
            color=[0.6, 0.4, 0.2, 1.0],
            halign='center'
        )
        
        # Animation pulsante pour le texte (sans font_size pour éviter les erreurs)
        pulse_text = Animation(opacity=0.7, duration=0.8)
        pulse_text += Animation(opacity=1.0, duration=0.8)
        pulse_text.repeat = True
        pulse_text.start(waiting_label)
        
        content_layout.add_widget(waiting_label)
        
        self.content = content_layout
    
    def create_ad_banner(self):
        """Crée une bannière publicitaire discrète"""
        # Pour l'instant, simulation d'une pub simple
        # En production, ici vous intégreriez AdMob, etc.
        
        # Simulation d'une pub thématique simple
        ad_label = Label(
            text="💎 Boutique Cristaux & Minéraux - Livraison gratuite 💎",
            font_size="12sp",
            color=[0.4, 0.3, 0.6, 1.0],  # Violet discret
            halign='center',
            size_hint=(1, 0.15),
            text_size=(None, None)
        )
        
        return ad_label


class FullScreenImagePopup(BoxLayout):
    def __init__(self, image_path, **kwargs):
        super(FullScreenImagePopup, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.image = Image(source=image_path, size_hint=(1, 1))
        self.add_widget(self.image)
        
        # Animation subtile de l'image (léger changement d'opacité)
        zoom_anim = Animation(opacity=0.8, duration=2)
        zoom_anim += Animation(opacity=1, duration=2)
        zoom_anim.repeat = True
        
        # Démarrer l'animation après un petit délai
        Clock.schedule_once(lambda dt: zoom_anim.start(self.image), 0.5)


class CardResponseScreen(Screen):
    """Ecran de réponse de l'application"""

    def __init__(self, **kwargs):
        super(CardResponseScreen, self).__init__(**kwargs)
        self.path = "tarot_img/MajorArcanaCards"
        self.cards = list(cards_signification.keys())
        self.states = ["a l'endroit", "a l'envers"]
        self.card_name = None
        self.card_state = None
        self.states_label = None
        self.card_text = None
        self.card_image = None

    def on_kv_post(self, base_widget):
        # Link Python attributes to widgets defined in the .kv file by their ids
        self.card_name = self.ids.get("card_name")
        self.card_state = self.ids.get("card_state")
        self.states_label = self.ids.get("states_label")
        self.card_text = self.ids.get("card_text")
        self.card_image = self.ids.get("card_image")

    def on_enter(self, *args):
        # Le popup est maintenant déclenché depuis CardScreen.draw_card()
        # Donc on ne fait rien ici pour éviter les doublons
        pass

    def show_loading_popup(self):
        # Vérifier si l'utilisateur est premium (pour l'instant simulé)
        is_premium = False  # À remplacer par la vraie logique premium
        
        # Afficher la pub seulement pour les utilisateurs gratuits
        show_ad = not is_premium
        
        self.loading_popup = LoadingPopup(show_ad=show_ad)
        self.loading_popup.open()
        Clock.schedule_once(
            self.load_card_data, 3
        )  # Appeler load_card_data après un court délai

    def load_card_data(self, dt):
        """Charge les données de la carte après un court délai simulé (0.1 seconde)"""
        try:
            self.drawn_card = random.choice(self.cards)
            self.state = random.choice(self.states)
            
            # Affichage séparé du nom de la carte et de son état
            if self.card_name is not None:
                self.card_name.text = self.drawn_card
            if self.card_state is not None:
                if self.state == "a l'envers":
                    self.card_state.text = "⬇ À L'ENVERS ⬇"
                else:
                    self.card_state.text = "⬆ À L'ENDROIT ⬆"
                    
            if self.states_label is not None:
                keywords = str(cards_signification[self.drawn_card][self.state])
                self.states_label.text = keywords.upper()  # Mots-clés en MAJUSCULES pour plus d'impact

            if self.state == "a l'envers":
                image_file_name = f"{self.drawn_card} {self.state}.jpg"
            else:
                image_file_name = f"{self.drawn_card}.jpg"
            image_path = os.path.join(
                self.path, image_file_name
            )  # Construct full path

            # Print the image path for debugging
            # print("Image Path:", image_path)

            if os.path.exists(image_path):
                if self.card_image is not None:
                    self.card_image.source = image_path
                    self.card_image.bind(
                        on_touch_down=self.on_image_click
                    )  # Bind the touch event
                else:
                    print("card_image is None, cannot set source.")
            else:
                print("Image not found:", image_path)

            if self.card_text is not None:
                self.card_text.text = str(
                    cards_signification[self.drawn_card][
                        f"signification {self.state}"
                    ]
                )
        except Exception as e:
            # Handle any exceptions and print the error message
            print("Error loading card data:", e)

        self.loading_popup.dismiss()  # Close the loading popup
        
        # Ajouter des animations d'apparition pour les éléments
        self.animate_card_appearance()

    def reset(self):
        """Réinitialise l'écran de réponse pour un nouveau tirage"""
        if self.card_name is not None:
            self.card_name.text = ""
        if self.card_state is not None:
            self.card_state.text = ""
        if self.states_label is not None:
            self.states_label.text = ""
        if self.card_text is not None:
            self.card_text.text = ""
        if self.card_image is not None:
            self.card_image.source = "tarot_img/Back.jpg"
        if hasattr(self, "full_screen_popup"):
            self.remove_widget(self.full_screen_popup)
            del self.full_screen_popup

    def on_image_click(self, instance, touch):
        """Affiche l'image en plein écran si l'utilisateur clique dessus avec animation"""
        if self.card_image is not None and self.card_image.collide_point(*touch.pos):
            if hasattr(self, "full_screen_popup"):
                # Sauvegarder une référence au popup avant de le supprimer
                popup_to_close = self.full_screen_popup
                del self.full_screen_popup  # Supprimer l'attribut immédiatement
                
                # Animation de fermeture simple
                close_anim = Animation(opacity=0, duration=0.3)
                close_anim.bind(on_complete=lambda *args: self.remove_widget(popup_to_close))
                close_anim.start(popup_to_close)
            else:
                if self.state == "a l'envers":
                    image_path = f"tarot_img/MajorArcanaCards/{self.drawn_card} {self.state}.jpg"
                else:
                    image_path = (
                        f"tarot_img/MajorArcanaCards/{self.drawn_card}.jpg"
                    )

                # Créer le popup plein écran avec animation d'ouverture
                self.full_screen_popup = FullScreenImagePopup(image_path)
                
                # Commencer invisible
                self.full_screen_popup.opacity = 0
                
                self.add_widget(self.full_screen_popup)
                
                # Animation d'ouverture simple
                open_anim = Animation(opacity=1, duration=0.5)
                open_anim.start(self.full_screen_popup)

    def animate_button_press(self, button):
        """Anime le bouton lors du clic pour un effet visuel"""
        # Animation simple d'opacité
        anim_press = Animation(opacity=0.5, duration=0.1)
        anim_release = Animation(opacity=1, duration=0.1)
        
        # Chaîner les animations
        anim_press.bind(on_complete=lambda *args: anim_release.start(button))
        anim_press.start(button)

    def on_button_hover(self, button, hover):
        """Effet de survol pour le bouton"""
        if hover:
            # Légère modification d'opacité au survol
            Animation(opacity=0.8, duration=0.2).start(button)
        else:
            # Retour à l'opacité normale
            Animation(opacity=1, duration=0.2).start(button)

    def on_button_press(self):
        """Méthode appelée lors du clic sur le bouton nouveau tirage avec animations fun"""
        try:
            button = self.ids.back_button
            if button:
                print("Bouton trouvé, animation fun en cours...")
                
                # Animation simple et efficace d'opacité
                pulse_anim = Animation(opacity=0.3, duration=0.1)
                pulse_anim += Animation(opacity=1.0, duration=0.1)
                pulse_anim += Animation(opacity=0.5, duration=0.1)
                pulse_anim += Animation(opacity=1.0, duration=0.1)
                pulse_anim += Animation(opacity=0.3, duration=0.1)
                pulse_anim += Animation(opacity=1.0, duration=0.1)
                
                # Démarrer l'animation
                pulse_anim.start(button)
                
                # Animation bonus: faire trembler le bouton
                self.create_shake_animation(button)
                
                # Délai pour voir toutes les animations
                Clock.schedule_once(lambda dt: self.change_screen(), 0.8)
            else:
                print("Bouton non trouvé, changement direct")
                self.change_screen()
        except Exception as e:
            print(f"Erreur animation: {e}")
            self.change_screen()
    
    def create_shake_animation(self, widget):
        """Crée une animation de tremblement pour le widget (opacité uniquement)"""
        # Animation de pulsation rapide pour simuler le tremblement
        shake1 = Animation(opacity=0.8, duration=0.05)
        shake2 = Animation(opacity=1.0, duration=0.05)
        shake3 = Animation(opacity=0.7, duration=0.05)
        shake4 = Animation(opacity=1.0, duration=0.05)
        shake5 = Animation(opacity=0.9, duration=0.05)
        shake6 = Animation(opacity=1.0, duration=0.05)
        
        # Chaîner les animations
        shake_sequence = shake1 + shake2 + shake3 + shake4 + shake5 + shake6
        
        # Démarrer après un petit délai
        Clock.schedule_once(lambda dt: shake_sequence.start(widget), 0.2)
    
    def animate_card_appearance(self):
        """Anime l'apparition des éléments de la carte"""
        # Animation de l'image de la carte (fondu seulement)
        if self.card_image:
            # Commencer invisible
            self.card_image.opacity = 0
            
            # Animation d'apparition simple
            fade_in = Animation(opacity=1, duration=0.8)
            fade_in.start(self.card_image)
        
        # Animation du nom de la carte (fondu)
        if self.card_name:
            self.card_name.opacity = 0
            
            fade_in_name = Animation(opacity=1, duration=0.6)
            
            Clock.schedule_once(lambda dt: fade_in_name.start(self.card_name), 0.2)
        
        # Animation de l'état de la carte (pulsation simple)
        if self.card_state:
            self.card_state.opacity = 0
            
            # Animation de pulsation simple
            pulse = Animation(opacity=1, duration=0.5)
            
            Clock.schedule_once(lambda dt: pulse.start(self.card_state), 0.4)
        
        # Animation du texte (typewriter effect simulé)
        if self.card_text:
            original_text = self.card_text.text
            self.card_text.text = ""
            self.card_text.opacity = 1
            
            # Effet typewriter
            Clock.schedule_once(lambda dt: self.typewriter_effect(original_text), 0.8)
        
        # Animation des mots-clés (fondu simple)
        if self.states_label:
            self.states_label.opacity = 0
            
            bounce_in = Animation(opacity=1, duration=0.4)
            
            Clock.schedule_once(lambda dt: bounce_in.start(self.states_label), 0.6)
    
    def typewriter_effect(self, full_text):
        """Simule un effet typewriter pour le texte"""
        if not self.card_text:
            return
            
        def add_char(dt, current_index=[0]):
            if current_index[0] < len(full_text):
                self.card_text.text = full_text[:current_index[0] + 1]
                current_index[0] += 1
                Clock.schedule_once(lambda dt: add_char(dt, current_index), 0.03)
            else:
                # Animation finale de brillance
                self.create_text_glow_effect()
        
        add_char(0)
    
    def create_text_glow_effect(self):
        """Crée un effet de brillance sur le texte"""
        if self.card_text:
            glow = Animation(opacity=0.7, duration=0.3)
            glow += Animation(opacity=1, duration=0.3)
            glow += Animation(opacity=0.8, duration=0.2)
            glow += Animation(opacity=1, duration=0.2)
            glow.start(self.card_text)
    
    def change_screen(self):
        """Change vers l'écran principal et reset"""
        self.manager.current = "hello_screen"
        self.reset()


class MaCarteDeTarotApp(App):
    """Application principale"""

    def __init__(self, **kwargs):
        super(MaCarteDeTarotApp, self).__init__(**kwargs)

    def build(self):
        """Build the app"""
        self.title = "Ma Carte de Tarot"
        self.icon = "tarot_img/tapis.ico"

        return RootScreen()


if __name__ == "__main__":
    MaCarteDeTarotApp().run()
