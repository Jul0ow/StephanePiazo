"""
Exemple d'utilisation: Analyser les prix pour une ville spécifique.

Usage:
    python examples/analyze_city.py --city "Paris" --year 2023
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.price_analyzer import PriceAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Analyser les prix immobiliers pour une ville")
    parser.add_argument("--city", type=str, required=True, help="Nom de la ville")
    parser.add_argument("--year", type=int, default=2023, help="Année des données")
    args = parser.parse_args()

    print(f"\n📊 Analyse des prix pour {args.city} ({args.year})")
    print("=" * 60)

    # Charger les données
    analyzer = PriceAnalyzer()
    try:
        analyzer.load_data(year=args.year)
    except FileNotFoundError as e:
        print(f"\n❌ Erreur: {e}")
        print("\nAssurez-vous d'avoir téléchargé et nettoyé les données:")
        print(f"  python -m src.data.dvf_downloader --year {args.year}")
        sys.exit(1)

    # Obtenir les statistiques
    stats = analyzer.get_city_stats(args.city)

    if stats is None:
        print(f"\n❌ Aucune donnée trouvée pour {args.city}")
        print("\nVilles disponibles:")
        cities = analyzer.df["nom_commune"].unique()
        for city in sorted(cities[:20]):  # Afficher les 20 premières
            print(f"  - {city}")
        if len(cities) > 20:
            print(f"  ... et {len(cities) - 20} autres")
        sys.exit(1)

    # Afficher les résultats
    print(f"\n🏠 Statistiques pour {args.city}:")
    print(f"  Prix moyen:   {stats.prix_moyen_m2:>10,.0f} €/m²")
    print(f"  Prix médian:  {stats.prix_median_m2:>10,.0f} €/m²")
    print(f"  Prix minimum: {stats.prix_min_m2:>10,.0f} €/m²")
    print(f"  Prix maximum: {stats.prix_max_m2:>10,.0f} €/m²")
    print(f"\n📈 Volume:")
    print(f"  Transactions: {stats.nombre_transactions:>10,}")
    print(f"  Surface moy.: {stats.surface_moyenne:>10,.1f} m²")

    if stats.prix_moyen_appartement_m2:
        print(f"\n🏢 Appartements:")
        print(f"  Prix moyen:   {stats.prix_moyen_appartement_m2:>10,.0f} €/m²")

    if stats.prix_moyen_maison_m2:
        print(f"\n🏡 Maisons:")
        print(f"  Prix moyen:   {stats.prix_moyen_maison_m2:>10,.0f} €/m²")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
