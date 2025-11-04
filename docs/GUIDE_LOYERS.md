# Guide d'Utilisation - Analyse des Loyers

## Vue d'ensemble

Ce guide explique comment utiliser les modules d'analyse des loyers basés sur la **Carte des loyers** publiée par le gouvernement français. Ces données permettent d'obtenir les prix moyens, bas et hauts de location au mètre carré pour les communes d'Île-de-France.

---

## 📊 Source des Données

### Carte des Loyers 2024

**URL**: https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/

**Description**: Les indicateurs de loyers sont calculés à partir des données d'annonces parues sur les plateformes leboncoin et du Groupe SeLoger sur la période 2018-2024.

**Caractéristiques**:
- Loyers charges comprises pour des biens non meublés
- Données au 3ème trimestre 2024
- Types de référence selon la surface du logement
- Niveaux de prédiction: Commune, EPCI ou Maille

---

## 🚀 Démarrage Rapide

### 1. Télécharger les Données

```python
from src.data.rent_downloader import RentDownloader

downloader = RentDownloader()

# Option 1: Téléchargement automatique (si URL configurée)
downloader.download_rent_data(year=2024)

# Option 2: Depuis une URL spécifique
url = "https://URL_DIRECTE_DU_FICHIER.csv"
downloader.download_rent_data_from_url(url, year=2024)
```

**Note**: Vous devrez peut-être télécharger manuellement le fichier CSV depuis data.gouv.fr et le placer dans `data/raw/carte_loyers_2024.csv`

### 2. Charger et Analyser les Données

```python
from src.analysis.rent_analyzer import RentAnalyzer

analyzer = RentAnalyzer(year=2024)

# Charger les données IDF
data_idf = analyzer.load_idf_data()
print(f"{len(data_idf)} communes chargées")

# Obtenir les loyers pour une ville
paris_rent = analyzer.get_city_rent_stats(city_name="Paris")
print(f"Loyer moyen à Paris: {paris_rent.loyer_moyen_m2:.2f}€/m²/mois")
```

---

## 📖 Guide Détaillé

### Analyser une Commune

```python
from src.analysis.rent_analyzer import RentAnalyzer

analyzer = RentAnalyzer(year=2024)

# Par nom de commune
rent_stats = analyzer.get_city_rent_stats(city_name="Versailles")

# Par code INSEE
rent_stats = analyzer.get_city_rent_stats(insee_code="78646")

if rent_stats:
    print(f"Loyer moyen: {rent_stats.loyer_moyen_m2:.2f} €/m²/mois")
    print(f"Loyer bas: {rent_stats.loyer_bas_m2:.2f} €/m²/mois")
    print(f"Loyer haut: {rent_stats.loyer_haut_m2:.2f} €/m²/mois")
    print(f"Loyer annuel: {rent_stats.loyer_moyen_m2 * 12:.2f} €/m²/an")
    print(f"Type de prédiction: {rent_stats.type_prediction}")
    print(f"Fiable: {rent_stats.is_reliable}")
```

### Comprendre la Fiabilité des Données

L'attribut `is_reliable` indique si les données sont fiables selon les critères suivants:
- **R² ajusté ≥ 0.5**: Le modèle explique au moins 50% de la variance
- **Nombre d'observations ≥ 30**: Au moins 30 annonces dans la commune

```python
if rent_stats.is_reliable:
    print("✓ Données fiables")
else:
    print("⚠ Données à utiliser avec prudence")
    print(f"  R²: {rent_stats.r2_ajuste}")
    print(f"  Observations: {rent_stats.nb_observations_commune}")
```

### Types de Prédiction

- **"Commune"**: Indicateur prédit au niveau de la commune (≥100 observations)
- **"epci"**: Indicateur prédit au niveau de l'EPCI (≥100 observations dans l'EPCI)
- **"maile"**: Indicateur prédit au niveau d'une maille regroupant des communes similaires (<100 observations)

---

## 📈 Analyses Avancées

### Comparer Plusieurs Villes

```python
cities = ["Paris", "Versailles", "Saint-Denis", "Nanterre", "Montreuil"]
comparison = analyzer.compare_cities(cities)

print(comparison)
# Affiche: commune, loyer_moyen_m2, loyer_bas_m2, loyer_haut_m2, fiable, etc.
```

### Top des Loyers

```python
# Top 20 des loyers les plus élevés
top_high = analyzer.get_top_cities(n=20, ascending=False)

# Top 20 des loyers les plus bas
top_low = analyzer.get_top_cities(n=20, ascending=True)

# Top des loyers pour un département spécifique
top_75 = analyzer.get_top_cities(n=10, department_code="75")
```

