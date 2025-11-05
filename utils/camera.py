from plyer import camera, filechooser
import os
from datetime import datetime
from kivy import platform
import shutil
import urllib.parse
import sys

class ImageManager:
    @staticmethod
    def get_base_dir():
        """Retourne le chemin absolu du dossier de base du projet"""
        # Si on est dans un environnement frozen (exe, apk)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            # En développement, utiliser le dossier du script principal
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return base_dir

    @staticmethod
    def get_assets_images_path():
        """Retourne le chemin absolu vers assets/images"""
        base_dir = ImageManager.get_base_dir()
        return os.path.join(base_dir, "assets", "images")

    @staticmethod
    def ensure_assets_folder():
        """Crée le dossier assets/images s'il n'existe pas"""
        assets_path = ImageManager.get_assets_images_path()
        os.makedirs(assets_path, exist_ok=True)

    @staticmethod
    def take_photo(callback=None):
        """Prend une photo avec la caméra"""
        try:
            ImageManager.ensure_assets_folder()
            assets_path = ImageManager.get_assets_images_path()
            photo_path = os.path.join(assets_path, f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            
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
        """Sélectionne une image depuis la galerie - retourne le chemin temporaire"""
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
        """Copie l'image dans assets/images et retourne le nouveau chemin"""
        try:
            ImageManager.ensure_assets_folder()
            assets_path = ImageManager.get_assets_images_path()
            
            if not source_path or not os.path.exists(source_path):
                print(f"Fichier source introuvable: {source_path}")
                return ImageManager.get_default_image()
            
            # Obtenir l'extension du fichier
            file_ext = os.path.splitext(source_path)[1].lower()
            if not file_ext:
                file_ext = '.jpg'
            
            # Générer un nom de fichier unique
            new_filename = f"gallery_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{file_ext}"
            new_filepath = os.path.join(assets_path, new_filename)
            
            print(f"Tentative de copie vers: {new_filepath}")
            
            # Copier le fichier
            shutil.copy2(source_path, new_filepath)
            
            # Vérifier que la copie a réussi
            if os.path.exists(new_filepath):
                print(f"Image copiée avec succès: {new_filepath}")
                # Retourner le chemin relatif pour la base de données
                return f"assets/images/{new_filename}"
            else:
                print("Échec de la copie de l'image")
                return ImageManager.get_default_image()
                
        except Exception as e:
            print(f"Erreur lors de la copie de l'image: {e}")
            return ImageManager.get_default_image()

    @staticmethod
    def _get_valid_path(file_path):
        """Tente d'obtenir un chemin de fichier valide"""
        # Essayer différents formats de chemin
        paths_to_try = [
            file_path,  # Chemin original
            file_path.strip('"\' '),  # Sans guillemets
            urllib.parse.unquote(file_path),  # URL décodée
            os.path.abspath(file_path),  # Chemin absolu
        ]
        
        for path in paths_to_try:
            if os.path.exists(path) and os.path.isfile(path):
                print(f"Chemin valide trouvé: {path}")
                return path
        
        print(f"Aucun chemin valide trouvé pour: {file_path}")
        return None

    @staticmethod
    def get_default_image():
        """Retourne le chemin de l'image par défaut"""
        return "assets/logo.png"

    @staticmethod
    def is_valid_image_path(path):
        """Vérifie si le chemin d'image est valide"""
        if not path:
            return False
            
        # Essayer le chemin absolu
        base_dir = ImageManager.get_base_dir()
        absolute_path = os.path.join(base_dir, path)
        
        if os.path.exists(absolute_path):
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            file_ext = os.path.splitext(absolute_path)[1].lower()
            return file_ext in valid_extensions
        
        return False

