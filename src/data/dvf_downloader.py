"""Téléchargement des données DVF depuis l'API du gouvernement."""

import gzip
import logging
import shutil
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from tqdm import tqdm

from src.utils.config import DVF_BASE_URL, IDF_DEPARTMENTS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DVFDownloader:
    """Gestionnaire de téléchargement des données DVF."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialise le téléchargeur DVF.

        Args:
            data_dir: Répertoire de stockage des données (par défaut: RAW_DATA_DIR)
        """
        self.data_dir = data_dir or RAW_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_department_data(self, department: str, year: int) -> Optional[Path]:
        """
        Télécharge les données DVF pour un département et une année.

        Args:
            department: Code département (ex: "75" pour Paris)
            year: Année des données (ex: 2023)

        Returns:
            Chemin vers le fichier téléchargé (décompressé), ou None en cas d'erreur
        """
        url = f"{DVF_BASE_URL}/{year}/departements/{department}.csv.gz"
        output_file = self.data_dir / f"dvf_{year}_{department}.csv"
        gz_file = self.data_dir / f"dvf_{year}_{department}.csv.gz"

        if output_file.exists():
            logger.info(f"Fichier déjà existant: {output_file}")
            return output_file

        try:
            logger.info(f"Téléchargement: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            # Télécharger le fichier .gz
            with open(gz_file, "wb") as f, tqdm(
                desc=f"Dept {department}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            # Décompresser le fichier
            logger.info(f"Décompression de {gz_file.name}...")
            with gzip.open(gz_file, "rb") as f_in:
                with open(output_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Supprimer le fichier .gz après décompression
            gz_file.unlink()

            logger.info(f"✓ Téléchargé et décompressé: {output_file}")
            return output_file

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Erreur téléchargement {department}/{year}: {e}")
            if gz_file.exists():
                gz_file.unlink()
            if output_file.exists():
                output_file.unlink()
            return None
        except Exception as e:
            logger.error(f"✗ Erreur décompression {department}/{year}: {e}")
            if gz_file.exists():
                gz_file.unlink()
            if output_file.exists():
                output_file.unlink()
            return None

    def download_idf_data(self, year: int) -> dict[str, Path]:
        """
        Télécharge les données DVF pour tous les départements d'Île-de-France.

        Args:
            year: Année des données

        Returns:
            Dictionnaire {code_dept: chemin_fichier}
        """
        logger.info(f"Téléchargement des données DVF {year} pour l'Île-de-France")

        downloaded_files = {}
        for dept_code in IDF_DEPARTMENTS.keys():
            file_path = self.download_department_data(dept_code, year)
            if file_path:
                downloaded_files[dept_code] = file_path

        logger.info(f"✓ {len(downloaded_files)}/{len(IDF_DEPARTMENTS)} départements téléchargés")
        return downloaded_files

    def load_idf_data(self, year: int) -> pd.DataFrame:
        """
        Charge et combine les données DVF de tous les départements IDF.

        Args:
            year: Année des données

        Returns:
            DataFrame contenant toutes les données IDF
        """
        dfs = []

        for dept_code in IDF_DEPARTMENTS.keys():
            file_path = self.data_dir / f"dvf_{year}_{dept_code}.csv"
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path, low_memory=False)
                    df["code_departement"] = dept_code
                    dfs.append(df)
                    logger.info(f"Chargé {len(df)} lignes pour le département {dept_code}")
                except Exception as e:
                    logger.error(f"Erreur chargement {file_path}: {e}")
            else:
                logger.warning(f"Fichier non trouvé: {file_path}")

        if not dfs:
            raise FileNotFoundError(
                f"Aucun fichier DVF trouvé pour {year}. "
                f"Utilisez download_idf_data({year}) d'abord."
            )

        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"✓ Total: {len(combined_df)} transactions chargées")
        return combined_df

    def save_as_parquet(self, df: pd.DataFrame, year: int) -> Path:
        """
        Sauvegarde le DataFrame au format Parquet pour optimiser le stockage.

        Args:
            df: DataFrame à sauvegarder
            year: Année des données

        Returns:
            Chemin vers le fichier Parquet
        """
        output_file = self.data_dir / f"dvf_{year}_idf.parquet"
        df.to_parquet(output_file, engine="pyarrow", compression="snappy")
        logger.info(f"✓ Sauvegardé: {output_file} ({output_file.stat().st_size / 1e6:.1f} MB)")
        return output_file


if __name__ == "__main__":
    # Exemple d'utilisation
    downloader = DVFDownloader()
    downloader.download_idf_data(year=2023)

    # Charger et convertir en Parquet
    df = downloader.load_idf_data(year=2023)
    downloader.save_as_parquet(df, year=2023)
