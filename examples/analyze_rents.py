"""Exemple d'utilisation de l'analyseur de loyers."""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.rent_analyzer import RentAnalyzer
from src.analysis.combined_analyzer import CombinedAnalyzer
from src.data.rent_downloader import RentDownloader
from src.utils.config import OUTPUTS_DIR


def main():
    """Fonction principale d'exemple."""
    
    print("=" * 80)
    print("ANALYSE DES LOYERS EN ÎLE-DE-FRANCE")
    print("=" * 80)
    
    # 1. Télécharger les données (si nécessaire)
    print("\n📥 Étape 1: Vérification et téléchargement des données...")
    downloader = RentDownloader()
    
    # IMPORTANT: Vous devez remplacer cette URL par l'URL réelle du fichier CSV
    # disponible sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
    
    print("\n⚠️  ATTENTION: Vous devez télécharger manuellement le fichier CSV depuis:")
    print("    https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/")
    print("    Et le placer dans le dossier: data/raw/carte_loyers_2024.csv")
    print()
    
    try:
        # 2. Créer l'analyseur
        print("\n📊 Étape 2: Chargement des données...")
        analyzer = RentAnalyzer(year=2024)
        data = analyzer.load_idf_data()
        print(f"✓ {len(data)} communes chargées pour l'Île-de-France")
        
        # 3. Analyser une ville spécifique
        print("\n" + "=" * 80)
        print("ANALYSE: PARIS")
        print("=" * 80)
        
        paris_rent = analyzer.get_city_rent_stats(city_name="Paris")
        if paris_rent:
            print(f"\n📍 Statistiques de loyers pour Paris:")
            print(f"   • Loyer moyen:    {paris_rent.loyer_moyen_m2:.2f} €/m²/mois")
            print(f"   • Loyer bas:      {paris_rent.loyer_bas_m2:.2f} €/m²/mois")
            print(f"   • Loyer haut:     {paris_rent.loyer_haut_m2:.2f} €/m²/mois")
            print(f"   • Loyer annuel:   {paris_rent.loyer_moyen_m2 * 12:.2f} €/m²/an")
            print(f"   • Type:           {paris_rent.type_prediction}")
            print(f"   • Observations:   {paris_rent.nb_observations_commune}")
            print(f"   • R² ajusté:      {paris_rent.r2_ajuste:.3f}")
            print(f"   • Fiable:         {'✓ Oui' if paris_rent.is_reliable else '✗ Non'}")
            
            # Calcul pour un appartement de 50m²
            surface = 50
            loyer_mensuel = paris_rent.loyer_moyen_m2 * surface
            loyer_annuel = loyer_mensuel * 12
            print(f"\n💡 Pour un appartement de {surface}m² à Paris:")
            print(f"   • Loyer mensuel estimé:  {loyer_mensuel:.0f} €")
            print(f"   • Loyer annuel estimé:   {loyer_annuel:.0f} €")
        
        # 4. Statistiques par département
        print("\n" + "=" * 80)
        print("STATISTIQUES PAR DÉPARTEMENT")
        print("=" * 80)
        
        idf_stats = analyzer.get_idf_statistics()
        print("\n", idf_stats.to_string(index=False))
        
        # 5. Top 15 des loyers les plus élevés
        print("\n" + "=" * 80)
        print("TOP 15 DES LOYERS LES PLUS ÉLEVÉS EN ÎLE-DE-FRANCE")
        print("=" * 80)
        
        top_15_high = analyzer.get_top_cities(n=15, ascending=False)
        print("\n", top_15_high.to_string(index=False))
        
        # 6. Top 15 des loyers les plus bas
        print("\n" + "=" * 80)
        print("TOP 15 DES LOYERS LES PLUS BAS EN ÎLE-DE-FRANCE")
        print("=" * 80)
        
        top_15_low = analyzer.get_top_cities(n=15, ascending=True)
        print("\n", top_15_low.to_string(index=False))
        
        # 7. Comparaison de villes
        print("\n" + "=" * 80)
        print("COMPARAISON DE VILLES SÉLECTIONNÉES")
        print("=" * 80)
        
        cities_to_compare = [
            "Paris", "Versailles", "Saint-Denis", "Créteil", 
            "Nanterre", "Montreuil", "Boulogne-Billancourt", "Neuilly-sur-Seine"
        ]
        
        comparison = analyzer.compare_cities(cities_to_compare)
        print("\n", comparison.to_string(index=False))
        
        # 8. Analyse par département (exemple: Paris 75)
        print("\n" + "=" * 80)
        print("FOCUS SUR PARIS (75)")
        print("=" * 80)
        
        paris_stats = analyzer.get_department_statistics("75")
        print("\n", paris_stats.to_string(index=False))
        
        # 9. Export vers Excel
        print("\n" + "=" * 80)
        print("EXPORT DES RÉSULTATS")
        print("=" * 80)
        
        output_file = OUTPUTS_DIR / "reports" / "analyse_loyers_idf_2024.xlsx"
        analyzer.export_to_excel(output_file)
        print(f"✓ Rapport Excel généré: {output_file}")
        
        # 10. Analyse combinée avec rendement locatif (exemple)
        print("\n" + "=" * 80)
        print("ANALYSE DE RENDEMENT LOCATIF (EXEMPLE)")
        print("=" * 80)
        
        combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)
        
        # Exemple avec des prix d'achat fictifs (à remplacer par vraies données DVF)
        exemple_prix = {
            "Paris": 10000,
            "Versailles": 5500,
            "Saint-Denis": 3500,
            "Créteil": 4000,
        }
        
        print("\n⚠️  Note: Les prix d'achat ci-dessous sont fictifs (exemples)")
        print("    Pour des calculs réels, intégrez les données DVF\n")
        
        for city, prix in exemple_prix.items():
            rendement = combined.calculate_rental_yield(
                city_name=city, 
                prix_achat_m2=prix
            )
            if rendement:
                print(f"📊 {city}:")
                print(f"   • Prix achat:        {rendement['prix_achat_m2']:>7.0f} €/m²")
                print(f"   • Loyer mensuel:     {rendement['loyer_mensuel_m2']:>7.2f} €/m²")
                print(f"   • Loyer annuel:      {rendement['loyer_annuel_m2']:>7.2f} €/m²")
                print(f"   • Rendement brut:    {rendement['rendement_brut_pct']:>7.2f} %")
                print()
        
        print("\n" + "=" * 80)
        print("✓ ANALYSE TERMINÉE")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\n❌ Erreur: {e}")
        print("\n💡 Veuillez d'abord télécharger les données avec:")
        print("   1. Aller sur: https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/")
        print("   2. Télécharger le fichier CSV")
        print("   3. Le placer dans: data/raw/carte_loyers_2024.csv")
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
