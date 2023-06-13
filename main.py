__version__ = "0.01"

import os
import random

from kivy.app import App, Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import *

from kivy.uix.boxlayout import BoxLayout
from PIL import Image as PILImage
from signification import cards_signification

Builder.load_file("macartedetarotapp.kv")


class RootScreen(ScreenManager):
    pass


class CardScreen(Screen):
    """Ecran principal de l'application"""

    def __init__(self, **kwargs):
        super(CardScreen, self).__init__(**kwargs)


class CardResponseScreen(Screen):
    """Ecran de réponse de l'application"""

    def __init__(self, **kwargs):
        super(CardResponseScreen, self).__init__(**kwargs)
        self.path = "tarot_img/MajorArcanaCards"
        self.cards = list(cards_signification.keys())
        self.states = ["a l'endroit", "a l'envers"]

    def on_enter(self, *args):
        self.build()

    def create_card_text(self, text):
        """
        insére "\n" tous les 30 caractères
         d'un texte complet afin de reduire la taille en largeur
        """
        list_of_text = [text[i : i + 70] for i in range(0, len(text), 70)]
        return "\n".join(list_of_text)

    def build(self):
        """Tire une carte de tarot aléatoire et affiche l'image correspondante"""
        self.drawn_card = random.choice(self.cards)
        self.state = random.choice(self.states)
        self.card_title.text = f"{self.drawn_card} {self.state}"
        states_label_text = str(cards_signification[self.drawn_card][self.state])
        self.states_label.text = self.create_card_text(states_label_text)

        if self.state == "a l'envers":
            if f"{self.drawn_card} {self.state}.jpg" not in os.listdir(
                "tarot_img/MajorArcanaCards"
            ):
                img = PILImage.open(f"tarot_img/MajorArcanaCards/{self.drawn_card}.jpg")
                img.rotate(180, expand=True).save(
                    f"tarot_img/MajorArcanaCards/{self.drawn_card} {self.state}.jpg"
                )

            image_path = (
                f"tarot_img/MajorArcanaCards/{self.drawn_card} {self.state}.jpg"
            )
            self.card_image.source = image_path
        else:
            image_path = f"tarot_img/MajorArcanaCards/{self.drawn_card}.jpg"  # Chemin de l'image correspondante

            self.card_image.source = image_path

        self.card_text.text = str(
            cards_signification[self.drawn_card][f"signification {self.state}"]
        )


class MaCarteDeTarotApp(App):
    """Application principale"""

    def __init__(self, **kwargs):
        super(MaCarteDeTarotApp, self).__init__(**kwargs)

    def build(self):
        """Build the app"""
        self.title = "Ma Carte de Tarot"
        self.icon = "tarot_img/icon.png"

        return RootScreen()


if __name__ == "__main__":
    MaCarteDeTarotApp().run()
