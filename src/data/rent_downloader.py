"""Téléchargement des données de la Carte des loyers depuis data.gouv.fr."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from tqdm import tqdm

from src.utils.config import RAW_DATA_DIR, RENT_CSV_URLS, RENT_CUSTOM_URLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RentDownloader:
    """Gestionnaire de téléchargement des données de la Carte des loyers."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialise le téléchargeur de données de loyers.

        Args:
            data_dir: Répertoire de stockage des données (par défaut: RAW_DATA_DIR)
        """
        self.data_dir = data_dir or RAW_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_rent_data(
        self, year: int = 2024, custom_url: Optional[str] = None, force: bool = False
    ) -> Optional[Path]:
        """
        Télécharge les données de la Carte des loyers pour une année.

        Args:
            year: Année des données (par défaut: 2024)
            custom_url: URL personnalisée pour le fichier CSV (optionnel)
            force: Force le téléchargement même si le fichier existe

        Returns:
            Chemin vers le fichier téléchargé, ou None en cas d'erreur
        """
        output_file = self.data_dir / f"carte_loyers_{year}.csv"

        if output_file.exists() and not force:
            logger.info(f"Fichier déjà existant: {output_file}")
            return output_file

        # Déterminer l'URL à utiliser
        if custom_url:
            url = custom_url
            logger.info(f"Utilisation de l'URL personnalisée: {url}")
        elif year in RENT_CUSTOM_URLS:
            url = RENT_CUSTOM_URLS[year]
            logger.info(f"Utilisation de l'URL custom depuis config: {url}")
        elif year in RENT_CSV_URLS:
            url = RENT_CSV_URLS[year]
            logger.info(f"Utilisation de l'URL par défaut depuis config: {url}")
        else:
            logger.error(
                f"❌ Aucune URL configurée pour l'année {year}. "
                f"Veuillez ajouter l'URL dans RENT_CSV_URLS ou RENT_CUSTOM_URLS dans config.py, "
                f"ou passer custom_url en paramètre."
            )
            return None

        try:
            logger.info(f"Téléchargement des données de loyers {year}...")
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(output_file, "wb") as f, tqdm(
                desc="Téléchargement loyers",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            logger.info(f"✓ Téléchargé: {output_file}")
            return output_file

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Erreur téléchargement données loyers {year}: {e}")
            if output_file.exists():
                output_file.unlink()
            return None

    def download_rent_data_from_url(self, url: str, year: int = 2024) -> Optional[Path]:
        """
        Télécharge les données de la Carte des loyers depuis une URL personnalisée.

        Args:
            url: URL du fichier CSV
            year: Année des données

        Returns:
            Chemin vers le fichier téléchargé, ou None en cas d'erreur
        """
        output_file = self.data_dir / f"carte_loyers_{year}.csv"

        if output_file.exists():
            logger.info(f"Fichier déjà existant: {output_file}")
            return output_file

        try:
            logger.info(f"Téléchargement: {url}")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(output_file, "wb") as f, tqdm(
                desc="Téléchargement loyers",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            logger.info(f"✓ Téléchargé: {output_file}")
            return output_file

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Erreur téléchargement: {e}")
            if output_file.exists():
                output_file.unlink()
            return None

    def load_rent_data(self, year: int = 2024) -> pd.DataFrame:
        """
        Charge les données de la Carte des loyers.

        Args:
            year: Année des données

        Returns:
            DataFrame contenant les données de loyers
        """
        file_path = self.data_dir / f"carte_loyers_{year}.csv"
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Fichier non trouvé: {file_path}. "
                f"Utilisez download_rent_data({year}) ou download_rent_data_from_url() d'abord."
            )

        try:
            # Charger les données avec le bon encodage
            df = pd.read_csv(file_path, sep=",", low_memory=False)
            logger.info(f"✓ Chargé: {len(df)} communes avec données de loyers")
            
            # Afficher les colonnes disponibles pour vérification
            logger.info(f"Colonnes disponibles: {df.columns.tolist()}")
            
            return df

        except Exception as e:
            logger.error(f"Erreur chargement {file_path}: {e}")
            raise

    def filter_idf_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtre les données pour ne garder que l'Île-de-France.

        Args:
            df: DataFrame des données de loyers

        Returns:
            DataFrame filtré pour l'IDF
        """
        # Codes des départements d'Île-de-France
        idf_departments = ["75", "77", "78", "91", "92", "93", "94", "95"]
        
        if "DEP" in df.columns:
            df_idf = df[df["DEP"].astype(str).isin(idf_departments)].copy()
            logger.info(f"✓ Filtré IDF: {len(df_idf)} communes sur {len(df)}")
            return df_idf
        else:
            logger.warning("⚠ Colonne 'DEP' non trouvée, impossible de filtrer par département")
            return df

    def save_as_parquet(self, df: pd.DataFrame, year: int = 2024) -> Path:
        """
        Sauvegarde le DataFrame au format Parquet pour optimiser le stockage.

        Args:
            df: DataFrame à sauvegarder
            year: Année des données

        Returns:
            Chemin vers le fichier Parquet
        """
        output_file = self.data_dir / f"carte_loyers_{year}.parquet"
        df.to_parquet(output_file, engine="pyarrow", compression="snappy")
        logger.info(f"✓ Sauvegardé: {output_file} ({output_file.stat().st_size / 1e6:.1f} MB)")
        return output_file


if __name__ == "__main__":
    # Exemple d'utilisation
    downloader = RentDownloader()
    
    # Si vous connaissez l'URL exacte du fichier CSV:
    # url = "https://URL_EXACTE_DU_FICHIER.csv"
    # downloader.download_rent_data_from_url(url, year=2024)
    
    # Sinon, essayer le téléchargement par défaut:
    downloader.download_rent_data(year=2024)
    
    # Charger les données
    df = downloader.load_rent_data(year=2024)
    print(f"\nAperçu des données:\n{df.head()}")
    print(f"\nInfo:\n{df.info()}")
    
    # Filtrer pour l'IDF
    df_idf = downloader.filter_idf_data(df)
    
    # Sauvegarder en Parquet
    downloader.save_as_parquet(df_idf, year=2024)
