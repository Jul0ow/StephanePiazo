"""Nettoyage et préparation des données DVF."""

import logging
from typing import Optional

import pandas as pd

from src.utils.config import (
    MAX_PRICE_M2,
    MIN_PRICE_M2,
    MIN_SURFACE,
    PROCESSED_DATA_DIR,
    VALID_MUTATION_TYPES,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Nettoyeur de données DVF."""

    def __init__(self):
        """Initialise le nettoyeur de données."""
        self.processed_dir = PROCESSED_DATA_DIR
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def clean_dvf_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les données DVF brutes.

        Args:
            df: DataFrame DVF brut

        Returns:
            DataFrame nettoyé
        """
        logger.info(f"Nettoyage des données: {len(df)} lignes initiales")
        initial_count = len(df)

        # Copie pour éviter les modifications du DataFrame original
        df_clean = df.copy()

        # 1. Filtrer sur le type de mutation
        df_clean = df_clean[df_clean["nature_mutation"].isin(VALID_MUTATION_TYPES)]
        logger.info(f"  Après filtre mutation: {len(df_clean)} lignes")

        # 2. Garder uniquement les lignes avec valeur foncière
        df_clean = df_clean[df_clean["valeur_fonciere"].notna()]
        df_clean = df_clean[df_clean["valeur_fonciere"] > 0]
        logger.info(f"  Après filtre valeur foncière: {len(df_clean)} lignes")

        # 3. Garder uniquement les lignes avec surface réelle bâti
        df_clean = df_clean[df_clean["surface_reelle_bati"].notna()]
        df_clean = df_clean[df_clean["surface_reelle_bati"] >= MIN_SURFACE]
        logger.info(f"  Après filtre surface (>= {MIN_SURFACE}m²): {len(df_clean)} lignes")

        # 4. Calculer le prix au m²
        df_clean["prix_m2"] = df_clean["valeur_fonciere"] / df_clean["surface_reelle_bati"]

        # 5. Filtrer les prix aberrants
        df_clean = df_clean[
            (df_clean["prix_m2"] >= MIN_PRICE_M2) & (df_clean["prix_m2"] <= MAX_PRICE_M2)
        ]
        logger.info(
            f"  Après filtre prix ({MIN_PRICE_M2}-{MAX_PRICE_M2}€/m²): {len(df_clean)} lignes"
        )

        # 6. Garder uniquement les colonnes utiles
        columns_to_keep = [
            "date_mutation",
            "nature_mutation",
            "valeur_fonciere",
            "code_commune",
            "nom_commune",
            "code_departement",
            "type_local",
            "surface_reelle_bati",
            "nombre_pieces_principales",
            "prix_m2",
        ]

        # Vérifier que les colonnes existent
        available_columns = [col for col in columns_to_keep if col in df_clean.columns]
        df_clean = df_clean[available_columns]

        # 7. Convertir la date
        if "date_mutation" in df_clean.columns:
            df_clean["date_mutation"] = pd.to_datetime(df_clean["date_mutation"], errors="coerce")

        # 8. Nettoyer les noms de communes
        if "nom_commune" in df_clean.columns:
            df_clean["nom_commune"] = df_clean["nom_commune"].str.strip().str.title()

        # Supprimer les doublons potentiels
        df_clean = df_clean.drop_duplicates()

        removed_count = initial_count - len(df_clean)
        removed_pct = (removed_count / initial_count) * 100
        logger.info(
            f"✓ Nettoyage terminé: {len(df_clean)} lignes conservées "
            f"({removed_count} supprimées, {removed_pct:.1f}%)"
        )

        return df_clean

    def save_cleaned_data(self, df: pd.DataFrame, year: int, suffix: str = "") -> None:
        """
        Sauvegarde les données nettoyées.

        Args:
            df: DataFrame nettoyé
            year: Année des données
            suffix: Suffixe optionnel pour le nom de fichier
        """
        filename = f"dvf_{year}_idf_clean{suffix}.parquet"
        output_path = self.processed_dir / filename
        df.to_parquet(output_path, engine="pyarrow", compression="snappy")
        logger.info(f"✓ Données nettoyées sauvegardées: {output_path}")

    def load_cleaned_data(self, year: int, suffix: str = "") -> Optional[pd.DataFrame]:
        """
        Charge les données nettoyées.

        Args:
            year: Année des données
            suffix: Suffixe optionnel pour le nom de fichier

        Returns:
            DataFrame nettoyé ou None si non trouvé
        """
        filename = f"dvf_{year}_idf_clean{suffix}.parquet"
        file_path = self.processed_dir / filename

        if not file_path.exists():
            logger.warning(f"Fichier non trouvé: {file_path}")
            return None

        df = pd.read_parquet(file_path)
        logger.info(f"✓ Données nettoyées chargées: {len(df)} lignes")
        return df


if __name__ == "__main__":
    # Exemple d'utilisation
    from src.data.dvf_downloader import DVFDownloader

    # Charger les données brutes
    downloader = DVFDownloader()
    df_raw = downloader.load_idf_data(year=2023)

    # Nettoyer
    cleaner = DataCleaner()
    df_clean = cleaner.clean_dvf_data(df_raw)

    # Sauvegarder
    cleaner.save_cleaned_data(df_clean, year=2023)
