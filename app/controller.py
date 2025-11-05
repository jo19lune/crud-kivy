from app.models import ItemModel
from utils.camera import ImageManager
from kivy.clock import Clock

class ItemController:
    def __init__(self, view):
        self.model = ItemModel()
        self.view = view
        self.selected_items = set()
        self.view_mode = "grid"
        self.current_editing_item = None
        self.sort_mode = "none"  # "none", "name_asc", "name_desc"
        
        # Rafraîchir la vue après un court délai pour éviter les problèmes de timing
        Clock.schedule_once(lambda dt: self.refresh_view(), 0.1)

    def refresh_view(self, search_query=None):
        """Rafraîchit la vue avec gestion des images manquantes et tri"""
        if search_query:
            items = self.model.search_items(search_query)
        else:
            items = self.model.load_items()
        
        # Appliquer le tri
        items = self._apply_sort(items)
        
        # Nettoyer les items avec images manquantes
        cleaned_items = self._clean_items_with_missing_images(items)
        if len(cleaned_items) != len(items):
            print(f"{len(items) - len(cleaned_items)} items nettoyés (images manquantes)")
        
        self.view.display_items(cleaned_items, self.selected_items, self.view_mode)
        
        # Mettre à jour le compteur d'items et info tri
        self._update_display_info(cleaned_items)

    def _apply_sort(self, items):
        """Applique le tri selon le mode actuel"""
        if self.sort_mode == "name_asc":
            return sorted(items, key=lambda x: x["name"].lower())
        elif self.sort_mode == "name_desc":
            return sorted(items, key=lambda x: x["name"].lower(), reverse=True)
        else:
            return items

    def _update_display_info(self, items):
        """Met à jour les informations d'affichage"""
        if hasattr(self.view, 'ids'):
            count = len(items)
            self.view.ids.items_count.text = f"({count} item{'s' if count != 1 else ''})"
            
            # Mettre à jour l'info de tri
            sort_text = ""
            if self.sort_mode == "name_asc":
                sort_text = "A-Z"
            elif self.sort_mode == "name_desc":
                sort_text = "Z-A"
            self.view.ids.sort_info.text = sort_text
            
            # Mettre à jour le titre
            title = "Mes Items"
            if self.sort_mode != "none":
                title += f" • Tri: {sort_text}"
            self.view.ids.items_title.text = title

    def set_sort_mode(self, sort_mode):
        """Définit le mode de tri"""
        self.sort_mode = sort_mode
        self.refresh_view()

    def set_view_mode(self, view_mode):
        """Définit le mode de vue"""
        self.view_mode = view_mode
        self.refresh_view()

    def _clean_items_with_missing_images(self, items):
        """Nettoie les items avec images manquantes et les corrige automatiquement"""
        cleaned_items = []
        needs_save = False
        
        for item in items:
            original_image = item["image"]
            safe_image = ImageManager.get_safe_image_path(original_image)
            
            # Si l'image a changé (image manquante détectée), mettre à jour l'item
            if safe_image != original_image:
                item["image"] = safe_image
                needs_save = True
                print(f"Image corrigée pour '{item['name']}': {original_image} -> {safe_image}")
            
            cleaned_items.append(item)
        
        # Sauvegarder si des corrections ont été faites
        if needs_save:
            self.model.save_items(cleaned_items)
            print("Items sauvegardés après correction des images")
        
        return cleaned_items

    def add_item(self, name, desc, image_path):
        if name.strip():
            # Traiter le chemin de l'image
            final_image_path = self._process_image_path(image_path)
            print(f"Ajout item avec image: {final_image_path}")
            
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
            # Récupérer l'item original pour comparer les images
            items = self.model.load_items()
            old_item = next((item for item in items if item["id"] == self.current_editing_item), None)
            
            if old_item:
                # Vérifier si l'image a changé
                image_changed = False
                final_image_path = image_path
                
                if image_path and image_path != ImageManager.get_default_image():
                    # Si une nouvelle image est sélectionnée (différente de l'ancienne)
                    if image_path != old_item["image"] and not image_path.startswith("assets/images/"):
                        print(f"Nouvelle image détectée, copie en cours...")
                        final_image_path = ImageManager.copy_image_to_assets(image_path)
                        image_changed = True
                    else:
                        # Même image ou image déjà dans assets/images
                        final_image_path = old_item["image"]
                else:
                    # Aucune image sélectionnée ou image par défaut
                    final_image_path = old_item["image"]
                
                print(f"Image finale pour la mise à jour: {final_image_path}")
                
                # Mettre à jour l'item
                self.model.update_item(self.current_editing_item, name, desc, final_image_path)
                self.current_editing_item = None
            else:
                print("Item à modifier non trouvé")

    def get_card_color(self, item_id):
        """Retourne la couleur en fonction de la sélection"""
        if item_id in self.selected_items:
            return [0.8, 0.9, 1, 1]
        return [1, 1, 1, 1]

    def _process_image_path(self, image_path):
        """Traite le chemin de l'image : copie si nécessaire"""
        if not image_path or image_path == ImageManager.get_default_image():
            return ImageManager.get_default_image()
        
        # Si l'image est déjà dans assets/images, la garder
        if image_path.startswith("assets/images/"):
            return image_path
        
        # Sinon, copier l'image dans assets/images
        return ImageManager.copy_image_to_assets(image_path)

    def cleanup_missing_images(self):
        """Nettoie tous les items avec images manquantes (méthode utilitaire)"""
        items = self.model.load_items()
        cleaned_items = self._clean_items_with_missing_images(items)
        print(f"Nettoyage terminé: {len(items)} -> {len(cleaned_items)} items valides")
        self.refresh_view()
        
        # Afficher un message de confirmation
        if hasattr(self.view, 'show_info_dialog'):
            self.view.show_info_dialog("Nettoyage terminé", 
                                     f"Base de données nettoyée : {len(cleaned_items)} items valides")

    def fix_image_paths(self):
        """
        Corrige tous les chemins d'images dans la base de données
        pour qu'ils soient sous la forme assets/images/nom_fichier.extension
        """
        try:
            items = self.model.load_items()
            print(f"🔧 Correction des chemins pour {len(items)} items")
            
            # Corriger les chemins d'images
            fixed_items, changes_made = ImageManager.fix_image_paths_in_items(items)
            
            if changes_made:
                # Sauvegarder les corrections
                self.model.save_items(fixed_items)
                print("✅ Tous les chemins d'images ont été corrigés")
                
                # Afficher un message de confirmation
                if hasattr(self.view, 'show_info_dialog'):
                    self.view.show_info_dialog("Chemins corrigés", 
                                             "Tous les chemins d'images ont été normalisés")
                
                # Rafraîchir l'affichage
                self.refresh_view()
                return True
            else:
                print("ℹ️ Aucun chemin d'image à corriger")
                if hasattr(self.view, 'show_info_dialog'):
                    self.view.show_info_dialog("Aucun changement", 
                                             "Tous les chemins d'images sont déjà corrects")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de la correction des chemins: {e}")
            if hasattr(self.view, 'show_error_dialog'):
                self.view.show_error_dialog("Erreur", "Impossible de corriger les chemins d'images")
            return False
