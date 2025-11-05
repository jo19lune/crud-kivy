import os
import sys

def get_project_root():
    """Retourne le chemin absolu du dossier racine du projet"""
    if getattr(sys, 'frozen', False):
        # En production
        return os.path.dirname(sys.executable)
    else:
        # En développement
        return os.path.dirname(os.path.abspath(sys.argv[0]))

PROJECT_ROOT = get_project_root()

def get_assets_path():
    """Retourne le chemin absolu vers le dossier assets"""
    return os.path.join(PROJECT_ROOT, "assets")

def get_images_path():
    """Retourne le chemin absolu vers assets/images"""
    return os.path.join(PROJECT_ROOT, "assets", "images")

def get_data_path():
    """Retourne le chemin absolu vers le dossier data"""
    return os.path.join(PROJECT_ROOT, "data")

def get_database_path():
    """Retourne le chemin absolu vers la base de données"""
    return os.path.join(PROJECT_ROOT, "data", "database.json")

# Afficher les chemins pour débogage
print("=== CONFIGURATION DES CHEMINS ===")
print(f"Racine du projet: {PROJECT_ROOT}")
print(f"Dossier assets: {get_assets_path()}")
print(f"Dossier images: {get_images_path()}")
print(f"Dossier data: {get_data_path()}")
print(f"Base de données: {get_database_path()}")
print("==================================")
