from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from app.controller import ItemController
from utils.camera import ImageManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
import os
from kivy.clock import Clock
import sys

try:
    from config import get_project_root, get_images_path, get_data_path, get_assets_path
except ImportError:
    # Fallback
    import sys
    def get_project_root():
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def get_assets_path():
        return os.path.join(get_project_root(), "assets")
    
    def get_images_path():
        return os.path.join(get_project_root(), "assets", "images")
    
    def get_data_path():
        return os.path.join(get_project_root(), "data")

# Charger le fichier KV
Builder.load_file("app/view.kv")

class ImageDialog(MDBoxLayout):
    """Boîte de dialogue pour choisir une image"""
    pass

class EditDialogContent(MDBoxLayout):
    """Contenu de la boîte de dialogue pour modifier un item"""
    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        self.item = item
        self.selected_image_path = item["image"]
        
        # Utiliser Clock pour initialiser après la création des widgets
        Clock.schedule_once(self._init_fields)

    def _init_fields(self, dt):
        """Initialise les champs après création des widgets"""
        if hasattr(self, 'ids'):
            self.ids.name_input.text = self.item["name"]
            self.ids.desc_input.text = self.item["desc"]

class MainScreen(Screen):
    selected_image_path = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_dialog = None
        self.edit_dialog = None
        self.error_dialog = None
        self.current_edit_content = None
        self.app = None
        self.selected_image_path = ImageManager.get_default_image()

    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        if hasattr(self, 'app') and self.app and self.app.controller:
            self.app.controller.refresh_view()

    def show_image_dialog(self, for_edit=False):
        """Affiche la boîte de dialogue pour choisir une image"""
        if not self.image_dialog:
            self.image_dialog = MDDialog(
                title="Choisir une image",
                type="custom",
                content_cls=ImageDialog(),
                buttons=[
                    MDFlatButton(
                        text="Fermer",
                        on_release=lambda x: self.image_dialog.dismiss()
                    )
                ],
                size_hint=(0.8, None),
                height=200
            )
        self.image_dialog.for_edit = for_edit
        self.image_dialog.open()

    def open_edit_dialog(self, item):
        """Ouvre la boîte de dialogue pour modifier un item"""
        # Fermer d'abord les autres dialogues
        if self.image_dialog:
            self.image_dialog.dismiss()
        
        content = EditDialogContent(item)
        self.current_edit_content = content
        
        self.edit_dialog = MDDialog(
            title="Modifier l'item",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Annuler",
                    on_release=lambda x: self.edit_dialog.dismiss()
                ),
                MDFlatButton(
                    text="Sauvegarder",
                    on_release=lambda x: self.save_edit_item(content)
                )
            ],
            size_hint=(0.8, None),
            height=300
        )
        self.edit_dialog.open()

    def save_edit_item(self, content):
        """Sauvegarde les modifications de l'item"""
        if content and hasattr(content, 'ids'):
            name = content.ids.name_input.text
            desc = content.ids.desc_input.text
            image_path = content.selected_image_path
            
            self.app.controller.update_item_with_dialog(name, desc, image_path)
            self.edit_dialog.dismiss()
            self.current_edit_content = None

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

    def handle_camera_result_for_edit(self, image_path):
        """Gère le résultat de la caméra pour l'édition"""
        if image_path and self.current_edit_content:
            self.current_edit_content.selected_image_path = image_path
            if hasattr(self.current_edit_content, 'ids'):
                self.current_edit_content.ids.image_btn_edit.text = "✓ Image sélectionnée"

    def handle_gallery_result_for_edit(self, image_path):
        """Gère le résultat de la galerie pour l'édition"""
        if image_path and self.current_edit_content:
            self.current_edit_content.selected_image_path = image_path
            if hasattr(self.current_edit_content, 'ids'):
                self.current_edit_content.ids.image_btn_edit.text = "✓ Image sélectionnée"

    def show_edit_image_dialog(self):
        """Affiche le dialogue de sélection d'image pour l'édition"""
        self.show_image_dialog(for_edit=True)

    def display_items(self, items, selected_items, view_mode):
        """Affiche les items selon le mode de vue"""
        if not hasattr(self, 'ids'):
            return
            
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
            self.display_grid_view(items, selected_items, grid_container)
        else:
            self.display_list_view(items, selected_items, list_container)
    
    def display_grid_view(self, items, selected_items, container):
        for item in items:
            # Créer la carte
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=240,
                padding=10,
                spacing=10,
                elevation=2
            )
            
            # Header avec checkbox et bouton d'édition
            header = MDBoxLayout(adaptive_height=True, spacing=5)
            
            # Checkbox
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(24, 24),
                active=item["id"] in selected_items
            )
            checkbox.bind(active=lambda instance, value, item_id=item["id"]: 
                self.app.controller.toggle_item_selection(item_id))
            header.add_widget(checkbox)
            
            # Bouton d'édition
            edit_btn = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=(24, 24),
                theme_text_color="Secondary"
            )
            edit_btn.bind(on_release=lambda instance, item_id=item["id"]: 
                self.app.controller.edit_item(item_id))
            header.add_widget(edit_btn)
            
            card.add_widget(header)
            
            # Image
            img = AsyncImage(
                source=item.get("image", "assets/logo.png"),
                size_hint_y=0.6,
                allow_stretch=True,
                keep_ratio=True
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
            
            # Style si sélectionné
            if item["id"] in selected_items:
                card.md_bg_color = [0.8, 0.9, 1, 1]
            
            container.add_widget(card)
        
    def display_list_view(self, items, selected_items, container):        
        for item in items:
            # Créer un layout horizontal pour la liste
            list_item = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                spacing=10,
                padding=10,
                size_hint_y=None,
                height=80
            )
            
            # Checkbox
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(24, 24),
                pos_hint={'center_y': 0.5},
                active=item["id"] in selected_items
            )
            checkbox.bind(active=lambda instance, value, item_id=item["id"]: 
                self.app.controller.toggle_item_selection(item_id))
            list_item.add_widget(checkbox)
            
            # Contenu textuel
            text_layout = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                spacing=5,
                size_hint_x=0.7
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
            
            # Bouton d'édition
            edit_btn = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=(40, 40),
                theme_text_color="Secondary",
                pos_hint={'center_y': 0.5}
            )
            edit_btn.bind(on_release=lambda instance, item_id=item["id"]: 
                self.app.controller.edit_item(item_id))
            list_item.add_widget(edit_btn)
            
            # Couleur de fond si sélectionné
            if item["id"] in selected_items:
                list_item.md_bg_color = [0.8, 0.9, 1, 1]
            
            container.add_widget(list_item)

