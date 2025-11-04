from app.models import ItemModel
from utils.camera import ImageManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

class ItemController:
    def __init__(self, view):
        self.model = ItemModel()
        self.view = view
        self.selected_items = set()
        self.view_mode = "grid"  # "grid" ou "list"
        self.current_editing_item = None
        self.refresh_view()

    def refresh_view(self, search_query=None):
        if search_query:
            items = self.model.search_items(search_query)
        else:
            items = self.model.load_items()
        self.view.display_items(items, self.selected_items, self.view_mode)

    def add_item(self, name, desc, image_path):
        if name.strip():
            # Utiliser l'image par défaut si aucun chemin n'est fourni
            if not image_path or image_path == "assets/logo.png":
                image_path = ImageManager.get_default_image()
            
            self.model.add_item(name, desc, image_path)
            self.refresh_view()
            return True
        return False

    def delete_item(self, item_id):
        self.model.delete_item(item_id)
        if item_id in self.selected_items:
            self.selected_items.remove(item_id)
        self.refresh_view()

    def delete_selected_items(self):
        for item_id in list(self.selected_items):
            self.model.delete_item(item_id)
        self.selected_items.clear()
        self.refresh_view()

    def update_item(self, item_id, name=None, desc=None, image_path=None):
        self.model.update_item(item_id, name, desc, image_path)
        self.refresh_view()

    def toggle_item_selection(self, item_id):
        if item_id in self.selected_items:
            self.selected_items.remove(item_id)
        else:
            self.selected_items.add(item_id)
        self.refresh_view()

    def toggle_view_mode(self):
        self.view_mode = "list" if self.view_mode == "grid" else "grid"
        self.refresh_view()

    def select_all_items(self):
        items = self.model.load_items()
        self.selected_items = {item["id"] for item in items}
        self.refresh_view()

    def clear_selection(self):
        self.selected_items.clear()
        self.refresh_view()

    def handle_camera_result(self, image_path):
        """Gère le résultat de la prise de photo"""
        if image_path:
            self.view.selected_image_path = image_path
            self.view.ids.image_btn.text = "Photo prise ✓"
        else:
            self.view.show_error_dialog("Erreur", "Impossible de prendre la photo")

    def handle_gallery_result(self, image_path):
        """Gère le résultat de la sélection galerie"""
        if image_path:
            self.view.selected_image_path = image_path
            self.view.ids.image_btn.text = "Image choisie ✓"
        else:
            self.view.show_error_dialog("Erreur", "Impossible de charger l'image")

    def edit_item(self, item_id):
        """Ouvre la boîte de dialogue pour modifier un item"""
        items = self.model.load_items()
        item = next((item for item in items if item["id"] == item_id), None)
        
        if item:
            self.current_editing_item = item_id
            self.view.open_edit_dialog(item)

    def update_item_with_dialog(self, name, desc, image_path):
        """Met à jour l'item en cours d'édition"""
        if self.current_editing_item:
            self.update_item(self.current_editing_item, name, desc, image_path)
            self.current_editing_item = None

    def get_card_color(self, item_id):
        """Retourne la couleur en fonction de la sélection"""
        if item_id in self.selected_items:
            return [0.8, 0.9, 1, 1]  # Bleu clair pour la sélection
        return [1, 1, 1, 1]  # Blanc normal
