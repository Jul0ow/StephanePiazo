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

# Configuration de filtrage
MIN_PRICE_M2: Final[float] = 500.0  # Prix minimum au m² pour filtrer les aberrations
MAX_PRICE_M2: Final[float] = 25000.0  # Prix maximum au m² pour filtrer les aberrations
MIN_SURFACE: Final[float] = 9.0  # Surface minimum en m² (loi Carrez)

# Types de mutations à considérer
VALID_MUTATION_TYPES: Final[list[str]] = ["Vente"]

# Types de biens locaux
LOCAL_TYPES: Final[dict[str, str]] = {
    "Appartement": "Appartement",
    "Maison": "Maison",
    "Dépendance": "Dépendance",
    "Local industriel. commercial ou assimilé": "Local commercial/industriel",
}
