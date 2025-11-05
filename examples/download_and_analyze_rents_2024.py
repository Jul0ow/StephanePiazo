"""
Script de démonstration pour télécharger et analyser les loyers 2024.

Ce script montre comment gérer les données de loyers 2024 qui sont 
séparées en deux fichiers (appartements et maisons).
"""

import logging
from pathlib import Path

from src.analysis.rent_analyzer import RentAnalyzer
from src.data.rent_downloader import RentDownloader
from src.utils.config import REPORTS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Télécharge et analyse les données de loyers 2024."""
    
    print("=" * 80)
    print("TÉLÉCHARGEMENT ET ANALYSE DES LOYERS 2024 (APPARTEMENTS + MAISONS)")
    print("=" * 80)
    
    # Étape 1: Télécharger les données
    print("\n📥 Étape 1: Téléchargement des données...")
    downloader = RentDownloader()
    
    result = downloader.download_rent_data(year=2024)
    
    if result:
        if isinstance(result, dict):
            print(f"✓ Fichiers téléchargés:")
            for ptype, path in result.items():
                print(f"  - {ptype}: {path}")
        else:
            print(f"✓ Fichier téléchargé: {result}")
    else:
        print("❌ Échec du téléchargement")
        return
    
    # Étape 2: Charger et filtrer pour l'IDF
    print("\n📊 Étape 2: Chargement des données IDF...")
    analyzer = RentAnalyzer(year=2024)
    data = analyzer.load_idf_data()
    
    print(f"✓ {len(data)} enregistrements chargés")
    if "type_bien" in data.columns:
        print(f"  Types de bien disponibles: {data['type_bien'].unique().tolist()}")
    
    # Étape 3: Analyser une ville (exemple: Paris)
    print("\n🏙️ Étape 3: Analyse de Paris...")
    paris_stats = analyzer.get_city_rent_stats(city_name="Paris")
    
    if isinstance(paris_stats, dict):
        print("✓ Statistiques par type de bien:")
        for ptype, stats in paris_stats.items():
            print(f"\n  {ptype.upper()}:")
            print(f"    • Loyer moyen: {stats.loyer_moyen_m2:.2f} €/m²")
            print(f"    • Loyer bas: {stats.loyer_bas_m2:.2f} €/m²")
            print(f"    • Loyer haut: {stats.loyer_haut_m2:.2f} €/m²")
            print(f"    • Observations: {stats.nb_observations_commune}")
            print(f"    • Fiabilité: {'✓ Fiable' if stats.is_reliable else '⚠ Non fiable'}")
    elif paris_stats:
        print("✓ Statistiques globales:")
        print(f"  • Loyer moyen: {paris_stats.loyer_moyen_m2:.2f} €/m²")
        print(f"  • Loyer bas: {paris_stats.loyer_bas_m2:.2f} €/m²")
        print(f"  • Loyer haut: {paris_stats.loyer_haut_m2:.2f} €/m²")
    
    # Étape 4: Top 10 appartements les plus chers
    print("\n🏆 Étape 4: Top 10 loyers appartements les plus élevés...")
    top_appart = analyzer.get_top_cities(n=10, property_type="appartements", ascending=False)
    print(top_appart[["commune", "departement", "loyer_moyen_m2", "type_bien"]].to_string(index=False))
    
    # Étape 5: Top 10 maisons les plus chères
    print("\n🏆 Étape 5: Top 10 loyers maisons les plus élevés...")
    top_maisons = analyzer.get_top_cities(n=10, property_type="maisons", ascending=False)
    print(top_maisons[["commune", "departement", "loyer_moyen_m2", "type_bien"]].to_string(index=False))
    
    # Étape 6: Comparer plusieurs villes
    print("\n🔍 Étape 6: Comparaison de villes...")
    villes = ["Paris", "Versailles", "Saint-Denis", "Créteil", "Nanterre"]
    comparison = analyzer.compare_cities(villes)
    
    print(comparison[["commune", "type_bien", "loyer_moyen_m2", "fiable"]].to_string(index=False))
    
    # Étape 7: Statistiques par département
    print("\n📈 Étape 7: Statistiques par département...")
    dept_stats = analyzer.get_idf_statistics()
    print(dept_stats[["department_name", "nb_communes", "loyer_moyen", "loyer_median"]].to_string(index=False))
    
    # Étape 8: Export vers Excel
    print("\n💾 Étape 8: Export vers Excel...")
    output_file = REPORTS_DIR / "loyers_idf_2024.xlsx"
    analyzer.export_to_excel(output_file)
    print(f"✓ Rapport exporté: {output_file}")
    
    # Étape 9: Sauvegarder en Parquet pour usage ultérieur
    print("\n💾 Étape 9: Sauvegarde en Parquet...")
    parquet_file = downloader.save_as_parquet(data, year=2024)
    print(f"✓ Données sauvegardées: {parquet_file}")
    
    print("\n" + "=" * 80)
    print("✓ ANALYSE TERMINÉE AVEC SUCCÈS")
    print("=" * 80)


if __name__ == "__main__":
    main()
