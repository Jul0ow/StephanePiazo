"""Configuration globale du projet."""

from pathlib import Path
from typing import Final

# Chemins du projet
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
OUTPUTS_DIR: Final[Path] = PROJECT_ROOT / "outputs"
REPORTS_DIR: Final[Path] = OUTPUTS_DIR / "reports"
VISUALIZATIONS_DIR: Final[Path] = OUTPUTS_DIR / "visualizations"

# Créer les répertoires s'ils n'existent pas
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, VISUALIZATIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration API DVF
DVF_BASE_URL: Final[str] = "https://files.data.gouv.fr/geo-dvf/latest/csv"
DVF_YEARS_AVAILABLE: Final[list[int]] = list(range(2014, 2025))  # DVF disponible depuis 2014

# URLs DVF personnalisées par année et département (optionnel)
# Format: {year: {dept: "url"}} ou {year: "url_template_avec_{dept}"}
DVF_CUSTOM_URLS: dict[int, dict[str, str] | str] = {
    # Exemple:
    # 2023: "https://mon-serveur.com/dvf/{dept}.csv.gz",
    # 2024: {"75": "https://mon-url-custom.com/paris.csv.gz"}
}

# Configuration Carte des loyers
RENT_DATA_BASE_URL: Final[str] = "https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/"
RENT_YEARS_AVAILABLE: Final[list[int]] = [2024]  # Carte des loyers disponible pour 2024

# URLs des fichiers CSV de la Carte des loyers 2024
# Note: À partir de 2024, les données sont séparées en 2 fichiers (appartements et maisons)
# Pour trouver les bonnes URLs:
# 1. Allez sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
# 2. Cliquez sur chaque fichier CSV dans la liste des ressources
# 3. Copiez l'URL du bouton "Télécharger"

RENT_CSV_URL_2024_APPARTEMENTS: Final[str] = (
    #"https://static.data.gouv.fr/resources/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/20241205-153050/pred-app-mef-dhup.csv"
    #"https://static.data.gouv.fr/resources/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/20241205-153048/pred-app12-mef-dhup.csv"
    "https://static.data.gouv.fr/resources/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/20241205-145658/pred-app3-mef-dhup.csv"
)

RENT_CSV_URL_2024_MAISONS: Final[str] = (
    "https://static.data.gouv.fr/resources/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/20241205-145700/pred-mai-mef-dhup.csv"
)

# Dictionnaire des URLs par année et type de bien
# Format: {year: {"appartements": url, "maisons": url} ou str pour fichier unique}
RENT_CSV_URLS: Final[dict[int, dict[str, str] | str]] = {
    2024: {
        "appartements": RENT_CSV_URL_2024_APPARTEMENTS,
        "maisons": RENT_CSV_URL_2024_MAISONS,
    },
    # 2025: {"appartements": "URL_APPART", "maisons": "URL_MAISONS"},  # À compléter
}

# Configuration personnalisée pour les URLs de loyers
# Permet de surcharger les URLs par défaut
# Peut être une string (fichier unique) ou un dict (appartements/maisons séparés)
RENT_CUSTOM_URLS: dict[int, dict[str, str] | str] = {
    # Exemple pour un fichier unique:
    # 2023: "https://mon-serveur.com/loyers_2023.csv",
    # Exemple pour fichiers séparés:
    # 2024: {"appartements": "https://...", "maisons": "https://..."},
}

# Départements Île-de-France
IDF_DEPARTMENTS: Final[dict[str, str]] = {
    "75": "Paris",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
}

# Configuration de filtrage DVF
MIN_PRICE_M2: Final[float] = 500.0  # Prix minimum au m² pour filtrer les aberrations
MAX_PRICE_M2: Final[float] = 40000.0  # Prix maximum au m² pour filtrer les aberrations
MIN_SURFACE: Final[float] = 9.0  # Surface minimum en m² (loi Carrez)

# Configuration de filtrage Carte des loyers
MIN_RENT_M2: Final[float] = 5.0  # Loyer minimum au m² pour filtrer les aberrations
MAX_RENT_M2: Final[float] = 100.0  # Loyer maximum au m² pour filtrer les aberrations
MIN_R2_THRESHOLD: Final[float] = 0.5  # Seuil minimum de R² pour considérer les données fiables
MIN_OBSERVATIONS: Final[int] = 30  # Nombre minimum d'observations pour données fiables

# Types de mutations à considérer
VALID_MUTATION_TYPES: Final[list[str]] = ["Vente"]

# Types de biens locaux
LOCAL_TYPES: Final[dict[str, str]] = {
    "Appartement": "Appartement",
    "Maison": "Maison",
    "Dépendance": "Dépendance",
    "Local industriel. commercial ou assimilé": "Local commercial/industriel",
}

# =============================================================================
# CHARGEMENT DE LA CONFIGURATION PERSONNALISÉE
# =============================================================================

# Charger les URLs personnalisées depuis config_urls.py (si le fichier existe)
def _load_custom_config() -> None:
    """Charge la configuration personnalisée depuis config_urls.py."""
    config_file = PROJECT_ROOT / "config_urls.py"
    
    if not config_file.exists():
        return
    
    try:
        import importlib.util
        import sys
        
        # Charger le module dynamiquement
        spec = importlib.util.spec_from_file_location("config_urls", config_file)
        if spec and spec.loader:
            config_urls = importlib.util.module_from_spec(spec)
            sys.modules["config_urls"] = config_urls
            spec.loader.exec_module(config_urls)
            
            # Fusionner les URLs DVF personnalisées
            if hasattr(config_urls, "DVF_CUSTOM_URLS"):
                DVF_CUSTOM_URLS.update(config_urls.DVF_CUSTOM_URLS)
                print(f"✓ URLs DVF personnalisées chargées depuis config_urls.py")
            
            # Fusionner les URLs de loyers personnalisées
            if hasattr(config_urls, "RENT_CUSTOM_URLS"):
                RENT_CUSTOM_URLS.update(config_urls.RENT_CUSTOM_URLS)
                print(f"✓ URLs de loyers personnalisées chargées depuis config_urls.py")
    
    except Exception as e:
        print(f"⚠ Erreur lors du chargement de config_urls.py: {e}")

# Charger automatiquement au démarrage
_load_custom_config()
