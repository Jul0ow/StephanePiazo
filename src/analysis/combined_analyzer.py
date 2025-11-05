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
        
        # Initialiser les analyseurs
        self.price_analyzer = PriceAnalyzer()
        self.rent_analyzer = RentAnalyzer(year=rent_year)
        
        # Charger les données DVF
        try:
            self.price_analyzer.load_data(year=dvf_year)
            logger.info(f"✓ Données DVF {dvf_year} chargées")
        except FileNotFoundError as e:
            logger.warning(f"⚠ Données DVF {dvf_year} non trouvées: {e}")
            logger.warning("L'analyse des prix d'achat ne sera pas disponible")

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
        
        # Récupérer les statistiques DVF si disponibles
        price_stats = None
        if search_name and self.price_analyzer.df is not None:
            try:
                price_stats = self.price_analyzer.get_city_stats(search_name)
            except Exception as e:
                logger.debug(f"Pas de données DVF pour {search_name}: {e}")

        result = {
            "commune": search_name,
            "code_insee": insee_code,
            "loyers": rent_stats.__dict__ if rent_stats else None,
            "prix_vente": price_stats.__dict__ if price_stats else None,
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

        # Utiliser le prix fourni ou calculer depuis les données DVF
        if prix_achat_m2 is None and self.price_analyzer.df is not None:
            # Récupérer le nom de la ville si besoin
            search_name = city_name
            if not search_name and insee_code:
                data = self.rent_analyzer.load_idf_data()
                city_row = data[data["INSEE_C"] == insee_code]
                if not city_row.empty:
                    search_name = city_row.iloc[0]["LIBGEO"]
            
            # Essayer de récupérer les stats DVF
            if search_name:
                try:
                    price_stats = self.price_analyzer.get_city_stats(search_name)
                    if price_stats:
                        prix_achat_m2 = price_stats.prix_moyen_m2
                except Exception as e:
                    logger.debug(f"Pas de données DVF pour {search_name}: {e}")

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

    def get_all_cities_combined_stats(self, department_code: Optional[str] = None) -> pd.DataFrame:
        """
        Récupère les statistiques combinées (prix + loyers + rendement) pour toutes les villes.
        
        Cette méthode charge les données de loyers et tente de récupérer les prix DVF
        pour chaque ville afin de calculer le rendement locatif.

        Args:
            department_code: Filtrer par département (optionnel)

        Returns:
            DataFrame avec toutes les statistiques combinées
        """
        logger.info("Récupération des statistiques combinées pour toutes les villes...")
        
        # Charger les données de loyers
        rent_data = self.rent_analyzer.load_idf_data()
        
        if department_code:
            rent_data = rent_data[rent_data["DEP"] == department_code].copy()

        results = []
        total = len(rent_data)
        
        for idx, row in rent_data.iterrows():
            if idx % 100 == 0:
                logger.debug(f"Progression: {idx}/{total} villes")
            
            city_name = row["LIBGEO"]
            insee_code = row["INSEE_C"]
            
            # Stats de base depuis les loyers
            city_data = {
                "commune": city_name,
                "code_insee": insee_code,
                "departement": row["DEP"],
                "loyer_moyen_m2": row["loypredm2"] if pd.notna(row["loypredm2"]) else None,
                "loyer_bas_m2": row["lwr_IPm2"] if pd.notna(row["lwr_IPm2"]) else None,
                "loyer_haut_m2": row["upr_IPm2"] if pd.notna(row["upr_IPm2"]) else None,
                "nb_obs_loyers": int(row["nbobs_com"]) if pd.notna(row["nbobs_com"]) else None,
                "r2_loyers": float(row["R2_adj"]) if pd.notna(row["R2_adj"]) else None,
            }
            
            # Ajouter colonne type_bien si disponible
            if "type_bien" in row.index and pd.notna(row["type_bien"]):
                city_data["type_bien"] = row["type_bien"]
            
            # Essayer de récupérer les prix DVF
            if self.price_analyzer.df is not None:
                try:
                    price_stats = self.price_analyzer.get_city_stats(city_name)
                    if price_stats:
                        city_data["prix_moyen_m2"] = price_stats.prix_moyen_m2
                        city_data["prix_min_m2"] = price_stats.prix_min_m2
                        city_data["prix_max_m2"] = price_stats.prix_max_m2
                        city_data["nb_transactions"] = price_stats.nombre_transactions
                        
                        # Calculer le rendement locatif si les données sont disponibles
                        if city_data["loyer_moyen_m2"] and price_stats.prix_moyen_m2 > 0:
                            loyer_annuel = city_data["loyer_moyen_m2"] * 12
                            city_data["rendement_brut_pct"] = (loyer_annuel / price_stats.prix_moyen_m2) * 100
                            
                            # Calculer aussi avec loyers bas/haut
                            if city_data["loyer_bas_m2"]:
                                city_data["rendement_bas_pct"] = (city_data["loyer_bas_m2"] * 12 / price_stats.prix_moyen_m2) * 100
                            if city_data["loyer_haut_m2"]:
                                city_data["rendement_haut_pct"] = (city_data["loyer_haut_m2"] * 12 / price_stats.prix_moyen_m2) * 100
                        else:
                            city_data["rendement_brut_pct"] = None
                            city_data["rendement_bas_pct"] = None
                            city_data["rendement_haut_pct"] = None
                    else:
                        # Pas de données DVF pour cette ville
                        city_data["prix_moyen_m2"] = None
                        city_data["prix_min_m2"] = None
                        city_data["prix_max_m2"] = None
                        city_data["nb_transactions"] = None
                        city_data["rendement_brut_pct"] = None
                        city_data["rendement_bas_pct"] = None
                        city_data["rendement_haut_pct"] = None
                except Exception as e:
                    logger.debug(f"Pas de données DVF pour {city_name}: {e}")
                    city_data["prix_moyen_m2"] = None
                    city_data["prix_min_m2"] = None
                    city_data["prix_max_m2"] = None
                    city_data["nb_transactions"] = None
                    city_data["rendement_brut_pct"] = None
                    city_data["rendement_bas_pct"] = None
                    city_data["rendement_haut_pct"] = None
            else:
                # Pas de données DVF chargées
                city_data["prix_moyen_m2"] = None
                city_data["prix_min_m2"] = None
                city_data["prix_max_m2"] = None
                city_data["nb_transactions"] = None
                city_data["rendement_brut_pct"] = None
                city_data["rendement_bas_pct"] = None
                city_data["rendement_haut_pct"] = None
            
            results.append(city_data)
        
        if not results:
            logger.warning("Aucune donnée combinée disponible")
            return pd.DataFrame()

        df = pd.DataFrame(results)
        logger.info(f"✓ Statistiques combinées pour {len(df)} villes")
        
        # Compter combien ont un rendement calculé
        with_yield = df["rendement_brut_pct"].notna().sum()
        logger.info(f"  • {with_yield} villes avec rendement calculé")
        
        return df
    
    def get_best_rental_yield_cities(
        self,
        n: int = 20,
        department_code: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Trouve les villes avec les meilleurs rendements locatifs.
        
        Utilise get_all_cities_combined_stats() pour obtenir les données,
        puis filtre et trie par rendement.

        Args:
            n: Nombre de villes à retourner
            department_code: Filtrer par département

        Returns:
            DataFrame des villes triées par rendement décroissant
        """
        # Récupérer toutes les stats combinées
        df = self.get_all_cities_combined_stats(department_code=department_code)
        
        if df.empty:
            logger.warning("Aucune donnée combinée disponible")
            return pd.DataFrame()
        
        # Filtrer les villes avec rendement calculé
        df_with_yield = df[df["rendement_brut_pct"].notna()].copy()
        
        if df_with_yield.empty:
            logger.warning("Aucune ville avec rendement calculable")
            return pd.DataFrame()
        
        # Trier et retourner le top N
        result = df_with_yield.sort_values("rendement_brut_pct", ascending=False).head(n)
        logger.info(f"✓ Top {n} rendements: {result['rendement_brut_pct'].min():.2f}% - {result['rendement_brut_pct'].max():.2f}%")
        
        return result

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
        Exporte toutes les données combinées vers Excel avec plusieurs feuilles.
        
        Feuilles créées:
        1. Données combinées complètes (prix + loyers + rendement)
        2. Top 30 rendements
        3. Stats par département
        4. Top 30 loyers

        Args:
            output_file: Chemin du fichier de sortie
            department_code: Filtrer par département (optionnel)
        """
        if output_file is None:
            dept_suffix = f"_{department_code}" if department_code else ""
            output_file = OUTPUTS_DIR / "reports" / f"analyse_complete_dvf{self.dvf_year}_loyers{self.rent_year}{dept_suffix}.xlsx"

        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Export des données combinées vers {output_file}...")

        # Récupérer les données combinées
        combined_data = self.get_all_cities_combined_stats(department_code=department_code)
        
        if combined_data.empty:
            logger.warning("⚠ Aucune donnée à exporter")
            return

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # Feuille 1: Données combinées complètes
            export_cols = [
                "commune", "code_insee", "departement",
                "prix_moyen_m2", "prix_min_m2", "prix_max_m2", "nb_transactions",
                "loyer_moyen_m2", "loyer_bas_m2", "loyer_haut_m2", "nb_obs_loyers",
                "rendement_brut_pct", "rendement_bas_pct", "rendement_haut_pct",
                "r2_loyers"
            ]
            
            # Ajouter type_bien si disponible
            if "type_bien" in combined_data.columns:
                export_cols.insert(3, "type_bien")
            
            # Filtrer les colonnes existantes
            export_cols = [col for col in export_cols if col in combined_data.columns]
            
            export_data = combined_data[export_cols].copy()
            
            # Renommer pour l'export
            column_mapping = {
                "commune": "Commune",
                "code_insee": "Code INSEE",
                "departement": "Département",
                "type_bien": "Type de bien",
                "prix_moyen_m2": "Prix vente moyen (€/m²)",
                "prix_min_m2": "Prix vente min (€/m²)",
                "prix_max_m2": "Prix vente max (€/m²)",
                "nb_transactions": "Nb transactions DVF",
                "loyer_moyen_m2": "Loyer moyen (€/m²/mois)",
                "loyer_bas_m2": "Loyer bas (€/m²/mois)",
                "loyer_haut_m2": "Loyer haut (€/m²/mois)",
                "nb_obs_loyers": "Nb obs. loyers",
                "rendement_brut_pct": "Rendement brut (%)",
                "rendement_bas_pct": "Rendement bas (%)",
                "rendement_haut_pct": "Rendement haut (%)",
                "r2_loyers": "R² ajusté loyers",
            }
            
            export_data.rename(columns=column_mapping, inplace=True)
            export_data.to_excel(writer, sheet_name="Données combinées", index=False)
            logger.info(f"  ✓ Feuille 'Données combinées': {len(export_data)} villes")

            # Feuille 2: Top 30 rendements
            if "rendement_brut_pct" in combined_data.columns:
                top_yield = combined_data[combined_data["rendement_brut_pct"].notna()].copy()
                if not top_yield.empty:
                    top_yield = top_yield.sort_values("rendement_brut_pct", ascending=False).head(30)
                    top_yield_export = top_yield[export_cols].copy()
                    top_yield_export.rename(columns=column_mapping, inplace=True)
                    top_yield_export.to_excel(writer, sheet_name="Top 30 rendements", index=False)
                    logger.info(f"  ✓ Feuille 'Top 30 rendements': {len(top_yield_export)} villes")

            # Feuille 3: Statistiques par département (loyers)
            if not department_code:
                try:
                    dept_stats = self.rent_analyzer.get_idf_statistics()
                    if not dept_stats.empty:
                        dept_stats["loyer_annuel_moyen"] = dept_stats["loyer_moyen"] * 12
                        dept_stats.to_excel(writer, sheet_name="Stats départements", index=False)
                        logger.info(f"  ✓ Feuille 'Stats départements': {len(dept_stats)} départements")
                except Exception as e:
                    logger.warning(f"Impossible de générer les stats par département: {e}")
            
            # Feuille 4: Top 30 loyers uniquement
            try:
                top_rent = self.rent_analyzer.get_top_cities(n=30, department_code=department_code)
                if not top_rent.empty:
                    top_rent.to_excel(writer, sheet_name="Top 30 loyers", index=False)
                    logger.info(f"  ✓ Feuille 'Top 30 loyers': {len(top_rent)} villes")
            except Exception as e:
                logger.warning(f"Impossible de générer le top loyers: {e}")

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
