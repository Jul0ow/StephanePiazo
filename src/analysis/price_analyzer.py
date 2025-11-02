"""Analyse des prix au mètre carré."""

import logging
from typing import Optional

import pandas as pd

from src.data.data_cleaner import DataCleaner
<<<<<<< HEAD
from src.models.city import City, CityStats, PropertyTypeStats
=======
from src.models.city import City, CityStats
>>>>>>> b635870c043313b779e3bb0e5486256e81c809f2
from src.utils.config import REPORTS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Analyseur de prix immobiliers."""

    def __init__(self, df: Optional[pd.DataFrame] = None):
        """
        Initialise l'analyseur.

        Args:
            df: DataFrame avec les données DVF nettoyées. Si None, doit être chargé manuellement.
        """
        self.df = df
        self.cleaner = DataCleaner()

    def load_data(self, year: int) -> None:
        """
        Charge les données nettoyées pour une année.

        Args:
            year: Année des données
        """
        self.df = self.cleaner.load_cleaned_data(year)
        if self.df is None:
            raise FileNotFoundError(
                f"Données nettoyées non trouvées pour {year}. "
                "Lancez d'abord le téléchargement et le nettoyage."
            )

    def get_city_stats(self, city_name: str) -> Optional[CityStats]:
        """
        Calcule les statistiques pour une ville.

        Args:
            city_name: Nom de la ville

        Returns:
            Objet CityStats ou None si pas de données
        """
        if self.df is None:
            raise ValueError("Aucune donnée chargée. Utilisez load_data() d'abord.")

        # Filtrer pour la ville
        city_df = self.df[self.df["nom_commune"].str.upper() == city_name.upper()]

        if city_df.empty:
            logger.warning(f"Aucune donnée trouvée pour {city_name}")
            return None

<<<<<<< HEAD
        # Calculs statistiques globaux
=======
        # Calculs statistiques
>>>>>>> b635870c043313b779e3bb0e5486256e81c809f2
        stats = CityStats(
            prix_moyen_m2=float(city_df["prix_m2"].mean()),
            prix_median_m2=float(city_df["prix_m2"].median()),
            prix_min_m2=float(city_df["prix_m2"].min()),
            prix_max_m2=float(city_df["prix_m2"].max()),
            nombre_transactions=len(city_df),
            surface_moyenne=float(city_df["surface_reelle_bati"].mean()),
        )

        # Statistiques par type de bien si disponible
        if "type_local" in city_df.columns:
<<<<<<< HEAD
            # Appartements
            apparts = city_df[city_df["type_local"] == "Appartement"]
            if not apparts.empty:
                stats.appartements = PropertyTypeStats(
                    prix_moyen_m2=float(apparts["prix_m2"].mean()),
                    prix_min_m2=float(apparts["prix_m2"].min()),
                    prix_max_m2=float(apparts["prix_m2"].max()),
                    nombre_transactions=len(apparts),
                    surface_moyenne=float(apparts["surface_reelle_bati"].mean()),
                )

            # Maisons
            maisons = city_df[city_df["type_local"] == "Maison"]
            if not maisons.empty:
                stats.maisons = PropertyTypeStats(
                    prix_moyen_m2=float(maisons["prix_m2"].mean()),
                    prix_min_m2=float(maisons["prix_m2"].min()),
                    prix_max_m2=float(maisons["prix_m2"].max()),
                    nombre_transactions=len(maisons),
                    surface_moyenne=float(maisons["surface_reelle_bati"].mean()),
                )
=======
            apparts = city_df[city_df["type_local"] == "Appartement"]
            if not apparts.empty:
                stats.prix_moyen_appartement_m2 = float(apparts["prix_m2"].mean())

            maisons = city_df[city_df["type_local"] == "Maison"]
            if not maisons.empty:
                stats.prix_moyen_maison_m2 = float(maisons["prix_m2"].mean())
>>>>>>> b635870c043313b779e3bb0e5486256e81c809f2

        return stats

    def analyze_all_cities(self) -> pd.DataFrame:
        """
        Analyse toutes les villes du dataset.

        Returns:
            DataFrame avec les statistiques par ville
        """
        if self.df is None:
            raise ValueError("Aucune donnée chargée. Utilisez load_data() d'abord.")

        logger.info("Analyse de toutes les villes...")

        results = []
        cities = self.df["nom_commune"].unique()

        for city_name in cities:
            stats = self.get_city_stats(city_name)
            if stats:
                city_df = self.df[self.df["nom_commune"] == city_name]
                dept_code = city_df["code_departement"].iloc[0]

<<<<<<< HEAD
                result = {
                    "ville": city_name,
                    "code_departement": dept_code,
                    "prix_moyen_m2": stats.prix_moyen_m2,
                    "prix_median_m2": stats.prix_median_m2,
                    "prix_min_m2": stats.prix_min_m2,
                    "prix_max_m2": stats.prix_max_m2,
                    "nombre_transactions": stats.nombre_transactions,
                    "surface_moyenne": stats.surface_moyenne,
                }

                # Ajouter les statistiques des appartements
                if stats.appartements:
                    result.update({
                        "appart_prix_moyen_m2": stats.appartements.prix_moyen_m2,
                        "appart_prix_min_m2": stats.appartements.prix_min_m2,
                        "appart_prix_max_m2": stats.appartements.prix_max_m2,
                        "appart_nb_transactions": stats.appartements.nombre_transactions,
                        "appart_surface_moyenne": stats.appartements.surface_moyenne,
                    })
                else:
                    result.update({
                        "appart_prix_moyen_m2": None,
                        "appart_prix_min_m2": None,
                        "appart_prix_max_m2": None,
                        "appart_nb_transactions": 0,
                        "appart_surface_moyenne": None,
                    })

                # Ajouter les statistiques des maisons
                if stats.maisons:
                    result.update({
                        "maison_prix_moyen_m2": stats.maisons.prix_moyen_m2,
                        "maison_prix_min_m2": stats.maisons.prix_min_m2,
                        "maison_prix_max_m2": stats.maisons.prix_max_m2,
                        "maison_nb_transactions": stats.maisons.nombre_transactions,
                        "maison_surface_moyenne": stats.maisons.surface_moyenne,
                    })
                else:
                    result.update({
                        "maison_prix_moyen_m2": None,
                        "maison_prix_min_m2": None,
                        "maison_prix_max_m2": None,
                        "maison_nb_transactions": 0,
                        "maison_surface_moyenne": None,
                    })

                results.append(result)
=======
                results.append(
                    {
                        "ville": city_name,
                        "code_departement": dept_code,
                        "prix_moyen_m2": stats.prix_moyen_m2,
                        "prix_median_m2": stats.prix_median_m2,
                        "prix_min_m2": stats.prix_min_m2,
                        "prix_max_m2": stats.prix_max_m2,
                        "nombre_transactions": stats.nombre_transactions,
                        "surface_moyenne": stats.surface_moyenne,
                        "prix_appart_m2": stats.prix_moyen_appartement_m2,
                        "prix_maison_m2": stats.prix_moyen_maison_m2,
                    }
                )
>>>>>>> b635870c043313b779e3bb0e5486256e81c809f2

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values("prix_moyen_m2", ascending=False)

        logger.info(f"✓ Analyse terminée: {len(df_results)} villes")
        return df_results

    def get_department_stats(self, dept_code: str) -> pd.DataFrame:
        """
        Obtient les statistiques pour toutes les villes d'un département.

        Args:
            dept_code: Code département (ex: "75")

        Returns:
            DataFrame avec les statistiques des villes du département
        """
        if self.df is None:
            raise ValueError("Aucune donnée chargée. Utilisez load_data() d'abord.")

        dept_df = self.df[self.df["code_departement"] == dept_code]

        if dept_df.empty:
            logger.warning(f"Aucune donnée pour le département {dept_code}")
            return pd.DataFrame()

        results = []
        for city_name in dept_df["nom_commune"].unique():
            stats = self.get_city_stats(city_name)
            if stats:
                results.append(
                    {
                        "ville": city_name,
                        "prix_moyen_m2": stats.prix_moyen_m2,
                        "prix_median_m2": stats.prix_median_m2,
                        "transactions": stats.nombre_transactions,
                    }
                )

        df_results = pd.DataFrame(results).sort_values("prix_moyen_m2", ascending=False)
        return df_results

    def export_analysis(
        self, df_results: pd.DataFrame, filename: str = "analyse_idf.xlsx"
    ) -> None:
        """
        Exporte les résultats d'analyse.

        Args:
            df_results: DataFrame avec les résultats
            filename: Nom du fichier de sortie
        """
        output_path = REPORTS_DIR / filename
        df_results.to_excel(output_path, index=False, engine="openpyxl")
        logger.info(f"✓ Résultats exportés: {output_path}")


if __name__ == "__main__":
    # Exemple d'utilisation
    analyzer = PriceAnalyzer()
    analyzer.load_data(year=2023)

    # Analyser Paris
    paris_stats = analyzer.get_city_stats("Paris")
    if paris_stats:
        print(f"Paris - Prix moyen: {paris_stats.prix_moyen_m2:.0f}€/m²")
        print(f"  Transactions: {paris_stats.nombre_transactions}")

    # Analyser toutes les villes
    all_stats = analyzer.analyze_all_cities()
    print(f"\nTop 10 villes les plus chères:")
    print(all_stats.head(10)[["ville", "prix_moyen_m2", "nombre_transactions"]])

    # Exporter
    analyzer.export_analysis(all_stats)