### Statistiques par Département

```python
# Statistiques pour Paris (75)
paris_stats = analyzer.get_department_statistics("75")

# Statistiques pour toute l'IDF
idf_stats = analyzer.get_idf_statistics()
print(idf_stats)
```

### Export vers Excel

```python
from pathlib import Path
from src.utils.config import OUTPUTS_DIR

output_file = OUTPUTS_DIR / "reports" / "loyers_idf_2024.xlsx"
analyzer.export_to_excel(output_file)

# Export pour un département spécifique
analyzer.export_to_excel(output_file, department_code="92")
```

Le fichier Excel contient:
- **Feuille 1**: Données détaillées par commune
- **Feuille 2**: Statistiques par département
- **Feuille 3**: Top 20 loyers élevés
- **Feuille 4**: Top 20 loyers bas

---

## 💰 Calcul du Rendement Locatif

### Rendement Locatif Brut

Le rendement locatif brut se calcule ainsi:

```
Rendement (%) = (Loyer annuel / Prix d'achat) × 100
```

Exemple avec l'analyseur combiné:

```python
from src.analysis.combined_analyzer import CombinedAnalyzer

combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

# Calculer le rendement pour Paris
# Prix d'achat fictif: 10000€/m²
rendement = combined.calculate_rental_yield(
    city_name="Paris",
    prix_achat_m2=10000
)

if rendement:
    print(f"Prix d'achat: {rendement['prix_achat_m2']}€/m²")
    print(f"Loyer mensuel: {rendement['loyer_mensuel_m2']:.2f}€/m²")
    print(f"Loyer annuel: {rendement['loyer_annuel_m2']:.2f}€/m²")
    print(f"Rendement brut: {rendement['rendement_brut_pct']:.2f}%")
```

### Interprétation du Rendement

- **< 3%**: Rendement faible (typique des zones très chères comme Paris centre)
- **3-5%**: Rendement moyen
- **5-7%**: Bon rendement
- **> 7%**: Excellent rendement (à vérifier la fiabilité et les risques)

**⚠ Important**: Le rendement brut ne prend pas en compte:
- Les charges de copropriété
- La taxe foncière
- Les travaux et entretien
- La vacance locative
- Les frais de gestion

Le **rendement net** est généralement 1-2% inférieur au rendement brut.

---

## 🔍 Structure des Données

### Colonnes Principales

| Variable | Description | Exemple |
|----------|-------------|---------|
| `INSEE_C` | Code INSEE de la commune | "75056" |
| `LIBGEO` | Nom de la commune | "Paris" |
| `DEP` | Code département | "75" |
| `loypredm2` | Loyer moyen (€/m²/mois) | 28.5 |
| `lwr_IPm2` | Borne basse intervalle prédiction | 26.0 |
| `upr_IPm2` | Borne haute intervalle prédiction | 31.0 |
| `TYPPRED` | Type de prédiction | "Commune" |
| `nbobs_com` | Nb observations dans la commune | 150 |
| `nbobs_mail` | Nb observations dans la maille | 150 |
| `R2_adj` | Coefficient de détermination ajusté | 0.75 |

### Objet RentStats

```python
@dataclass
class RentStats:
    loyer_moyen_m2: float          # Loyer moyen €/m²/mois
    loyer_bas_m2: float            # Loyer bas (intervalle 95%)
    loyer_haut_m2: float           # Loyer haut (intervalle 95%)
    type_prediction: str           # "Commune", "epci", "maile"
    nb_observations_commune: int   # Nombre d'observations
    r2_ajuste: float               # R² ajusté du modèle
    
    @property
    def is_reliable(self) -> bool:
        """Vérifie si R² ≥ 0.5 et observations ≥ 30"""
```

---

## 📝 Exemples Pratiques

### Exemple 1: Estimation de Loyer pour un Appartement

```python
from src.analysis.rent_analyzer import RentAnalyzer

analyzer = RentAnalyzer(year=2024)

# Appartement de 60m² à Versailles
versailles = analyzer.get_city_rent_stats(city_name="Versailles")

if versailles and versailles.is_reliable:
    surface = 60  # m²
    
    loyer_mensuel = versailles.loyer_moyen_m2 * surface
    loyer_bas = versailles.loyer_bas_m2 * surface
    loyer_haut = versailles.loyer_haut_m2 * surface
    
    print(f"Estimation loyer pour 60m² à Versailles:")
    print(f"  Loyer moyen: {loyer_mensuel:.0f}€/mois")
    print(f"  Fourchette: {loyer_bas:.0f}€ - {loyer_haut:.0f}€/mois")
    print(f"  Confiance: {versailles.is_reliable}")
```

