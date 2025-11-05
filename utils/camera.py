from plyer import camera, filechooser
from kivy.core.image import Image as CoreImage
from io import BytesIO
import os
from datetime import datetime
from kivy import platform

class ImageManager:
    @staticmethod
    def ensure_assets_folder():
        """Crée le dossier assets/images s'il n'existe pas"""
        os.makedirs("assets/images", exist_ok=True)

    @staticmethod
    def take_photo(callback=None):
        """Prend une photo avec la caméra"""
        try:
            ImageManager.ensure_assets_folder()
            photo_path = f"assets/images/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            if platform == 'android':
                # Sur Android, utiliser l'implémentation standard
                camera.take_picture(
                    filename=photo_path,
                    on_complete=lambda path: callback(path) if callback else None
                )
            else:
                # Sur desktop, simuler avec un filechooser
                print("Fonction caméra simulée sur desktop - utilisez la galerie")
                if callback:
                    callback(None)
            
            return photo_path
        except Exception as e:
            print(f"Erreur caméra: {e}")
            if callback:
                callback(None)
            return None

    @staticmethod
    def select_from_gallery(callback=None):
        """Sélectionne une image depuis la galerie"""
        try:
            ImageManager.ensure_assets_folder()
            
            def handle_selection(selection):
                if selection:
                    source_path = selection[0]
                    file_ext = os.path.splitext(source_path)[1]
                    new_filename = f"assets/images/gallery_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
                    
                    try:
                        shutil.copy2(source_path, new_filename)
                        if callback:
                            callback(new_filename)
                    except Exception as e:
                        print(f"Erreur copie image: {e}")
                        if callback:
                            callback(None)
                else:
                    if callback:
                        callback(None)
            
            filechooser.open_file(
                title="Sélectionner une image",
                filters=[["Images", "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"]],
                on_selection=handle_selection
            )
            
        except Exception as e:
            print(f"Erreur galerie: {e}")
            if callback:
                callback(None)
            return None

    @staticmethod
    def get_default_image():
        """Retourne le chemin de l'image par défaut"""
        return "assets/logo.png"
