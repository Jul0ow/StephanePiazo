"""
Exemple d'utilisation du téléchargement avec URLs personnalisées.

Ce script montre comment télécharger des données DVF et de la Carte des loyers
en utilisant des URLs personnalisées au lieu des URLs par défaut.
"""

import logging
from pathlib import Path

from src.data.dvf_downloader import DVFDownloader
from src.data.rent_downloader import RentDownloader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def example_1_rent_with_custom_url():
    """
    Exemple 1: Télécharger la Carte des loyers avec une URL personnalisée.
    
    Utilisez cette méthode si vous avez trouvé une URL spécifique
    pour le fichier CSV de la Carte des loyers.
    """
    print("\n" + "="*70)
    print("EXEMPLE 1: Téléchargement de la Carte des loyers avec URL custom")
    print("="*70 + "\n")
    
    downloader = RentDownloader()
    
    # URL du fichier CSV de la Carte des loyers 2024
    # Note: Cette URL peut changer. Trouvez la bonne URL sur:
    # https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
    custom_url = (
        "https://static.data.gouv.fr/resources/"
        "carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/"
        "20241001-093315/indicateurs-loyers-par-commune.csv"
    )
    
    # Télécharger avec l'URL personnalisée
    file_path = downloader.download_rent_data(
        year=2024,
        custom_url=custom_url,
        force=False  # Ne pas re-télécharger si le fichier existe déjà
    )
    
    if file_path:
        print(f"✓ Fichier téléchargé: {file_path}")
        
        # Charger et afficher un aperçu
        df = downloader.load_rent_data(year=2024)
        print(f"\nAperçu des données ({len(df)} lignes):")
        print(df.head())
    else:
        print("✗ Erreur lors du téléchargement")


def example_2_dvf_with_custom_urls():
    """
    Exemple 2: Télécharger les données DVF avec des URLs personnalisées.
    
    Utilisez cette méthode si vous hébergez vos propres données DVF
    ou si vous voulez utiliser un miroir alternatif.
    """
    print("\n" + "="*70)
    print("EXEMPLE 2: Téléchargement DVF avec URLs personnalisées")
    print("="*70 + "\n")
    
    downloader = DVFDownloader()
    
    # Option A: URLs personnalisées pour chaque département
    custom_urls = {
        "75": "https://files.data.gouv.fr/geo-dvf/latest/csv/2023/departements/75.csv.gz",
        "92": "https://files.data.gouv.fr/geo-dvf/latest/csv/2023/departements/92.csv.gz",
    }
    
    # Télécharger seulement Paris (75) et Hauts-de-Seine (92)
    print("Téléchargement avec URLs personnalisées par département...")
    for dept_code, url in custom_urls.items():
        file_path = downloader.download_department_data(
            department=dept_code,
            year=2023,
            custom_url=url
        )
        if file_path:
            print(f"✓ {dept_code}: {file_path}")


def example_3_using_config_file():
    """
    Exemple 3: Utiliser le fichier config_urls.py pour la configuration.
    
    C'est la méthode recommandée pour une utilisation régulière.
    Les URLs sont définies une seule fois dans config_urls.py
    et automatiquement chargées à l'import du module.
    """
    print("\n" + "="*70)
    print("EXEMPLE 3: Configuration via config_urls.py")
    print("="*70 + "\n")
    
    print("1. Créez le fichier config_urls.py à la racine du projet:")
    print("   cp config_urls.example.py config_urls.py")
    print()
    print("2. Modifiez config_urls.py pour ajouter vos URLs:")
    print("""
    RENT_CUSTOM_URLS = {
        2024: "https://votre-url-custom/loyers_2024.csv",
    }
    
    DVF_CUSTOM_URLS = {
        2023: "https://votre-serveur.com/dvf/{dept}.csv.gz",
    }
    """)
    print()
    print("3. Utilisez les downloaders normalement:")
    print("""
    from src.data.rent_downloader import RentDownloader
    downloader = RentDownloader()
    # Les URLs custom seront automatiquement utilisées
    downloader.download_rent_data(year=2024)
    """)


def example_4_check_available_urls():
    """
    Exemple 4: Vérifier quelles URLs sont disponibles.
    """
    print("\n" + "="*70)
    print("EXEMPLE 4: Vérifier les URLs configurées")
    print("="*70 + "\n")
    
    from src.utils.config import (
        DVF_BASE_URL,
        DVF_CUSTOM_URLS,
        RENT_CSV_URLS,
        RENT_CUSTOM_URLS
    )
    
    print("📍 Configuration DVF:")
    print(f"  URL de base: {DVF_BASE_URL}")
    print(f"  URLs custom: {DVF_CUSTOM_URLS if DVF_CUSTOM_URLS else 'Aucune'}")
    
    print("\n📍 Configuration Carte des loyers:")
    print(f"  URLs par défaut: {RENT_CSV_URLS}")
    print(f"  URLs custom: {RENT_CUSTOM_URLS if RENT_CUSTOM_URLS else 'Aucune'}")


def example_5_download_all_idf():
    """
    Exemple 5: Télécharger toute l'Île-de-France avec configuration custom.
    """
    print("\n" + "="*70)
    print("EXEMPLE 5: Téléchargement complet IDF")
    print("="*70 + "\n")
    
    downloader = DVFDownloader()
    
    # Vous pouvez passer des URLs custom pour tous les départements
    # ou laisser None pour utiliser la config par défaut
    downloaded_files = downloader.download_idf_data(
        year=2023,
        custom_urls=None  # Utilise la config par défaut ou config_urls.py
    )
    
    print(f"\n✓ {len(downloaded_files)} départements téléchargés:")
    for dept, path in downloaded_files.items():
        print(f"  - {dept}: {path.name}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  TÉLÉCHARGEMENT AVEC URLS PERSONNALISÉES                             ║
║                                                                      ║
║  Ce script présente différentes façons de télécharger des données   ║
║  en utilisant des URLs personnalisées au lieu des URLs par défaut.  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Décommentez les exemples que vous voulez exécuter:
    
    # example_1_rent_with_custom_url()
    # example_2_dvf_with_custom_urls()
    example_3_using_config_file()
    example_4_check_available_urls()
    # example_5_download_all_idf()
    
    print("\n" + "="*70)
    print("✓ Exemples terminés!")
    print("="*70)
