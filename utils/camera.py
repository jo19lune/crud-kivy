from plyer import camera, filechooser
import os
from datetime import datetime
from kivy import platform
import shutil
import urllib.parse
import sys

# Import de la configuration
try:
    from config import get_images_path, get_project_root, get_assets_path
except ImportError:
    # Fallback si config.py n'existe pas
    def get_project_root():
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def get_assets_path():
        return os.path.join(get_project_root(), "assets")
    
    def get_images_path():
        return os.path.join(get_project_root(), "assets", "images")

class ImageManager:
    @staticmethod
    def ensure_assets_folder():
        """Crée le dossier assets/images s'il n'existe pas"""
        images_path = get_images_path()
        os.makedirs(images_path, exist_ok=True)
        
        # S'assurer que logo.png existe
        logo_path = os.path.join(get_assets_path(), "logo.png")
        if not os.path.exists(logo_path):
            print(f"⚠️ Logo non trouvé: {logo_path}")
            # Créer un logo par défaut si nécessaire
            ImageManager._create_default_logo()

    @staticmethod
    def _create_default_logo():
        """Crée un logo par défaut si il n'existe pas"""
        try:
            logo_path = os.path.join(get_assets_path(), "logo.png")
            # Créer un PNG 1x1 pixel transparent
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82'
            with open(logo_path, 'wb') as f:
                f.write(png_data)
            print(f"✅ Logo par défaut créé: {logo_path}")
        except Exception as e:
            print(f"❌ Erreur création logo: {e}")

    @staticmethod
    def get_default_image():
        """Retourne le chemin ABSOLU de l'image par défaut"""
        logo_path = os.path.join(get_assets_path(), "logo.png")
        print(f"📍 Chemin logo: {logo_path}")
        print(f"📍 Logo existe: {os.path.exists(logo_path)}")
        return logo_path

    @staticmethod
    def take_photo(callback=None):
        """Prend une photo avec la caméra"""
        try:
            ImageManager.ensure_assets_folder()
            images_path = get_images_path()
            photo_path = os.path.join(images_path, f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            
            print(f"Tentative de prise de photo vers: {photo_path}")
            
            if platform == 'android':
                camera.take_picture(
                    filename=photo_path,
                    on_complete=lambda path: callback(path) if callback else None
                )
            else:
                # Sur desktop, utiliser directement la galerie
                ImageManager.select_from_gallery(callback)
            
            return photo_path
        except Exception as e:
            print(f"Erreur caméra: {e}")
            ImageManager.select_from_gallery(callback)
            return None

    @staticmethod
    def select_from_gallery(callback=None):
        """Sélectionne une image depuis la galerie"""
        try:
            def handle_selection(selection):
                if not selection:
                    print("Aucune image sélectionnée")
                    if callback:
                        callback(None)
                    return
                
                source_path = selection[0]
                print(f"Fichier sélectionné: {source_path}")
                
                # Méthode robuste pour obtenir un chemin valide
                valid_path = ImageManager._get_valid_path(source_path)
                if not valid_path:
                    print("Impossible d'obtenir un chemin valide pour le fichier")
                    if callback:
                        callback(None)
                    return
                
                # Retourner le chemin original - la copie se fera plus tard lors de la sauvegarde
                if callback:
                    callback(valid_path)
            
            filechooser.open_file(
                title="Sélectionner une image",
                filters=[["Images", "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"]],
                on_selection=handle_selection
            )
            
        except Exception as e:
            print(f"Erreur galerie: {e}")
            if callback:
                callback(None)

    @staticmethod
    def copy_image_to_assets(source_path):
        """Copie l'image dans assets/images et retourne le nouveau chemin ABSOLU"""
        try:
            ImageManager.ensure_assets_folder()
            images_path = get_images_path()
            
            if not source_path or not os.path.exists(source_path):
                print(f"Fichier source introuvable: {source_path}")
                return ImageManager.get_default_image()
            
            # Obtenir l'extension du fichier
            file_ext = os.path.splitext(source_path)[1].lower()
            if not file_ext:
                file_ext = '.jpg'
            
            # Générer un nom de fichier unique
            new_filename = f"gallery_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{file_ext}"
            new_filepath = os.path.join(images_path, new_filename)
            
            print(f"=== COPIE D'IMAGE ===")
            print(f"Source: {source_path}")
            print(f"Destination: {new_filepath}")
            
            # Copier le fichier
            shutil.copy2(source_path, new_filepath)
            
            # Vérifier que la copie a réussi
            if os.path.exists(new_filepath):
                print(f"✅ Image copiée avec succès: {new_filepath}")
                return new_filepath  # Retourner le chemin ABSOLU
            else:
                print("❌ Échec de la copie de l'image")
                return ImageManager.get_default_image()
                
        except Exception as e:
            print(f"❌ Erreur lors de la copie de l'image: {e}")
            return ImageManager.get_default_image()

    @staticmethod
    def _get_valid_path(file_path):
        """Tente d'obtenir un chemin de fichier valide"""
        paths_to_try = [
            file_path,
            file_path.strip('"\' '),
            urllib.parse.unquote(file_path),
            os.path.abspath(file_path),
        ]
        
        for path in paths_to_try:
            if os.path.exists(path) and os.path.isfile(path):
                print(f"Chemin valide trouvé: {path}")
                return path
        
        print(f"Aucun chemin valide trouvé pour: {file_path}")
        return None

    @staticmethod
    def is_valid_image_path(path):
        """Vérifie si le chemin d'image est valide"""
        if not path:
            return False
            
        # Vérifier si le chemin existe
        if os.path.exists(path):
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            file_ext = os.path.splitext(path)[1].lower()
            return file_ext in valid_extensions
        
        return False
