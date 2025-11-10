"""Script principal pour analyser les données immobilières Île-de-France.

Ce script permet de:
1. Télécharger les données DVF (ventes) et de loyers
2. Nettoyer les données
3. Analyser les prix d'achat et de location au m²
4. Générer des rapports combinés

Usage:
    # Pipeline complet (ventes + loyers)
    python main.py --year 2023 --rent-year 2024 --full-pipeline
    
    # Étapes individuelles
    python main.py --year 2023 --download
    python main.py --year 2023 --clean
    python main.py --year 2023 --rent-year 2024 --analyze
    
    # Seulement les loyers
    python main.py --rent-year 2024 --download-rent
    python main.py --rent-year 2024 --analyze-rent
"""

import argparse
import logging
import sys
import traceback
from pathlib import Path

import pandas as pd

from src.analysis.combined_analyzer import CombinedAnalyzer
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.rent_analyzer import RentAnalyzer
from src.data.data_cleaner import DataCleaner
from src.data.dvf_downloader import DVFDownloader
from src.data.rent_downloader import RentDownloader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def download_data(year: int) -> bool:
    """Télécharge les données DVF."""
    logger.info(f"📥 Téléchargement des données DVF pour {year}...")
    downloader = DVFDownloader()
    files = downloader.download_idf_data(year=year)

    if not files:
        logger.error("❌ Échec du téléchargement")
        return False

    logger.info(f"✅ {len(files)} fichiers téléchargés")
    return True


def clean_data(year: int) -> bool:
    """Nettoie les données DVF."""
    logger.info(f"🧹 Nettoyage des données {year}...")

    try:
        downloader = DVFDownloader()
        df_raw = downloader.load_idf_data(year=year)

        cleaner = DataCleaner()
        df_clean = cleaner.clean_dvf_data(df_raw)
        cleaner.save_cleaned_data(df_clean, year=year)

        logger.info(f"✅ Données nettoyées: {len(df_clean):,} lignes")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.info(f"Lancez d'abord: python main.py --year {year} --download")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False


def download_rent_data(year: int) -> bool:
    """Télécharge les données de loyers."""
    logger.info(f"📥 Téléchargement des données de loyers pour {year}...")
    downloader = RentDownloader()
    file_path = downloader.download_rent_data(year=year)

    if not file_path:
        logger.error("❌ Échec du téléchargement des loyers")
        return False

    logger.info(f"✅ Données de loyers téléchargées")
    return True


def analyze_data(year: int) -> bool:
    """Analyse les données DVF (ventes) et génère les rapports."""
    logger.info(f"📊 Analyse des données de ventes {year}...")

    try:
        analyzer = PriceAnalyzer()
        analyzer.load_data(year=year)

        # Analyser toutes les villes
        all_stats = analyzer.analyze_all_cities()

        # Afficher le top 10
        logger.info(f"\n🏆 Top 10 des villes - Prix de vente les plus élevés ({year}):")
        print("\n" + "=" * 80)
        print(f"{'Ville':<30} {'Département':<12} {'Prix moyen/m²':>15} {'Transactions':>12}")
        print("=" * 80)
        for _, row in all_stats.head(10).iterrows():
            print(
                f"{row['ville']:<30} {row['code_departement']:<12} "
                f"{row['prix_moyen_m2']:>12,.0f} € {row['nombre_transactions']:>12,}"
            )
        print("=" * 80)

        # Exporter
        analyzer.export_analysis(all_stats, filename=f"analyse_ventes_idf_{year}.xlsx")
        logger.info(f"\n✅ Analyse des ventes terminée et exportée")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.info(f"Lancez d'abord: python main.py --year {year} --clean")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False


def analyze_rent_data(year: int) -> bool:
    """Analyse les données de loyers et génère les rapports."""
    logger.info(f"📊 Analyse des données de loyers {year}...")

    try:
        analyzer = RentAnalyzer(year=year)
        data = analyzer.load_idf_data()

        # Afficher le top 10 des loyers
        top_rent = analyzer.get_top_cities(n=10, ascending=False)
        logger.info(f"\n🏆 Top 10 des villes - Loyers les plus élevés ({year}):")
        print("\n" + "=" * 80)
        print(f"{'Ville':<30} {'Département':<12} {'Loyer moyen/m²':>15} {'Observations':>12}")
        print("=" * 80)
        for _, row in top_rent.iterrows():
            print(
                f"{row['commune']:<30} {row['departement']:<12} "
                f"{row['loyer_moyen_m2']:>12,.2f} € {row['nb_observations']:>12,}"
            )
        print("=" * 80)

        # Exporter
        from src.utils.config import REPORTS_DIR
        output_file = REPORTS_DIR / f"analyse_loyers_idf_{year}.xlsx"
        analyzer.export_to_excel(output_file)
        logger.info(f"\n✅ Analyse des loyers terminée et exportée")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.info(f"Lancez d'abord: python main.py --rent-year {year} --download-rent")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse des loyers: {e}")
        return False

