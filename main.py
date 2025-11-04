from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from app.controller import ItemController
import os

# Charger le fichier KV
Builder.load_file("app/view.kv")

class MainScreen(Screen):
    def display_items(self, items):
        container = self.ids.list_container
        container.clear_widgets()
        
        for item in items:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivy.uix.image import AsyncImage
            
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height='200dp',
                padding='10dp',
                spacing='10dp',
                elevation=2
            )
            
            # Image avec gestion d'erreur
            img = AsyncImage(
                source=item.get("image", "assets/logo.png"),
                size_hint_y=0.6,
                allow_stretch=True
            )
            
            card.add_widget(img)
            card.add_widget(MDLabel(
                text=item["name"], 
                halign="center",
                bold=True
            ))
            card.add_widget(MDLabel(
                text=item["desc"], 
                halign="center", 
                theme_text_color="Secondary"
            ))
            
            container.add_widget(card)

class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # Créer le ScreenManager
        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        sm.add_widget(main_screen)
        
        # Initialiser le controller après la création de la vue
        self.controller = ItemController(main_screen)
        
        return sm

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    MyApp().run()
