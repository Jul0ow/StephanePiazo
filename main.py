"""
Script principal pour analyser les données DVF Île-de-France.

Ce script permet de:
1. Télécharger les données DVF
2. Nettoyer les données
3. Analyser les prix au m²
4. Générer des rapports

Usage:
    # Pipeline complet
    python main.py --year 2023 --full-pipeline
    
    # Étapes individuelles
    python main.py --year 2023 --download
    python main.py --year 2023 --clean
    python main.py --year 2023 --analyze
"""

import argparse
import logging
import sys
from pathlib import Path

from src.analysis.price_analyzer import PriceAnalyzer
from src.data.data_cleaner import DataCleaner
from src.data.dvf_downloader import DVFDownloader

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


def analyze_data(year: int) -> bool:
    """Analyse les données et génère les rapports."""
    logger.info(f"📊 Analyse des données {year}...")

    try:
        analyzer = PriceAnalyzer()
        analyzer.load_data(year=year)

        # Analyser toutes les villes
        all_stats = analyzer.analyze_all_cities()

        # Afficher le top 10
        logger.info(f"\n🏆 Top 10 des villes les plus chères ({year}):")
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
        analyzer.export_analysis(all_stats, filename=f"analyse_idf_{year}.xlsx")
        logger.info(f"\n✅ Analyse terminée et exportée")
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.info(f"Lancez d'abord: python main.py --year {year} --clean")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline d'analyse des données DVF Île-de-France"
    )
    parser.add_argument("--year", type=int, default=2023, help="Année des données (défaut: 2023)")
    parser.add_argument("--download", action="store_true", help="Télécharger les données")
    parser.add_argument("--clean", action="store_true", help="Nettoyer les données")
    parser.add_argument("--analyze", action="store_true", help="Analyser les données")
    parser.add_argument(
        "--full-pipeline", action="store_true", help="Exécuter le pipeline complet"
    )

    args = parser.parse_args()

    # Si aucune action spécifiée, afficher l'aide
    if not any([args.download, args.clean, args.analyze, args.full_pipeline]):
        parser.print_help()
        sys.exit(0)

    print("\n" + "=" * 80)
    print(f"📈 Analyse des Statistiques Immobilières Île-de-France ({args.year})")
    print("=" * 80 + "\n")

    success = True

    if args.full_pipeline or args.download:
        success = download_data(args.year)
        if not success and args.full_pipeline:
            sys.exit(1)

    if args.full_pipeline or args.clean:
        success = clean_data(args.year)
        if not success and args.full_pipeline:
            sys.exit(1)

    if args.full_pipeline or args.analyze:
        success = analyze_data(args.year)

    if success:
        print("\n" + "=" * 80)
        print("✅ Pipeline terminé avec succès!")
        print("=" * 80 + "\n")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
