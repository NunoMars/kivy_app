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
        """Déclenche le tirage d'une carte depuis l'écran d'accueil"""
        # Récupérer l'écran de réponse
        response_screen = self.manager.get_screen("response_screen")
        
        # Déclencher le chargement des données avec popup
        response_screen.show_loading_popup()
        
        # Changer d'écran après un court délai pour permettre au popup de s'afficher
        Clock.schedule_once(lambda dt: self.switch_to_response(), 0.1)
    
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
        animated_card = Image(source=gif_path, anim_delay=0.1, size_hint=(1, 0.8))
        content_layout.add_widget(animated_card)
        
        # Message d'attente en bas
        waiting_label = Label(
            text="Concentration en cours...",
            size_hint=(1, 0.1),
            font_size="14sp",
            color=[0.6, 0.4, 0.2, 1.0],
            halign='center'
        )
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
        """Affiche l'image en plein écran si l'utilisateur clique dessus"""
        if self.card_image is not None and self.card_image.collide_point(*touch.pos):
            if hasattr(self, "full_screen_popup"):
                self.remove_widget(self.full_screen_popup)
                del self.full_screen_popup
            else:
                if self.state == "a l'envers":
                    image_path = f"tarot_img/MajorArcanaCards/{self.drawn_card} {self.state}.jpg"
                else:
                    image_path = (
                        f"tarot_img/MajorArcanaCards/{self.drawn_card}.jpg"
                    )

                # Create a full-screen popup with the image
                self.full_screen_popup = FullScreenImagePopup(image_path)
                self.add_widget(self.full_screen_popup)

    def animate_button_press(self, button):
        """Anime le bouton lors du clic pour un effet visuel"""
        # Animation de pressage (réduction de taille)
        anim_press = Animation(size_hint=(0.55, 0.13), duration=0.1)  # Légèrement plus petit
        # Animation de retour à la taille normale
        anim_release = Animation(size_hint=(0.6, 0.15), duration=0.1)  # Taille normale du bouton
        
        # Chaîner les animations
        anim_press.bind(on_complete=lambda *args: anim_release.start(button))
        anim_press.start(button)

    def on_button_hover(self, button, hover):
        """Effet de survol pour le bouton"""
        if hover:
            # Légère augmentation de taille au survol
            Animation(size_hint=(0.85, 1.05), duration=0.2).start(button)
        else:
            # Retour à la taille normale
            Animation(size_hint=(0.8, 1), duration=0.2).start(button)

    def on_button_press(self):
        """Méthode appelée lors du clic sur le bouton nouveau tirage"""
        try:
            button = self.ids.back_button
            if button:
                print("Bouton trouvé, animation en cours...")
                # Animation simple de pressage - seulement sur la largeur
                original_size_hint_x = button.size_hint_x
                anim = Animation(size_hint_x=0.6, duration=0.1)
                anim += Animation(size_hint_x=original_size_hint_x, duration=0.1)
                anim.start(button)
                # Délai pour voir l'animation
                Clock.schedule_once(lambda dt: self.change_screen(), 0.25)
            else:
                print("Bouton non trouvé, changement direct")
                self.change_screen()
        except Exception as e:
            print(f"Erreur animation: {e}")
            self.change_screen()
    
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
