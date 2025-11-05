import json
import os
from uuid import uuid4

try:
    from config import get_database_path
    DB_PATH = get_database_path()
except ImportError:
    # Fallback
    import sys
    def get_database_path():
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_dir, "data", "database.json")
    DB_PATH = get_database_path()

class ItemModel:
    def __init__(self):
        # S'assurer que le dossier data existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        # S'assurer que le fichier existe
        if not os.path.exists(DB_PATH):
            self.save_items([])

    def load_items(self):
        try:
            if not os.path.exists(DB_PATH):
                return []
                
            with open(DB_PATH, "r", encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_items(self, items):
        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            
            with open(DB_PATH, "w", encoding='utf-8') as f:
                json.dump(items, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            try:
                with open(DB_PATH, "w", encoding='utf-8') as f:
                    json.dump([], f, indent=4, ensure_ascii=False)
            except Exception as e2:
                print(f"Erreur critique lors de la recréation de la base: {e2}")

    def add_item(self, name, desc, image_path):
        items = self.load_items()
        new_item = {
            "id": str(uuid4()),
            "name": name,
            "desc": desc,
            "image": image_path
        }
        items.append(new_item)
        self.save_items(items)
        return new_item

    def delete_item(self, item_id):
        items = self.load_items()
        items = [item for item in items if item["id"] != item_id]
        self.save_items(items)

    def update_item(self, item_id, name=None, desc=None, image_path=None):
        items = self.load_items()
        for item in items:
            if item["id"] == item_id:
                if name is not None:
                    item["name"] = name
                if desc is not None:
                    item["desc"] = desc
                if image_path is not None:
                    item["image"] = image_path
                break
        self.save_items(items)

    def search_items(self, query):
        items = self.load_items()
        if not query:
            return items
        query = query.lower()
        return [item for item in items 
                if query in item["name"].lower() or query in item["desc"].lower()]
    
    def get_all_image_paths(self):
        """
        Retourne tous les chemins d'images utilisés dans la base de données
        """
        items = self.load_items()
        image_paths = []
        
        for item in items:
            if item.get("image"):
                image_paths.append(item["image"])
        
        # print(f"{len(image_paths)} chemins d'images trouvés dans la base")
        return image_paths
