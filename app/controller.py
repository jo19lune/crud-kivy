from app.models import ItemModel
from utils.camera import ImageManager

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
        
        # Mettre à jour le compteur d'items
        if hasattr(self.view, 'ids') and hasattr(self.view.ids, 'items_count'):
            count = len(items)
            self.view.ids.items_count.text = f"({count} item{'s' if count != 1 else ''})"

    def add_item(self, name, desc, image_path):
        if name.strip():
            # Traiter le chemin de l'image
            final_image_path = self._process_image_path(image_path)
            print(f"📍 Ajout item avec image: {final_image_path}")
            
            self.model.add_item(name, desc, final_image_path)
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
        # Si une nouvelle image est fournie, la copier
        if image_path and image_path != ImageManager.get_default_image() and not image_path.startswith("assets/images/"):
            image_path = ImageManager.copy_image_to_assets(image_path)
        
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
        """Gère le résultat de la prise de photo pour nouvel item"""
        if image_path:
            self.view.selected_image_path = image_path
            if hasattr(self.view, 'ids') and hasattr(self.view.ids, 'image_btn'):
                self.view.ids.image_btn.text = "✓ Image sélectionnée"
        else:
            self.view.show_error_dialog("Erreur", "Impossible de prendre la photo")

    def handle_gallery_result(self, image_path):
        """Gère le résultat de la sélection galerie pour nouvel item"""
        if image_path:
            self.view.selected_image_path = image_path
            if hasattr(self.view, 'ids') and hasattr(self.view.ids, 'image_btn'):
                self.view.ids.image_btn.text = "✓ Image sélectionnée"
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
            # Copier l'image seulement si c'est une nouvelle image
            if image_path and image_path != ImageManager.get_default_image() and not image_path.startswith("assets/images/"):
                image_path = ImageManager.copy_image_to_assets(image_path)
            elif not image_path or image_path == ImageManager.get_default_image():
                # Garder l'ancienne image
                items = self.model.load_items()
                old_item = next((item for item in items if item["id"] == self.current_editing_item), None)
                if old_item:
                    image_path = old_item["image"]
            
            self.update_item(self.current_editing_item, name, desc, image_path)
            self.current_editing_item = None

    def get_card_color(self, item_id):
        """Retourne la couleur en fonction de la sélection"""
        if item_id in self.selected_items:
            return [0.8, 0.9, 1, 1]  # Bleu clair pour la sélection
        return [1, 1, 1, 1]  # Blanc normal

    def _process_image_path(self, image_path):
        """Traite le chemin de l'image : copie si nécessaire"""
        if not image_path or image_path == ImageManager.get_default_image():
            return ImageManager.get_default_image()
        
        # Si l'image est déjà dans assets/images, la garder
        if image_path.startswith("assets/images/"):
            return image_path
        
        # Sinon, copier l'image dans assets/images
        return ImageManager.copy_image_to_assets(image_path)
