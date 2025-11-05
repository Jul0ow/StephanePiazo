"""
Exemple d'utilisation de l'analyse combinée (ventes + loyers).

Ce script montre comment obtenir un résumé complet par ville avec:
- Prix de vente au m² (bas, moyen, haut)
- Prix de location au m² (bas, moyen, haut)
- Rendement locatif brut

Usage:
    python examples/combined_analysis_example.py
"""

import pandas as pd
from pathlib import Path

from src.analysis.combined_analyzer import CombinedAnalyzer
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.rent_analyzer import RentAnalyzer


def print_city_summary(city_name: str, dvf_year: int = 2023, rent_year: int = 2024):
    """Affiche un résumé complet pour une ville."""
    print(f"\n{'=' * 80}")
    print(f"📊 RÉSUMÉ COMPLET - {city_name.upper()}")
    print(f"{'=' * 80}")

    try:
        # Analyseur de ventes (DVF)
        price_analyzer = PriceAnalyzer()
        price_analyzer.load_data(year=dvf_year)
        
        # Analyseur de loyers
        rent_analyzer = RentAnalyzer(year=rent_year)
        
        # Statistiques de vente
        vente_stats = price_analyzer.get_city_stats(city_name)
        
        # Statistiques de loyers
        loyer_stats = rent_analyzer.get_city_rent_stats(city_name=city_name)
        
        if vente_stats:
            print(f"\n🏠 PRIX DE VENTE ({dvf_year}):")
            print(f"   Prix bas:    {vente_stats.prix_min_m2:>10,.0f} €/m²")
            print(f"   Prix moyen:  {vente_stats.prix_moyen_m2:>10,.0f} €/m²")
            print(f"   Prix haut:   {vente_stats.prix_max_m2:>10,.0f} €/m²")
            print(f"   Transactions: {vente_stats.nombre_transactions:>9,}")
            
            if vente_stats.appartements:
                print(f"\n   📦 Appartements:")
                print(f"      Prix moyen: {vente_stats.appartements.prix_moyen_m2:>10,.0f} €/m²")
                print(f"      Transactions: {vente_stats.appartements.nombre_transactions:>7,}")
            
            if vente_stats.maisons:
                print(f"\n   🏡 Maisons:")
                print(f"      Prix moyen: {vente_stats.maisons.prix_moyen_m2:>10,.0f} €/m²")
                print(f"      Transactions: {vente_stats.maisons.nombre_transactions:>7,}")
        else:
            print(f"\n⚠️  Pas de données de vente pour {city_name}")
        
        if loyer_stats:
            print(f"\n🔑 PRIX DE LOCATION ({rent_year}):")
            if loyer_stats.loyer_bas_m2 and loyer_stats.loyer_haut_m2:
                print(f"   Loyer bas:   {loyer_stats.loyer_bas_m2:>10,.2f} €/m²/mois")
                print(f"   Loyer moyen: {loyer_stats.loyer_moyen_m2:>10,.2f} €/m²/mois")
                print(f"   Loyer haut:  {loyer_stats.loyer_haut_m2:>10,.2f} €/m²/mois")
            else:
                print(f"   Loyer moyen: {loyer_stats.loyer_moyen_m2:>10,.2f} €/m²/mois")
            
            print(f"   Type prédiction: {loyer_stats.type_prediction}")
            print(f"   Fiable: {'✓' if loyer_stats.is_reliable else '✗'}")
            
            if loyer_stats.nb_observations_commune:
                print(f"   Observations: {loyer_stats.nb_observations_commune:>8,}")
        else:
            print(f"\n⚠️  Pas de données de location pour {city_name}")
        
        # Calculer le rendement locatif si les deux sont disponibles
        if vente_stats and loyer_stats and loyer_stats.loyer_moyen_m2:
            loyer_annuel_m2 = loyer_stats.loyer_moyen_m2 * 12
            rendement_brut = (loyer_annuel_m2 / vente_stats.prix_moyen_m2) * 100
            
            print(f"\n💰 RENDEMENT LOCATIF BRUT:")
            print(f"   Loyer annuel: {loyer_annuel_m2:>10,.2f} €/m²/an")
            print(f"   Prix d'achat: {vente_stats.prix_moyen_m2:>10,.0f} €/m²")
            print(f"   Rendement:    {rendement_brut:>10,.2f} %")
            
            # Estimation du rendement net (approximatif: -30% de charges)
            rendement_net_approx = rendement_brut * 0.7
            print(f"   Rendement net estimé*: {rendement_net_approx:>6,.2f} %")
            print(f"   * Estimation approximative (-30% de charges)")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    print(f"\n{'=' * 80}")