class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = None
        self.main_screen = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        # Vérifier que les assets sont accessibles
        self._check_assets()
        
        # Créer le ScreenManager
        sm = ScreenManager()
        self.main_screen = MainScreen(name='main')
        self.main_screen.app = self
        sm.add_widget(self.main_screen)
        
        # Initialiser le controller
        self.controller = ItemController(self.main_screen)
        
        return sm

    def _check_assets(self):
        """Vérifie que les assets sont accessibles"""
        logo_path = ImageManager.get_default_image()
        print(f"🔍 Vérification assets: {logo_path}")
        print(f"🔍 Logo accessible: {os.path.exists(logo_path)}")
        
        if not os.path.exists(logo_path):
            print("⚠️ Logo non trouvé, création d'un logo par défaut")
            ImageManager.ensure_assets_folder()
    
    def on_start(self):
        """Appelé quand l'application démarre"""
        # Rafraîchir la vue après que l'interface soit complètement chargée
        Clock.schedule_once(lambda dt: self.controller.refresh_view(), 0.5)
    
    def show_image_dialog(self):
        """Affiche la boîte de dialogue pour choisir une image (pour nouvel item)"""
        if self.main_screen:
            self.main_screen.show_image_dialog(for_edit=False)

    def show_edit_image_dialog(self):
        """Affiche la boîte de dialogue pour choisir une image (pour édition)"""
        if self.main_screen:
            self.main_screen.show_edit_image_dialog()

    def open_camera(self):
        """Ouvre la caméra pour prendre une photo"""
        try:
            if (hasattr(self.main_screen, 'image_dialog') and self.main_screen.image_dialog and 
                getattr(self.main_screen.image_dialog, 'for_edit', False)):
                # Pour l'édition
                ImageManager.take_photo(self.main_screen.handle_camera_result_for_edit)
            else:
                # Pour un nouvel item
                ImageManager.take_photo(self.controller.handle_camera_result)
        except Exception as e:
            print(f"Erreur caméra: {e}")

    def open_gallery(self):
        """Ouvre la galerie pour choisir une image"""
        try:
            if (hasattr(self.main_screen, 'image_dialog') and self.main_screen.image_dialog and 
                getattr(self.main_screen.image_dialog, 'for_edit', False)):
                # Pour l'édition
                ImageManager.select_from_gallery(self.main_screen.handle_gallery_result_for_edit)
            else:
                # Pour un nouvel item
                ImageManager.select_from_gallery(self.controller.handle_gallery_result)
        except Exception as e:
            print(f"Erreur galerie: {e}")
    
    def get_card_color(self, item_id):
        """Retourne la couleur en fonction de la sélection"""
        if hasattr(self, 'controller') and self.controller:
            if item_id in self.controller.selected_items:
                return [0.8, 0.9, 1, 1]
        return [1, 1, 1, 1]

def ensure_directories():
    """Crée les dossiers nécessaires dans le projet"""
    assets_path = get_assets_path()
    images_path = get_images_path()
    data_path = get_data_path()
    
    print("=== CRÉATION DES DOSSIERS ===")
    print(f"Création du dossier: {assets_path}")
    os.makedirs(assets_path, exist_ok=True)
    print(f"Création du dossier: {images_path}")
    os.makedirs(images_path, exist_ok=True)
    print(f"Création du dossier: {data_path}")
    os.makedirs(data_path, exist_ok=True)
    
    # Vérifier que les dossiers sont créés
    print(f"Dossier assets existe: {os.path.exists(assets_path)}")
    print(f"Dossier images existe: {os.path.exists(images_path)}")
    print(f"Dossier data existe: {os.path.exists(data_path)}")
    print("=============================")

if __name__ == '__main__':
    ensure_directories()
    MyApp().run()
