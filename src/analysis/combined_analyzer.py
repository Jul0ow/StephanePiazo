"""Analyseur combiné pour les prix d'achat (DVF) et les loyers (Carte des loyers)."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.rent_analyzer import RentAnalyzer
from src.models.city import City, CityStats, RentStats
from src.utils.config import IDF_DEPARTMENTS, OUTPUTS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CombinedAnalyzer:
    """Analyseur combiné pour les données d'achat et de location."""

    def __init__(self, dvf_year: int = 2023, rent_year: int = 2024):
        """
        Initialise l'analyseur combiné.

        Args:
            dvf_year: Année des données DVF à analyser
            rent_year: Année des données de loyers à analyser
        """
        self.dvf_year = dvf_year
        self.rent_year = rent_year
        self.price_analyzer = PriceAnalyzer(year=dvf_year)
        self.rent_analyzer = RentAnalyzer(year=rent_year)

    def get_city_complete_stats(
        self, 
        city_name: Optional[str] = None,
        insee_code: Optional[str] = None
    ) -> Optional[dict]:
        """
        Récupère toutes les statistiques (achat + loyers) pour une ville.

        Args:
            city_name: Nom de la commune
            insee_code: Code INSEE de la commune

        Returns:
            Dictionnaire avec toutes les statistiques
        """
        # Récupérer les statistiques de loyers
        rent_stats = self.rent_analyzer.get_city_rent_stats(
            city_name=city_name, 
            insee_code=insee_code
        )

        # Pour les statistiques DVF, on a besoin du nom de la ville
        # (à adapter selon votre implémentation de PriceAnalyzer)
        if city_name:
            search_name = city_name
        elif insee_code and rent_stats:
            # Récupérer le nom depuis les données de loyers
            data = self.rent_analyzer.load_idf_data()
            city_row = data[data["INSEE_C"] == insee_code]
            if not city_row.empty:
                search_name = city_row.iloc[0]["LIBGEO"]
            else:
                search_name = None
        else:
            search_name = None

        result = {
            "commune": search_name,
            "code_insee": insee_code,
            "loyers": rent_stats.__dict__ if rent_stats else None,
        }

        return result

    def calculate_rental_yield(
        self,
        city_name: Optional[str] = None,
        insee_code: Optional[str] = None,
        prix_achat_m2: Optional[float] = None
    ) -> Optional[dict]:
        """
        Calcule le rendement locatif brut pour une ville.

        Rendement locatif brut (%) = (Loyer annuel / Prix d'achat) × 100

        Args:
            city_name: Nom de la commune
            insee_code: Code INSEE de la commune
            prix_achat_m2: Prix d'achat au m² (optionnel, sinon calculé depuis DVF)

        Returns:
            Dictionnaire avec le rendement et les détails
        """
        # Récupérer les loyers
        rent_stats = self.rent_analyzer.get_city_rent_stats(
            city_name=city_name,
            insee_code=insee_code
        )

        if not rent_stats or not rent_stats.loyer_moyen_m2:
            logger.warning(f"Pas de données de loyers pour {city_name or insee_code}")
            return None

        # Utiliser le prix fourni ou calculer depuis les données
        if prix_achat_m2 is None:
            # Pour le moment, retourner None si pas de prix fourni
            # À adapter selon votre implémentation de PriceAnalyzer
            logger.warning("Prix d'achat non fourni et pas encore d'intégration avec PriceAnalyzer")
            prix_achat_m2 = None

        if prix_achat_m2 is None:
            return {
                "commune": city_name,
                "loyer_mensuel_m2": rent_stats.loyer_moyen_m2,
                "loyer_annuel_m2": rent_stats.loyer_moyen_m2 * 12,
                "prix_achat_m2": None,
                "rendement_brut_pct": None,
                "message": "Prix d'achat non disponible"
            }

        # Calculer le rendement
        loyer_annuel_m2 = rent_stats.loyer_moyen_m2 * 12
        rendement_brut = (loyer_annuel_m2 / prix_achat_m2) * 100

        # Calculer aussi avec les bornes basses et hautes
        rendement_bas = None
        rendement_haut = None
        
        if rent_stats.loyer_bas_m2:
            loyer_annuel_bas = rent_stats.loyer_bas_m2 * 12
            rendement_bas = (loyer_annuel_bas / prix_achat_m2) * 100
            
        if rent_stats.loyer_haut_m2:
            loyer_annuel_haut = rent_stats.loyer_haut_m2 * 12
            rendement_haut = (loyer_annuel_haut / prix_achat_m2) * 100

        return {
            "commune": city_name,
            "loyer_mensuel_m2": rent_stats.loyer_moyen_m2,
            "loyer_annuel_m2": loyer_annuel_m2,
            "prix_achat_m2": prix_achat_m2,
            "rendement_brut_pct": rendement_brut,
            "rendement_bas_pct": rendement_bas,
            "rendement_haut_pct": rendement_haut,
            "fiable": rent_stats.is_reliable,
        }

    def get_best_rental_yield_cities(
        self,
        n: int = 20,
        department_code: Optional[str] = None,
        prix_achat_dict: Optional[dict] = None
    ) -> pd.DataFrame:
        """
        Trouve les villes avec les meilleurs rendements locatifs.

        Args:
            n: Nombre de villes à retourner
            department_code: Filtrer par département
            prix_achat_dict: Dictionnaire {insee_code: prix_m2} pour les prix d'achat

        Returns:
            DataFrame des villes triées par rendement
        """
        if prix_achat_dict is None:
            logger.warning("Pas de données de prix d'achat fournies")
            return pd.DataFrame()

        rent_data = self.rent_analyzer.load_idf_data()
        
        if department_code:
            rent_data = rent_data[rent_data["DEP"] == department_code].copy()

        results = []
        
        for _, row in rent_data.iterrows():
            insee_code = row["INSEE_C"]
            
            if insee_code in prix_achat_dict:
                prix_achat = prix_achat_dict[insee_code]
                loyer_mensuel = row["loypredm2"]
                
                if pd.notna(loyer_mensuel) and prix_achat > 0:
                    rendement = (loyer_mensuel * 12 / prix_achat) * 100
                    
                    results.append({
                        "commune": row["LIBGEO"],
                        "code_insee": insee_code,
                        "departement": row["DEP"],
                        "loyer_mensuel_m2": loyer_mensuel,
                        "prix_achat_m2": prix_achat,
                        "rendement_brut_pct": rendement,
                        "nb_observations": row["nbobs_com"] if pd.notna(row["nbobs_com"]) else 0,
                    })

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)
        return df.sort_values("rendement_brut_pct", ascending=False).head(n)

    def create_comparison_report(
        self,
        city_names: list[str],
        output_file: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Crée un rapport de comparaison pour plusieurs villes.

        Args:
            city_names: Liste des noms de communes
            output_file: Chemin du fichier de sortie (optionnel)

        Returns:
            DataFrame de comparaison
        """
        comparisons = []

        for city_name in city_names:
            # Récupérer les loyers
            rent_stats = self.rent_analyzer.get_city_rent_stats(city_name=city_name)
            
            if rent_stats:
                comparisons.append({
                    "commune": city_name,
                    "loyer_moyen_m2": rent_stats.loyer_moyen_m2,
                    "loyer_bas_m2": rent_stats.loyer_bas_m2,
                    "loyer_haut_m2": rent_stats.loyer_haut_m2,
                    "loyer_annuel_m2": rent_stats.loyer_moyen_m2 * 12 if rent_stats.loyer_moyen_m2 else None,
                    "type_prediction": rent_stats.type_prediction,
                    "fiable": rent_stats.is_reliable,
                    "nb_observations": rent_stats.nb_observations_commune,
                    "r2": rent_stats.r2_ajuste,
                })

        if not comparisons:
            logger.warning("Aucune donnée trouvée pour les villes spécifiées")
            return pd.DataFrame()

        df = pd.DataFrame(comparisons)
        df = df.sort_values("loyer_moyen_m2", ascending=False)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(output_file, index=False)
            logger.info(f"✓ Rapport exporté vers: {output_file}")

        return df

    def export_combined_data(
        self,
        output_file: Optional[Path] = None,
        department_code: Optional[str] = None
    ) -> None:
        """
        Exporte toutes les données combinées vers Excel.

        Args:
            output_file: Chemin du fichier de sortie
            department_code: Filtrer par département (optionnel)
        """
        if output_file is None:
            output_file = OUTPUTS_DIR / "reports" / f"analyse_complete_idf_{self.rent_year}.xlsx"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Charger les données de loyers
        rent_data = self.rent_analyzer.load_idf_data()
        
        if department_code:
            rent_data = rent_data[rent_data["DEP"] == department_code].copy()

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # Feuille 1: Données de loyers
            rent_export = rent_data[[
                "LIBGEO", "INSEE_C", "DEP", "EPCI",
                "loypredm2", "lwr_IPm2", "upr_IPm2",
                "TYPPRED", "nbobs_com", "nbobs_mail", "R2_adj"
            ]].copy()
            
            rent_export.columns = [
                "Commune", "Code INSEE", "Département", "EPCI",
                "Loyer moyen (€/m²/mois)", "Loyer bas (€/m²/mois)", "Loyer haut (€/m²/mois)",
                "Type prédiction", "Nb obs. commune", "Nb obs. maille", "R² ajusté"
            ]
            
            # Ajouter le loyer annuel
            rent_export["Loyer annuel (€/m²)"] = rent_export["Loyer moyen (€/m²/mois)"] * 12
            
            rent_export.to_excel(writer, sheet_name="Loyers", index=False)

            # Feuille 2: Statistiques par département
            if not department_code:
                dept_stats = self.rent_analyzer.get_idf_statistics()
                dept_stats["loyer_annuel_moyen"] = dept_stats["loyer_moyen"] * 12
                dept_stats.to_excel(writer, sheet_name="Stats par département", index=False)

            # Feuille 3: Top loyers
            top_rent = self.rent_analyzer.get_top_cities(n=30, department_code=department_code)
            top_rent.to_excel(writer, sheet_name="Top 30 loyers", index=False)

        logger.info(f"✓ Données combinées exportées vers: {output_file}")


if __name__ == "__main__":
    # Exemple d'utilisation
    analyzer = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

    # Comparer plusieurs villes
    cities = ["Paris", "Versailles", "Saint-Denis", "Créteil", "Nanterre", "Montreuil"]
    comparison = analyzer.create_comparison_report(cities)
    print("\n=== Comparaison des loyers ===")
    print(comparison)

    # Calculer le rendement locatif (exemple avec prix fictifs)
    prix_paris = 10000  # 10000€/m²
    rendement = analyzer.calculate_rental_yield(city_name="Paris", prix_achat_m2=prix_paris)
    if rendement:
        print(f"\n=== Rendement locatif Paris ===")
        print(f"Prix d'achat: {rendement['prix_achat_m2']}€/m²")
        print(f"Loyer mensuel: {rendement['loyer_mensuel_m2']:.2f}€/m²")
        print(f"Loyer annuel: {rendement['loyer_annuel_m2']:.2f}€/m²")
        print(f"Rendement brut: {rendement['rendement_brut_pct']:.2f}%")

    # Exporter toutes les données
    analyzer.export_combined_data()
