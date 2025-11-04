"""Analyse des données de loyers de la Carte des loyers."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.data.rent_downloader import RentDownloader
from src.models.city import RentStats
from src.utils.config import IDF_DEPARTMENTS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RentAnalyzer:
    """Analyseur de données de loyers pour les communes."""

    def __init__(self, year: int = 2024, data_dir: Optional[Path] = None):
        """
        Initialise l'analyseur de loyers.

        Args:
            year: Année des données à analyser
            data_dir: Répertoire contenant les données (par défaut: RAW_DATA_DIR)
        """
        self.year = year
        self.data_dir = data_dir or RAW_DATA_DIR
        self.downloader = RentDownloader(data_dir=self.data_dir)
        self.data: Optional[pd.DataFrame] = None
        self.data_idf: Optional[pd.DataFrame] = None

    def load_data(self) -> pd.DataFrame:
        """
        Charge les données de loyers.

        Returns:
            DataFrame des données de loyers
        """
        if self.data is None:
            try:
                self.data = self.downloader.load_rent_data(year=self.year)
                logger.info(f"✓ Données de loyers {self.year} chargées: {len(self.data)} communes")
            except FileNotFoundError:
                logger.error(
                    f"Données de loyers {self.year} non trouvées. "
                    "Téléchargez-les d'abord avec RentDownloader.download_rent_data()"
                )
                raise

        return self.data

    def load_idf_data(self) -> pd.DataFrame:
        """
        Charge et filtre les données pour l'Île-de-France.

        Returns:
            DataFrame des données IDF
        """
        if self.data_idf is None:
            data = self.load_data()
            self.data_idf = self.downloader.filter_idf_data(data)

        return self.data_idf

    def get_city_rent_stats(
        self, 
        city_name: Optional[str] = None, 
        insee_code: Optional[str] = None
    ) -> Optional[RentStats]:
        """
        Récupère les statistiques de loyers pour une ville.

        Args:
            city_name: Nom de la commune (optionnel si insee_code fourni)
            insee_code: Code INSEE de la commune (optionnel si city_name fourni)

        Returns:
            RentStats ou None si la commune n'est pas trouvée
        """
        data = self.load_idf_data()

        # Filtrer selon le critère fourni
        if insee_code:
            mask = data["INSEE_C"] == insee_code
        elif city_name:
            mask = data["LIBGEO"].str.upper() == city_name.upper()
        else:
            raise ValueError("Vous devez fournir city_name ou insee_code")

        filtered = data[mask]

        if filtered.empty:
            logger.warning(
                f"Aucune donnée de loyer trouvée pour "
                f"{'INSEE ' + insee_code if insee_code else city_name}"
            )
            return None

        # Prendre la première ligne (devrait être unique par commune)
        row = filtered.iloc[0]

        # Créer l'objet RentStats
        return RentStats(
            loyer_moyen_m2=float(row["loypredm2"]) if pd.notna(row["loypredm2"]) else None,
            loyer_bas_m2=float(row["lwr_IPm2"]) if pd.notna(row["lwr_IPm2"]) else None,
            loyer_haut_m2=float(row["upr_IPm2"]) if pd.notna(row["upr_IPm2"]) else None,
            type_prediction=row["TYPPRED"] if pd.notna(row["TYPPRED"]) else None,
            nb_observations_commune=int(row["nbobs_com"]) if pd.notna(row["nbobs_com"]) else None,
            nb_observations_maille=int(row["nbobs_mail"]) if pd.notna(row["nbobs_mail"]) else None,
            r2_ajuste=float(row["R2_adj"]) if pd.notna(row["R2_adj"]) else None,
            id_maille=row["id_zone"] if pd.notna(row["id_zone"]) else None,
        )

    def get_department_statistics(self, department_code: str) -> pd.DataFrame:
        """
        Calcule les statistiques de loyers pour un département.

        Args:
            department_code: Code du département (ex: "75" pour Paris)

        Returns:
            DataFrame avec les statistiques agrégées
        """
        data = self.load_idf_data()
        dept_data = data[data["DEP"] == department_code].copy()

        if dept_data.empty:
            logger.warning(f"Aucune donnée pour le département {department_code}")
            return pd.DataFrame()

        stats = {
            "nb_communes": len(dept_data),
            "loyer_moyen": dept_data["loypredm2"].mean(),
            "loyer_median": dept_data["loypredm2"].median(),
            "loyer_min": dept_data["loypredm2"].min(),
            "loyer_max": dept_data["loypredm2"].max(),
            "loyer_bas_moyen": dept_data["lwr_IPm2"].mean(),
            "loyer_haut_moyen": dept_data["upr_IPm2"].mean(),
        }

        return pd.DataFrame([stats])

    def get_idf_statistics(self) -> pd.DataFrame:
        """
        Calcule les statistiques de loyers pour toute l'Île-de-France.

        Returns:
            DataFrame avec les statistiques agrégées par département
        """
        results = []

        for dept_code, dept_name in IDF_DEPARTMENTS.items():
            dept_stats = self.get_department_statistics(dept_code)
            if not dept_stats.empty:
                dept_stats["department_code"] = dept_code
                dept_stats["department_name"] = dept_name
                results.append(dept_stats)

        if not results:
            return pd.DataFrame()

        return pd.concat(results, ignore_index=True)

    def compare_cities(self, city_names: list[str]) -> pd.DataFrame:
        """
        Compare les loyers de plusieurs villes.

        Args:
            city_names: Liste des noms de communes à comparer

        Returns:
            DataFrame avec les comparaisons
        """
        comparisons = []

        for city_name in city_names:
            rent_stats = self.get_city_rent_stats(city_name=city_name)
            if rent_stats:
                comparisons.append({
                    "commune": city_name,
                    "loyer_moyen_m2": rent_stats.loyer_moyen_m2,
                    "loyer_bas_m2": rent_stats.loyer_bas_m2,
                    "loyer_haut_m2": rent_stats.loyer_haut_m2,
                    "type_prediction": rent_stats.type_prediction,
                    "fiable": rent_stats.is_reliable,
                    "nb_observations": rent_stats.nb_observations_commune,
                })

        if not comparisons:
            return pd.DataFrame()

        df = pd.DataFrame(comparisons)
        return df.sort_values("loyer_moyen_m2", ascending=False)

    def get_top_cities(
        self, 
        n: int = 10, 
        department_code: Optional[str] = None,
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Récupère les villes avec les loyers les plus élevés/bas.

        Args:
            n: Nombre de villes à retourner
            department_code: Filtrer par département (optionnel)
            ascending: Si True, retourne les loyers les plus bas

        Returns:
            DataFrame des top villes
        """
        data = self.load_idf_data()

        if department_code:
            data = data[data["DEP"] == department_code].copy()

        # Trier par loyer moyen
        sorted_data = data.sort_values("loypredm2", ascending=ascending).head(n)

        # Sélectionner les colonnes pertinentes
        result = sorted_data[[
            "LIBGEO", "INSEE_C", "DEP", "loypredm2", 
            "lwr_IPm2", "upr_IPm2", "TYPPRED", "nbobs_com", "R2_adj"
        ]].copy()

        result.columns = [
            "commune", "code_insee", "departement", "loyer_moyen_m2",
            "loyer_bas_m2", "loyer_haut_m2", "type_prediction", 
            "nb_observations", "r2_ajuste"
        ]

        return result.reset_index(drop=True)

    def export_to_excel(
        self, 
        output_file: Path, 
        department_code: Optional[str] = None
    ) -> None:
        """
        Exporte les statistiques de loyers vers un fichier Excel.

        Args:
            output_file: Chemin du fichier de sortie
            department_code: Filtrer par département (optionnel)
        """
        data = self.load_idf_data()

        if department_code:
            data = data[data["DEP"] == department_code].copy()

        # Sélectionner et renommer les colonnes
        export_data = data[[
            "LIBGEO", "INSEE_C", "DEP", "EPCI", 
            "loypredm2", "lwr_IPm2", "upr_IPm2",
            "TYPPRED", "nbobs_com", "nbobs_mail", "R2_adj"
        ]].copy()

        export_data.columns = [
            "Commune", "Code INSEE", "Département", "EPCI",
            "Loyer moyen (€/m²)", "Loyer bas (€/m²)", "Loyer haut (€/m²)",
            "Type prédiction", "Nb obs. commune", "Nb obs. maille", "R² ajusté"
        ]

        # Créer un fichier Excel avec plusieurs feuilles
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # Feuille principale: données détaillées
            export_data.to_excel(writer, sheet_name="Données détaillées", index=False)

            # Feuille 2: statistiques par département
            if not department_code:
                dept_stats = self.get_idf_statistics()
                dept_stats.to_excel(writer, sheet_name="Stats par département", index=False)

            # Feuille 3: Top 20 loyers les plus élevés
            top_high = self.get_top_cities(n=20, department_code=department_code, ascending=False)
            top_high.to_excel(writer, sheet_name="Top 20 loyers élevés", index=False)

            # Feuille 4: Top 20 loyers les plus bas
            top_low = self.get_top_cities(n=20, department_code=department_code, ascending=True)
            top_low.to_excel(writer, sheet_name="Top 20 loyers bas", index=False)

        logger.info(f"✓ Données exportées vers: {output_file}")


if __name__ == "__main__":
    # Exemple d'utilisation
    analyzer = RentAnalyzer(year=2024)

    # Charger les données IDF
    data = analyzer.load_idf_data()
    print(f"\n{len(data)} communes avec données de loyers en IDF")

    # Statistiques pour Paris
    paris_rent = analyzer.get_city_rent_stats(city_name="Paris")
    if paris_rent:
        print(f"\nStatistiques de loyers pour Paris:")
        print(paris_rent)
        print(f"Fiable: {paris_rent.is_reliable}")

    # Statistiques par département
    print("\n=== Statistiques par département ===")
    idf_stats = analyzer.get_idf_statistics()
    print(idf_stats)

    # Top 10 loyers les plus élevés
    print("\n=== Top 10 loyers les plus élevés en IDF ===")
    top_10 = analyzer.get_top_cities(n=10, ascending=False)
    print(top_10)

    # Comparer plusieurs villes
    print("\n=== Comparaison de villes ===")
    comparison = analyzer.compare_cities([
        "Paris", "Versailles", "Saint-Denis", "Créteil", "Nanterre"
    ])
    print(comparison)
