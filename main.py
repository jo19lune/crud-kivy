from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from app.controller import ItemController
from utils.camera import ImageManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
import os

# Charger le fichier KV
Builder.load_file("app/view.kv")

class ImageDialog(MDBoxLayout):
    """Boîte de dialogue pour choisir une image"""
    pass

class EditDialog(MDBoxLayout):
    """Boîte de dialogue pour modifier un item"""
    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        self.ids.name_input.text = item["name"]
        self.ids.desc_input.text = item["desc"]
        self.selected_image_path = item["image"]

class MainScreen(Screen):
    selected_image_path = StringProperty("assets/logo.png")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_dialog = None
        self.edit_dialog = None
        self.error_dialog = None

    def show_image_dialog(self):
        """Affiche la boîte de dialogue pour choisir une image"""
        if not self.image_dialog:
            self.image_dialog = MDDialog(
                title="Choisir une image",
                type="custom",
                content_cls=ImageDialog(),
                size_hint=(0.8, None),
                height=200
            )
        self.image_dialog.open()

    def open_edit_dialog(self, item):
        """Ouvre la boîte de dialogue pour modifier un item"""
        self.edit_dialog = MDDialog(
            title="Modifier l'item",
            type="custom",
            content_cls=EditDialog(item),
            buttons=[
                MDFlatButton(
                    text="Annuler",
                    on_release=lambda x: self.edit_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Sauvegarder",
                    on_release=lambda x: self.save_edit_item()
                )
            ],
            size_hint=(0.8, None),
            height=400
        )
        self.edit_dialog.open()

    def save_edit_item(self):
        """Sauvegarde les modifications de l'item"""
        if self.edit_dialog:
            content = self.edit_dialog.content_cls
            name = content.ids.name_input.text
            desc = content.ids.desc_input.text
            image_path = content.selected_image_path
            
            self.app.controller.update_item_with_dialog(name, desc, image_path)
            self.edit_dialog.dismiss()

    def show_error_dialog(self, title, message):
        """Affiche une boîte de dialogue d'erreur"""
        self.error_dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.error_dialog.dismiss()
                )
            ]
        )
        self.error_dialog.open()

    def display_items(self, items, selected_items, view_mode):
        grid_container = self.ids.grid_container
        list_container = self.ids.list_container
        
        # Effacer les conteneurs
        grid_container.clear_widgets()
        list_container.clear_widgets()
        
        # Mettre à jour le bouton de suppression
        self.ids.delete_selected_btn.disabled = len(selected_items) == 0
        
        # Mettre à jour le switch de mode vue
        self.ids.view_mode_switch.active = view_mode == "list"
        
        if view_mode == "grid":
            # Afficher la grille, cacher la liste
            list_container.opacity = 0
            list_container.size_hint_y = 0
            grid_container.opacity = 1
            grid_container.size_hint_y = None
            grid_container.height = grid_container.minimum_height
            self.display_grid_view(items, selected_items, grid_container)
        else:
            # Afficher la liste, cacher la grille
            grid_container.opacity = 0
            grid_container.size_hint_y = 0
            list_container.opacity = 1
            list_container.size_hint_y = None
            list_container.height = list_container.minimum_height
            self.display_list_view(items, selected_items, list_container)
    
    def display_grid_view(self, items, selected_items, container):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivy.uix.image import AsyncImage
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDIconButton
        
        for item in items:
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height='240dp',
                padding='10dp',
                spacing='10dp',
                elevation=2
            )
            
            # Ajouter l'ID de l'item à la carte
            card.item_id = item["id"]
            
            # Couleur de fond si sélectionné
            if item["id"] in selected_items:
                card.md_bg_color = [0.8, 0.9, 1, 1]  # Bleu clair
            
            # Conteneur pour la checkbox et le bouton d'édition
            header_layout = MDBoxLayout(adaptive_height=True, spacing=5)
            
            # Checkbox
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(24, 24),
                active=item["id"] in selected_items,
                on_active=lambda instance, value, item_id=item["id"]: 
                    self.app.controller.toggle_item_selection(item_id)
            )
            header_layout.add_widget(checkbox)
            
            # Bouton d'édition
            edit_btn = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=(24, 24),
                theme_text_color="Secondary",
                on_release=lambda instance, item_id=item["id"]: 
                    self.app.controller.edit_item(item_id)
            )
            header_layout.add_widget(edit_btn)
            
            card.add_widget(header_layout)
            
            # Image
            img = AsyncImage(
                source=item.get("image", "assets/logo.png"),
                size_hint_y=0.6,
                allow_stretch=True
            )
            card.add_widget(img)
            
            # Nom
            name_label = MDLabel(
                text=item["name"], 
                halign="center",
                bold=True,
                size_hint_y=0.2
            )
            card.add_widget(name_label)
            
            # Description
            desc_label = MDLabel(
                text=item["desc"], 
                halign="center", 
                theme_text_color="Secondary",
                size_hint_y=0.2
            )
            card.add_widget(desc_label)
            
            container.add_widget(card)
    
    def display_list_view(self, items, selected_items, container):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.label import MDLabel
        
        for item in items:
            # Créer un layout horizontal pour la liste
            list_item = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                spacing=10,
                padding=10
            )
            
            # Ajouter l'ID de l'item
            list_item.item_id = item["id"]
            list_item.text = item["name"]
            list_item.secondary_text = item["desc"]
            
            # Checkbox
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(24, 24),
                pos_hint={'center_y': 0.5},
                active=item["id"] in selected_items,
                on_active=lambda instance, value, item_id=item["id"]: 
                    self.app.controller.toggle_item_selection(item_id)
            )
            list_item.add_widget(checkbox)
            
            # Contenu textuel
            text_layout = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                spacing=5
            )
            
            # Nom
            name_label = MDLabel(
                text=item["name"],
                theme_text_color="Primary",
                font_style="Subtitle1",
                adaptive_height=True
            )
            text_layout.add_widget(name_label)
            
            # Description
            desc_label = MDLabel(
                text=item["desc"],
                theme_text_color="Secondary",
                font_style="Body2",
                adaptive_height=True
            )
            text_layout.add_widget(desc_label)
            
            list_item.add_widget(text_layout)
            
            # Couleur de fond si sélectionné
            if item["id"] in selected_items:
                list_item.md_bg_color = [0.8, 0.9, 1, 1]
            
            container.add_widget(list_item)

class MyApp(MDApp):
    selected_color = ListProperty([0.8, 0.9, 1, 1])
    normal_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # Créer le ScreenManager
        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        main_screen.app = self  # Référence à l'app
        sm.add_widget(main_screen)
        
        # Initialiser le controller après la création de la vue
        self.controller = ItemController(main_screen)
        
        return sm
    
    def show_image_dialog(self):
        """Affiche la boîte de dialogue pour choisir une image"""
        self.root.show_image_dialog()

    def open_camera(self):
        """Ouvre la caméra pour prendre une photo"""
        if self.root.image_dialog:
            self.root.image_dialog.dismiss()
        
        ImageManager.take_photo(self.controller.handle_camera_result)

    def open_gallery(self):
        """Ouvre la galerie pour choisir une image"""
        if self.root.image_dialog:
            self.root.image_dialog.dismiss()
        
        ImageManager.select_from_gallery(self.controller.handle_gallery_result)
    
    def get_card_color(self, item_id):
        """Retourne la couleur en fonction de la sélection"""
        if item_id in self.controller.selected_items:
            return self.selected_color
        return self.normal_color

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    MyApp().run()
