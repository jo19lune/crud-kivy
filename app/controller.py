from app.models import ItemModel

class ItemController:
    def __init__(self, view):
        self.model = ItemModel()
        self.view = view
        self.refresh_view()

    def refresh_view(self):
        items = self.model.load_items()
        self.view.display_items(items)

    def add_item(self, name, desc, image_path):
        if name.strip():  # Vérifier que le nom n'est pas vide
            self.model.add_item(name, desc, image_path)
            self.refresh_view()
            return True
        return False

    def delete_item(self, item_id):
        self.model.delete_item(item_id)
        self.refresh_view()

    def update_item(self, item_id, name=None, desc=None, image_path=None):
        self.model.update_item(item_id, name, desc, image_path)
        self.refresh_view()