def compare_multiple_cities(cities: list[str], dvf_year: int = 2023, rent_year: int = 2024):
    """Compare plusieurs villes."""
    print(f"\n{'=' * 100}")
    print(f"📊 COMPARAISON MULTI-VILLES")
    print(f"{'=' * 100}\n")
    
    results = []
    
    price_analyzer = PriceAnalyzer()
    price_analyzer.load_data(year=dvf_year)
    rent_analyzer = RentAnalyzer(year=rent_year)
    
    for city in cities:
        try:
            vente_stats = price_analyzer.get_city_stats(city)
            loyer_stats = rent_analyzer.get_city_rent_stats(city_name=city)
            
            result = {
                "Ville": city,
                "Prix vente (€/m²)": vente_stats.prix_moyen_m2 if vente_stats else None,
                "Loyer (€/m²/mois)": loyer_stats.loyer_moyen_m2 if loyer_stats else None,
            }
            
            if vente_stats and loyer_stats and loyer_stats.loyer_moyen_m2:
                loyer_annuel = loyer_stats.loyer_moyen_m2 * 12
                rendement = (loyer_annuel / vente_stats.prix_moyen_m2) * 100
                result["Rendement brut (%)"] = round(rendement, 2)
            else:
                result["Rendement brut (%)"] = None
            
            results.append(result)
        except Exception as e:
            print(f"⚠️  Erreur pour {city}: {e}")
    
    df = pd.DataFrame(results)
    df = df.sort_values("Rendement brut (%)", ascending=False)
    
    print(df.to_string(index=False))
    print(f"\n{'=' * 100}")


def export_department_analysis(dept_code: str, dvf_year: int = 2023, rent_year: int = 2024):
    """Exporte une analyse complète pour un département."""
    print(f"\n📥 Export de l'analyse pour le département {dept_code}...")
    
    try:
        combined = CombinedAnalyzer(dvf_year=dvf_year, rent_year=rent_year)
        
        # Charger les données
        combined.price_analyzer.load_data(year=dvf_year)
        rent_data = combined.rent_analyzer.load_idf_data()
        
        # Filtrer par département
        dept_rent_data = rent_data[rent_data["DEP"] == dept_code]
        
        results = []
        
        for _, row in dept_rent_data.iterrows():
            city_name = row["LIBGEO"]
            
            # Stats de vente
            vente_stats = combined.price_analyzer.get_city_stats(city_name)
            
            result = {
                "ville": city_name,
                "code_insee": row["INSEE_C"],
                "loyer_moyen_m2": row["loypredm2"] if pd.notna(row["loypredm2"]) else None,
                "loyer_bas_m2": row["lwr_IPm2"] if pd.notna(row["lwr_IPm2"]) else None,
                "loyer_haut_m2": row["upr_IPm2"] if pd.notna(row["upr_IPm2"]) else None,
            }
            
            if vente_stats:
                result.update({
                    "prix_vente_moyen_m2": vente_stats.prix_moyen_m2,
                    "prix_vente_bas_m2": vente_stats.prix_min_m2,
                    "prix_vente_haut_m2": vente_stats.prix_max_m2,
                    "nb_transactions": vente_stats.nombre_transactions,
                })
                
                if result["loyer_moyen_m2"]:
                    loyer_annuel = result["loyer_moyen_m2"] * 12
                    result["rendement_brut_pct"] = (loyer_annuel / result["prix_vente_moyen_m2"]) * 100
            
            results.append(result)
        
        df = pd.DataFrame(results)
        
        # Exporter
        output_file = Path(f"outputs/reports/analyse_dept_{dept_code}_{dvf_year}_{rent_year}.xlsx")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_excel(output_file, index=False)
        print(f"✅ Analyse exportée: {output_file}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("🏠 EXEMPLES D'ANALYSE COMBINÉE - Ventes + Loyers")
    print("=" * 100)
    
    # Exemple 1: Résumé détaillé pour quelques villes
    print("\n📍 EXEMPLE 1: Résumés détaillés par ville")
    for city in ["Paris", "Versailles", "Saint-Denis"]:
        print_city_summary(city)
    
    # Exemple 2: Comparaison de plusieurs villes
    print("\n📍 EXEMPLE 2: Comparaison multi-villes")
    cities = [
        "Paris", "Versailles", "Saint-Denis", "Créteil", 
        "Nanterre", "Montreuil", "Boulogne-Billancourt"
    ]
    compare_multiple_cities(cities)
    
    # Exemple 3: Export pour un département
    print("\n📍 EXEMPLE 3: Export département 92 (Hauts-de-Seine)")
    export_department_analysis("92")
    
    print("\n" + "=" * 100)
    print("✅ Exemples terminés!")
    print("=" * 100 + "\n")