### Exemple 2: Trouver les Meilleures Opportunités

```python
from src.analysis.combined_analyzer import CombinedAnalyzer

combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

# Comparer plusieurs villes
villes = [
    "Montreuil", "Aubervilliers", "Saint-Denis",
    "Pantin", "Ivry-sur-Seine", "Villejuif"
]

comparison = combined.create_comparison_report(
    city_names=villes,
    output_file=Path("outputs/reports/comparaison_93_94.xlsx")
)

# Trier par rendement potentiel (loyer/prix estimé)
print(comparison.sort_values("loyer_moyen_m2", ascending=False))
```

### Exemple 3: Analyse Départementale

```python
from src.analysis.rent_analyzer import RentAnalyzer
import matplotlib.pyplot as plt

analyzer = RentAnalyzer(year=2024)

# Récupérer les stats par département
stats = analyzer.get_idf_statistics()

# Créer un graphique
fig, ax = plt.subplots(figsize=(12, 6))
stats = stats.sort_values("loyer_moyen", ascending=False)

ax.bar(stats["department_name"], stats["loyer_moyen"])
ax.set_xlabel("Département")
ax.set_ylabel("Loyer moyen (€/m²/mois)")
ax.set_title("Loyers moyens par département en Île-de-France")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("outputs/visualizations/loyers_par_dept.png")
```

---

## ⚠️ Limites et Précautions

### Limites des Données

1. **Source**: Données d'annonces, pas de transactions réelles
2. **Charges comprises**: Les loyers incluent les charges
3. **Non meublés uniquement**: Pas de données pour la location meublée
4. **Délai**: Données du T3 2024, peuvent être décalées
5. **Maillage**: Pour certaines communes, prédiction basée sur des communes similaires

### Précautions d'Usage

- **Toujours vérifier `is_reliable`** avant d'utiliser les données
- **Comparer avec le marché réel** via des annonces récentes
- Les **intervalles de prédiction** (bas/haut) donnent la marge d'incertitude
- Les communes avec `type_prediction="maile"` ont moins de données locales

### Utilisation Responsable

```python
rent_stats = analyzer.get_city_rent_stats(city_name="PetiteCommune")

if rent_stats:
    if rent_stats.is_reliable:
        print(f"✓ Estimation fiable: {rent_stats.loyer_moyen_m2:.2f}€/m²")
    else:
        print(f"⚠ Estimation indicative: {rent_stats.loyer_moyen_m2:.2f}€/m²")
        print(f"  Raisons: R²={rent_stats.r2_ajuste:.2f}, "
              f"Obs={rent_stats.nb_observations_commune}")
        
        if rent_stats.type_prediction == "maile":
            print(f"  ℹ Estimation basée sur une maille de communes similaires")
```

---

## 🔧 Dépannage

### Problème: Fichier non trouvé

```
FileNotFoundError: Fichier non trouvé: data/raw/carte_loyers_2024.csv
```

**Solution**:
1. Aller sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
2. Télécharger le fichier CSV
3. Le placer dans `data/raw/carte_loyers_2024.csv`

### Problème: Commune non trouvée

```python
rent_stats = analyzer.get_city_rent_stats(city_name="MaCommune")
# Retourne None
```

**Solutions**:
- Vérifier l'orthographe exacte (majuscules, tirets, etc.)
- Utiliser le code INSEE si connu
- Vérifier que la commune est en Île-de-France
- Certaines petites communes peuvent ne pas avoir de données

### Problème: Données non fiables

Si `is_reliable` retourne `False`:

```python
rent_stats = analyzer.get_city_rent_stats(city_name="MaCommune")

if rent_stats and not rent_stats.is_reliable:
    # Option 1: Utiliser les données de la maille
    print(f"Observations maille: {rent_stats.nb_observations_maille}")
    
    # Option 2: Regarder les communes voisines
    dept = "XX"  # Code du département
    top_dept = analyzer.get_top_cities(n=50, department_code=dept)
    print(top_dept)
```

---

## 📚 Références

- **Carte des loyers**: https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
- **Méthodologie ANIL**: https://www.anil.org/lanil-et-les-observatoires-des-loyers/
- **Documentation API**: Voir le manuel fourni (pièce-jointe)

---

## 💡 Prochaines Étapes

1. **Intégrer avec DVF**: Combiner prix d'achat et loyers pour calculer les rendements réels
2. **Visualisations**: Créer des cartes interactives des loyers en IDF
3. **Prédictions**: Modèles de ML pour prédire l'évolution des loyers
4. **Alertes**: Système de notification pour les bonnes opportunités

---

**Dernière mise à jour**: 2025-01-02  
**Version**: 1.0.0
