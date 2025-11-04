import json
import os
from uuid import uuid4

DB_PATH = "data/database.json"

class ItemModel:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        if not os.path.exists(DB_PATH):
            self.save_items([])

    def load_items(self):
        try:
            with open(DB_PATH, "r", encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_items(self, items):
        with open(DB_PATH, "w", encoding='utf-8') as f:
            json.dump(items, f, indent=4, ensure_ascii=False)

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
