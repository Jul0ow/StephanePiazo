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
        self, 
        year: int = 2024, 
        custom_url: Optional[str | dict[str, str]] = None, 
        force: bool = False
    ) -> Optional[Path | dict[str, Path]]:
        """
        Télécharge les données de la Carte des loyers pour une année.
        
        Pour les années avec fichiers séparés (appartements/maisons), retourne un dict.
        Pour les années avec fichier unique, retourne un Path.

        Args:
            year: Année des données (par défaut: 2024)
            custom_url: URL(s) personnalisée(s) - str ou dict["appartements"/"maisons": url]
            force: Force le téléchargement même si le fichier existe

        Returns:
            Path ou dict[str, Path] vers le(s) fichier(s) téléchargé(s), ou None en cas d'erreur
        """
        # Déterminer les URLs à utiliser
        urls_to_download: dict[str, str] | str
        
        if custom_url:
            urls_to_download = custom_url
            logger.info(f"Utilisation d'URL(s) personnalisée(s)")
        elif year in RENT_CUSTOM_URLS:
            urls_to_download = RENT_CUSTOM_URLS[year]
            logger.info(f"Utilisation d'URL(s) custom depuis config")
        elif year in RENT_CSV_URLS:
            urls_to_download = RENT_CSV_URLS[year]
            logger.info(f"Utilisation d'URL(s) par défaut depuis config")
        else:
            logger.error(
                f"❌ Aucune URL configurée pour l'année {year}. "
                f"Veuillez ajouter l'URL dans RENT_CSV_URLS ou RENT_CUSTOM_URLS dans config.py, "
                f"ou passer custom_url en paramètre."
            )
            return None

        # Si URLs multiples (dict), télécharger chaque fichier
        if isinstance(urls_to_download, dict):
            downloaded_files = {}
            for property_type, url in urls_to_download.items():
                output_file = self.data_dir / f"carte_loyers_{year}_{property_type}.csv"
                
                if output_file.exists() and not force:
                    logger.info(f"Fichier déjà existant: {output_file}")
                    downloaded_files[property_type] = output_file
                    continue
                
                result = self._download_file(url, output_file, f"loyers {year} {property_type}")
                if result:
                    downloaded_files[property_type] = result
                else:
                    logger.error(f"❌ Échec téléchargement {property_type}")
                    return None
            
            return downloaded_files if downloaded_files else None
        
        # Sinon, télécharger un seul fichier (ancien format)
        else:
            output_file = self.data_dir / f"carte_loyers_{year}.csv"
            
            if output_file.exists() and not force:
                logger.info(f"Fichier déjà existant: {output_file}")
                return output_file
            
            return self._download_file(urls_to_download, output_file, f"loyers {year}")

    def _download_file(self, url: str, output_file: Path, description: str) -> Optional[Path]:
        """
        Télécharge un fichier depuis une URL.

        Args:
            url: URL du fichier
            output_file: Chemin de destination
            description: Description pour les logs

        Returns:
            Path du fichier téléchargé ou None en cas d'erreur
        """
        try:
            logger.info(f"Téléchargement {description}...")
            logger.info(f"URL: {url}")
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(output_file, "wb") as f, tqdm(
                desc=f"Téléchargement {description}",
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
            logger.error(f"✗ Erreur téléchargement {description}: {e}")
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

    def load_rent_data(self, year: int = 2024, property_type: Optional[str] = None) -> pd.DataFrame:
        """
        Charge les données de la Carte des loyers.
        
        Pour les années avec fichiers séparés, combine les données des appartements et maisons.
        Utiliser property_type pour charger uniquement un type de bien.

        Args:
            year: Année des données
            property_type: Type de bien (« appartements » ou « maisons ») ou None pour tout

        Returns:
            DataFrame contenant les données de loyers
        """
        # Vérifier si fichiers séparés ou unique
        file_appartements = self.data_dir / f"carte_loyers_{year}_appartements.csv"
        file_maisons = self.data_dir / f"carte_loyers_{year}_maisons.csv"
        file_unique = self.data_dir / f"carte_loyers_{year}.csv"
        
        has_separated_files = file_appartements.exists() or file_maisons.exists()
        has_unique_file = file_unique.exists()
        
        if not has_separated_files and not has_unique_file:
            raise FileNotFoundError(
                f"Aucun fichier de données trouvé pour {year}. "
                f"Utilisez download_rent_data({year}) d'abord."
            )

        try:
            # Cas 1: Fichiers séparés (appartements + maisons)
            if has_separated_files:
                dataframes = []
                
                # Charger appartements si demandé ou si pas de filtre
                if property_type in (None, "appartements"):
                    if file_appartements.exists():
                        # Essayer différents encodages et séparateurs
                        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                            try:
                                # Utiliser sep=None pour détecter automatiquement le séparateur
                                df_appart = pd.read_csv(file_appartements, sep=None, engine='python', encoding=encoding)
                                df_appart["type_bien"] = "appartements"
                                dataframes.append(df_appart)
                                logger.info(f"✓ Chargé appartements: {len(df_appart)} communes (encodage: {encoding})")
                                break
                            except UnicodeDecodeError:
                                if encoding == 'cp1252':  # Dernier encodage
                                    raise
                                continue
                    elif property_type == "appartements":
                        raise FileNotFoundError(f"Fichier appartements non trouvé: {file_appartements}")
                
                # Charger maisons si demandé ou si pas de filtre
                if property_type in (None, "maisons"):
                    if file_maisons.exists():
                        # Essayer différents encodages et séparateurs
                        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                            try:
                                # Utiliser sep=None pour détecter automatiquement le séparateur
                                df_maisons = pd.read_csv(file_maisons, sep=None, engine='python', encoding=encoding)
                                df_maisons["type_bien"] = "maisons"
                                dataframes.append(df_maisons)
                                logger.info(f"✓ Chargé maisons: {len(df_maisons)} communes (encodage: {encoding})")
                                break
                            except UnicodeDecodeError:
                                if encoding == 'cp1252':  # Dernier encodage
                                    raise
                                continue
                    elif property_type == "maisons":
                        raise FileNotFoundError(f"Fichier maisons non trouvé: {file_maisons}")
                
                if not dataframes:
                    raise ValueError(f"Aucune donnée chargée pour property_type={property_type}")
                
                # Combiner les dataframes
                df = pd.concat(dataframes, ignore_index=True)
                logger.info(f"✓ Total: {len(df)} enregistrements de loyers")
            
            # Cas 2: Fichier unique (ancien format)
            else:
                # Essayer différents encodages et séparateurs
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        # Utiliser sep=None pour détecter automatiquement le séparateur
                        df = pd.read_csv(file_unique, sep=None, engine='python', encoding=encoding)
                        df["type_bien"] = "tous"  # Marquer comme données combinées
                        logger.info(f"✓ Chargé: {len(df)} communes avec données de loyers (encodage: {encoding})")
                        break
                    except UnicodeDecodeError:
                        if encoding == 'cp1252':  # Dernier encodage
                            raise
                        continue
            
            # Nettoyer les noms de colonnes
            df = self._clean_column_names(df)
            
            # Convertir les colonnes numériques (format français vers float)
            df = self._convert_numeric_columns(df)
            
            # Afficher les colonnes disponibles pour vérification
            logger.info(f"Colonnes disponibles: {df.columns.tolist()}")
            
            return df

        except Exception as e:
            logger.error(f"Erreur chargement données loyers {year}: {e}")
            raise

    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les noms de colonnes (supprime guillemets, normalise).
        
        Args:
            df: DataFrame avec colonnes à nettoyer
            
        Returns:
            DataFrame avec noms de colonnes nettoyés
        """
        # Supprimer les guillemets et espaces
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False)
        
        # Normaliser les noms (remplacer points par underscores pour cohérence)
        df.columns = df.columns.str.replace('.', '_', regex=False)
        
        logger.info(f"✓ Noms de colonnes nettoyés")
        return df
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convertit les colonnes numériques du format français (virgules) vers float.
        
        Args:
            df: DataFrame avec valeurs à convertir
            
        Returns:
            DataFrame avec colonnes numériques converties
        """
        # Colonnes numériques connues dans les données de loyers
        numeric_columns = ['loypredm2', 'lwr_IPm2', 'upr_IPm2', 'nbobs_com', 'nbobs_mail', 'R2_adj']
        
        for col in numeric_columns:
            if col in df.columns:
                # Remplacer virgules par points et convertir en float
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"✓ Colonnes numériques converties en float")
        return df
    
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
            logger.warning("⚠ Colonne 'DEP' non trouvée, impossible de filtrer par département", df.columns)
            return df

    def save_as_parquet(self, df: pd.DataFrame, year: int = 2024, property_type: Optional[str] = None) -> Path:
        """
        Sauvegarde le DataFrame au format Parquet pour optimiser le stockage.

        Args:
            df: DataFrame à sauvegarder
            year: Année des données
            property_type: Type de bien si fichiers séparés (optionnel)

        Returns:
            Chemin vers le fichier Parquet
        """
        suffix = f"_{property_type}" if property_type else ""
        output_file = self.data_dir / f"carte_loyers_{year}{suffix}.parquet"
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