# Pour l'instant cette fonction permet d'afficher les statistiques des ventes par villes et par nombre de pièces
def analyze_combined2(dvf_year: int, rent_year: int) -> bool:
    """Analyse combinée des données de ventes et de loyers."""
    logger.info(f"📊 Analyse combinée: Ventes {dvf_year} + Loyers {rent_year}...")
    try:
        # Créer l'analyseur combiné
        combined = CombinedAnalyzer(dvf_year=dvf_year, rent_year=rent_year)

        # Charger les données DVF
        combined.price_analyzer.load_data(year=dvf_year)

        dvf_stats = combined.price_analyzer.analyze_all_cities()
        combined.price_analyzer.export_analysis(dvf_stats, filename=f"analyse_ventes_idf_{dvf_year}_detailed.xlsx")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse combinée: {e}")
        traceback.print_exc()
        return False
    return True

def analyze_combined(dvf_year: int, rent_year: int) -> bool:
    """Analyse combinée des données de ventes et de loyers."""
    logger.info(f"📊 Analyse combinée: Ventes {dvf_year} + Loyers {rent_year}...")

    try:
        # Créer l'analyseur combiné
        combined = CombinedAnalyzer(dvf_year=dvf_year, rent_year=rent_year)

        # Charger les données DVF
        combined.price_analyzer.load_data(year=dvf_year)
        
        # Charger les données de loyers
        rent_data = combined.rent_analyzer.load_idf_data()

        # Analyser toutes les villes pour les ventes
        dvf_stats = combined.price_analyzer.analyze_all_cities()

        # Créer un dictionnaire de prix par code INSEE
        # On doit d'abord récupérer les codes INSEE depuis les données brutes
        dvf_raw = combined.price_analyzer.df
        if dvf_raw is None:
            logger.error("Impossible de charger les données DVF")
            return False

        # Créer mapping ville -> prix
        city_prices = {}
        for city_name in dvf_raw["nom_commune"].unique():
            city_df = dvf_raw[dvf_raw["nom_commune"] == city_name]
            if not city_df.empty:
                city_prices[city_name] = city_df["prix_m2"].mean()

        # Créer le résumé combiné
        logger.info("\n🏘️  Création du résumé combiné par ville...")
        combined_results = []

        for _, rent_row in rent_data.iterrows():
            city_name = rent_row["LIBGEO"]
            insee_code = rent_row["INSEE_C"]
            dept_code = rent_row["DEP"]

            # Récupérer les stats de vente depuis DVF
            dvf_city_stats = dvf_stats[dvf_stats["ville"].str.upper() == city_name.upper()]

            result = {
                "ville": city_name,
                "code_insee": insee_code,
                "departement": dept_code,
                # Loyers
                "loyer_moyen_m2": rent_row["loypredm2"] if pd.notna(rent_row["loypredm2"]) else None,
                "loyer_bas_m2": rent_row["lwr_IPm2"] if pd.notna(rent_row["lwr_IPm2"]) else None,
                "loyer_haut_m2": rent_row["upr_IPm2"] if pd.notna(rent_row["upr_IPm2"]) else None,
                "loyer_fiable": rent_row["TYPPRED"] == "commune" if pd.notna(rent_row["TYPPRED"]) else False,
                "type_bien": rent_row["type_bien"] if pd.notna(rent_row["type_bien"]) else "inconnu",
            }

            # Ajouter les données de vente si disponibles
            if not dvf_city_stats.empty:
                row = dvf_city_stats.iloc[0]
                result.update({
                    "prix_vente_moyen_m2": float(row["appart_prix_moyen_m2"]) if rent_row["type_bien"] == "appartements" else float(row["prix_moyen_m2"]),
                    "prix_vente_bas_m2": float(row["appart_prix_min_m2"]) if rent_row["type_bien"] == "appartements" else float(row["prix_min_m2"]),
                    "prix_vente_haut_m2":  float(row["appart_prix_max_m2"]) if rent_row["type_bien"] == "appartements" else float(row["prix_max_m2"]),
                    "surface_moyenne":  float(row["appart_surface_moyenne"]) if rent_row["type_bien"] == "appartements" else float(row["maison_surface_moyenne"]),
                    "nb_transactions": int(row["nombre_transactions"]) if pd.notna(row["nombre_transactions"]) else 0,
                })

                # Calculer le rendement locatif brut
                if result["loyer_moyen_m2"] is not None and result["prix_vente_moyen_m2"] is not None:
                    loyer_annuel = float(result["loyer_moyen_m2"]) * 12
                    result["rendement_brut_pct"] = (loyer_annuel / float(result["prix_vente_moyen_m2"])) * 100
                else:
                    result["rendement_brut_pct"] = None
            else:
                result.update({
                    "prix_vente_moyen_m2": None,
                    "prix_vente_bas_m2": None,
                    "prix_vente_haut_m2": None,
                    "nb_transactions": 0,
                    "rendement_brut_pct": None,
                })

            combined_results.append(result)

        # Créer le DataFrame résultat
        df_combined = pd.DataFrame(combined_results)

        # Afficher un résumé des villes avec données complètes
        complete_data = df_combined[
            df_combined["prix_vente_moyen_m2"].notna() & 
            df_combined["loyer_moyen_m2"].notna()
        ].copy()

        if not complete_data.empty:
            logger.info(f"\n✅ {len(complete_data)} villes avec données complètes (vente + location)")
            
            # Top 10 par rendement locatif
            complete_data_sorted = complete_data[
                complete_data["rendement_brut_pct"].notna()
            ].sort_values("rendement_brut_pct", ascending=False)

            if not complete_data_sorted.empty:
                logger.info(f"\n🏆 Top 10 des meilleurs rendements locatifs bruts:")
                print("\n" + "=" * 100)
                print(f"{'Ville':<25} {'Dept':<6} {'Prix vente/m²':>14} {'Loyer/m²':>12} {'Rendement':>12}")
                print("=" * 100)
                for _, row in complete_data_sorted.head(10).iterrows():
                    print(
                        f"{row['ville']:<25} {row['departement']:<6} "
                        f"{row['prix_vente_moyen_m2']:>11,.0f} € "
                        f"{row['loyer_moyen_m2']:>9,.2f} € "
                        f"{row['rendement_brut_pct']:>10,.2f} %"
                    )
                print("=" * 100)

            # Exemple de résumé pour quelques villes
            example_cities = ["Paris", "Versailles", "Saint-Denis", "Créteil"]
            logger.info(f"\n📋 Résumé détaillé pour quelques villes:")
            print("\n" + "=" * 120)
            
            for city in example_cities:
                city_data = complete_data[complete_data["ville"].str.upper() == city.upper()]
                if not city_data.empty:
                    row = city_data.iloc[0]
                    print(f"\n🏙️  {row['ville']} ({row['departement']})")
                    print(f"   VENTE:    Bas: {row['prix_vente_bas_m2']:>8,.0f}€/m²  |  Moyen: {row['prix_vente_moyen_m2']:>8,.0f}€/m²  |  Haut: {row['prix_vente_haut_m2']:>8,.0f}€/m²")
                    if pd.notna(row['loyer_bas_m2']) and pd.notna(row['loyer_haut_m2']):
                        print(f"   LOCATION: Bas: {row['loyer_bas_m2']:>8,.2f}€/m²  |  Moyen: {row['loyer_moyen_m2']:>8,.2f}€/m²  |  Haut: {row['loyer_haut_m2']:>8,.2f}€/m²")
                    else:
                        print(f"   LOCATION: Moyen: {row['loyer_moyen_m2']:>8,.2f}€/m²")
                    if pd.notna(row['rendement_brut_pct']):
                        print(f"   RENDEMENT BRUT: {row['rendement_brut_pct']:.2f}%")
            print("\n" + "=" * 120)

        # Exporter le résultat combiné
        from src.utils.config import REPORTS_DIR
        output_file = REPORTS_DIR / f"analyse_complete_idf_{dvf_year}_{rent_year}.xlsx"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # Feuille 1: Toutes les villes avec données complètes
            if not complete_data.empty:
                complete_data.sort_values("rendement_brut_pct", ascending=False).to_excel(
                    writer, sheet_name="Résumé complet", index=False
                )

            # Feuille 2: Toutes les données (même partielles)
            df_combined.to_excel(writer, sheet_name="Toutes les données", index=False)

            # Feuille 3: Statistiques par département
            dept_stats_list = []
            for dept_code in df_combined["departement"].unique():
                dept_data = complete_data[complete_data["departement"] == dept_code]
                if not dept_data.empty:
                    dept_stats_list.append({
                        "departement": dept_code,
                        "nb_villes": len(dept_data),
                        "prix_vente_moyen": dept_data["prix_vente_moyen_m2"].mean(),
                        "loyer_moyen": dept_data["loyer_moyen_m2"].mean(),
                        "rendement_moyen": dept_data["rendement_brut_pct"].mean(),
                    })
            
            if dept_stats_list:
                pd.DataFrame(dept_stats_list).to_excel(
                    writer, sheet_name="Stats par département", index=False
                )

        logger.info(f"\n✅ Analyse combinée exportée: {output_file}")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.info("Assurez-vous que les données DVF et de loyers sont téléchargées et nettoyées")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse combinée: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline d'analyse des données immobilières Île-de-France"
    )
    parser.add_argument(
        "--year", 
        type=int, 
        default=2023, 
        help="Année des données DVF (ventes) (défaut: 2023)"
    )
    parser.add_argument(
        "--rent-year", 
        type=int, 
        default=2024, 
        help="Année des données de loyers (défaut: 2024)"
    )
    parser.add_argument(
        "--download", 
        action="store_true", 
        help="Télécharger les données DVF (ventes)"
    )
    parser.add_argument(
        "--download-rent", 
        action="store_true", 
        help="Télécharger les données de loyers"
    )
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="Nettoyer les données DVF"
    )
    parser.add_argument(
        "--analyze", 
        action="store_true", 
        help="Analyser les données DVF (ventes uniquement)"
    )
    parser.add_argument(
        "--analyze-rent", 
        action="store_true", 
        help="Analyser les données de loyers uniquement"
    )
    parser.add_argument(
        "--analyze-combined", 
        action="store_true", 
        help="Analyser les données combinées (ventes + loyers)"
    )
    parser.add_argument(
        "--analyze-combined2", 
        action="store_true", 
        help="Analyser les données combinées (ventes + loyers) - version 2"
    )

    parser.add_argument(
        "--full-pipeline", 
        action="store_true", 
        help="Exécuter le pipeline complet (ventes + loyers)"
    )

    args = parser.parse_args()

    # Si aucune action spécifiée, afficher l'aide
    if not any([
        args.download, args.download_rent, args.clean, 
        args.analyze, args.analyze_rent, args.analyze_combined, args.analyze_combined2,
        args.full_pipeline
    ]):
        parser.print_help()
        sys.exit(0)

    print("\n" + "=" * 80)
    print(f"📈 Analyse des Statistiques Immobilières Île-de-France")
    print(f"   Ventes (DVF): {args.year} | Loyers: {args.rent_year}")
    print("=" * 80 + "\n")

    success = True

    # Pipeline complet
    if args.full_pipeline:
        # Télécharger DVF
        success = download_data(args.year)
        if not success:
            sys.exit(1)

        # Télécharger loyers
        success = download_rent_data(args.rent_year)
        if not success:
            sys.exit(1)

        # Nettoyer DVF
        success = clean_data(args.year)
        if not success:
            sys.exit(1)

        # Analyse combinée
        success = analyze_combined2(args.year, args.rent_year)
        if not success:
            sys.exit(1)

    else:
        # Étapes individuelles
        if args.download:
            success = download_data(args.year)
            if not success:
                sys.exit(1)

        if args.download_rent:
            success = download_rent_data(args.rent_year)
            if not success:
                sys.exit(1)

        if args.clean:
            success = clean_data(args.year)
            if not success:
                sys.exit(1)

        if args.analyze:
            success = analyze_data(args.year)
            if not success:
                sys.exit(1)

        if args.analyze_rent:
            success = analyze_rent_data(args.rent_year)
            if not success:
                sys.exit(1)

        if args.analyze_combined:
            success = analyze_combined(args.year, args.rent_year)
            if not success:
                sys.exit(1)

        if args.analyze_combined2:
            success = analyze_combined2(args.year, args.rent_year)
            if not success:
                sys.exit(1)

    if success:
        print("\n" + "=" * 80)
        print("✅ Pipeline terminé avec succès!")
        print("=" * 80 + "\n")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
