# Statistiques Immobilières Île-de-France

Projet Python pour analyser les prix immobiliers (achat et location) en Île-de-France à partir des données ouvertes du gouvernement français.

## 🎯 Objectifs

- **Prix d'achat**: Analyser les prix au m² à partir des données DVF (Demandes de Valeurs Foncières)
- **Loyers**: Analyser les prix de location à partir de la Carte des loyers
- **Rendement locatif**: Calculer et comparer les rendements entre communes
- **Visualisations**: Créer des analyses visuelles et comparatives

## 🚀 Démarrage Rapide

### ⚠️ IMPORTANT - Données 2024 (Nouveauté)

**À partir de 2024, les données de loyers sont séparées en 2 fichiers :**
- 🏢 Appartements
- 🏠 Maisons

Le code gère automatiquement cette séparation. Voir [Guide Migration 2024](docs/MIGRATION_LOYERS_2024.md).

### 🎯 Analyse Combinée (Ventes + Loyers) - NOUVEAU!

**Pipeline complet en une seule commande :**

```bash
# Télécharge, nettoie et analyse les données de ventes ET loyers
python main.py --year 2023 --rent-year 2024 --full-pipeline
```

**Résultat :** Un fichier Excel avec un résumé complet par ville comprenant :
- 🏠 Prix de vente au m² (bas, moyen, haut)
- 🔑 Prix de location au m² (bas, moyen, haut)
- 💰 Rendement locatif brut
- 📊 Statistiques par département

📖 **[Guide complet de l'analyse combinée](docs/ANALYSE_COMBINEE.md)**

### Configuration des URLs (Optionnel)

Si les URLs par défaut ne fonctionnent pas ou si vous voulez utiliser vos propres sources :

```bash
# Créer un fichier de configuration personnalisée
cp config_urls.example.py config_urls.py

# Éditer le fichier avec vos URLs
# Voir docs/CUSTOM_URLS.md pour plus de détails
```

### Installation

```bash
# Cloner le projet
git clone <url-du-depot>
cd StephanePiazo

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### Utilisation en Ligne de Commande

```bash
# Pipeline complet (recommandé)
python main.py --year 2023 --rent-year 2024 --full-pipeline

# Étapes individuelles
python main.py --year 2023 --download              # Télécharger ventes
python main.py --rent-year 2024 --download-rent    # Télécharger loyers
python main.py --year 2023 --clean                 # Nettoyer
python main.py --year 2023 --rent-year 2024 --analyze-combined  # Analyser

# Analyses séparées
python main.py --year 2023 --analyze               # Ventes uniquement
python main.py --rent-year 2024 --analyze-rent     # Loyers uniquement
```

### Utilisation en Python

#### Résumé complet pour une ville

```python
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.rent_analyzer import RentAnalyzer

# Charger les analyseurs
price_analyzer = PriceAnalyzer()
price_analyzer.load_data(year=2023)
rent_analyzer = RentAnalyzer(year=2024)

# Statistiques de vente
vente = price_analyzer.get_city_stats("Paris")
print(f"Vente - Prix moyen: {vente.prix_moyen_m2:.0f}€/m²")
print(f"Vente - Fourchette: {vente.prix_min_m2:.0f} - {vente.prix_max_m2:.0f}€/m²")

# Statistiques de location
loyer = rent_analyzer.get_city_rent_stats(city_name="Paris")
print(f"Location - Loyer moyen: {loyer.loyer_moyen_m2:.2f}€/m²/mois")
print(f"Location - Fourchette: {loyer.loyer_bas_m2:.2f} - {loyer.loyer_haut_m2:.2f}€/m²/mois")

# Rendement locatif
loyer_annuel = loyer.loyer_moyen_m2 * 12
rendement = (loyer_annuel / vente.prix_moyen_m2) * 100
print(f"Rendement brut: {rendement:.2f}%")
```

#### Comparaison de plusieurs villes

```python
from examples.combined_analysis_example import compare_multiple_cities

cities = ["Paris", "Versailles", "Saint-Denis", "Créteil"]
compare_multiple_cities(cities, dvf_year=2023, rent_year=2024)
```

### Exemples Complets

```bash
# Analyse combinée avec exemples détaillés
python examples/combined_analysis_example.py

# Analyse des loyers uniquement
python examples/analyze_rents.py
```

## 📊 Fonctionnalités

### Prix d'Achat (DVF)
- ✅ Téléchargement automatique des données DVF (2014-2024)
- ✅ Calcul des prix min/max/moyen au m²
- ✅ Statistiques par ville et département
- ✅ Filtrage par type de bien (appartement, maison)
- 🚧 Analyse temporelle et évolution des prix

### Loyers (Carte des loyers)
- ✅ Téléchargement des données de la Carte des loyers 2024
- ✅ **Support fichiers séparés (appartements + maisons) depuis 2024**
- ✅ Calcul des loyers moyen/bas/haut au m²
- ✅ Analyse par type de bien (appartements vs maisons)
- ✅ Indicateur de fiabilité (R², nb observations)
- ✅ Comparaison entre communes
- ✅ Top des loyers par département et type
- ✅ Export Excel multi-feuilles

### Analyses Combinées
- ✅ **Pipeline complet via main.py**
- ✅ Résumé par ville (vente + location)
- ✅ Calcul du rendement locatif brut
- ✅ Identification des meilleures opportunités
- ✅ Rapports Excel multi-feuilles
- ✅ Top villes par rendement
- ✅ Statistiques par département
- 🚧 Visualisations cartographiques
- 🚧 Prédictions ML

## 📚 Documentation

### Guides Principaux
- 📖 **[Guide d'Analyse Combinée](docs/ANALYSE_COMBINEE.md)** - 🆕 Ventes + Loyers + Rendements
- 📖 **[Migration Loyers 2024](docs/MIGRATION_LOYERS_2024.md)** - 🆕 Fichiers séparés appartements/maisons
- 📖 [Guide Complet du Projet](.continue/rules/CONTINUE.md) - Architecture et développement
- 📖 [Guide d'Analyse des Loyers](docs/GUIDE_LOYERS.md) - Utilisation du module de loyers
- 📖 [Documentation Technique du Module Loyers](docs/RENT_MODULE_README.md) - API et architecture
- 📖 [Démarrage Rapide](QUICKSTART.md) - Premiers pas

### Exemples
- 🆕 `examples/combined_analysis_example.py` - Analyse combinée ventes + loyers
- 🆕 `examples/download_and_analyze_rents_2024.py` - Gestion fichiers séparés 2024
- `examples/analyze_rents.py` - Analyse complète des loyers en IDF
- `examples/analyze_city.py` - Analyse d'une ville spécifique
- `examples/download_with_custom_urls.py` - Téléchargement avec URLs personnalisées

### Configuration
- 🆕 [URLs Personnalisées](docs/CUSTOM_URLS.md) - Configurer des URLs custom pour le téléchargement

### Données Sources
- [Base DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/) - Prix d'achat
- [Carte des loyers](https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/) - Prix de location

## 🛠️ Stack Technique

- **Python** 3.9+
- **Data**: pandas, numpy, pyarrow (Parquet)
- **HTTP**: requests, urllib3
- **Visualisation**: matplotlib, seaborn
- **Export**: openpyxl (Excel)
- **Tests**: pytest, pytest-cov
- **Qualité**: ruff, black (linting/formatting)

## 📦 Structure du Projet

```
StephanePiazo/
├── src/
│   ├── data/
│   │   ├── dvf_downloader.py       # Téléchargement données DVF
│   │   ├── rent_downloader.py      # Téléchargement Carte des loyers
│   │   └── data_cleaner.py         # Nettoyage des données
│   ├── analysis/
│   │   ├── price_analyzer.py       # Analyse des prix d'achat
│   │   ├── rent_analyzer.py        # Analyse des loyers
│   │   └── combined_analyzer.py    # Analyses combinées
│   ├── models/
│   │   └── city.py                 # Modèles: City, RentStats, CityStats
│   └── utils/
│       └── config.py               # Configuration globale
├── data/
│   ├── raw/                        # Données brutes téléchargées
│   └── processed/                  # Données traitées
├── tests/                          # Tests unitaires
├── examples/                       # Scripts d'exemple
├── docs/                           # Documentation
└── outputs/
    ├── reports/                    # Rapports Excel/CSV générés
    └── visualizations/             # Graphiques et cartes
```

## 📄 License

MIT License - voir [LICENSE](LICENSE)

## 👨‍💻 Auteur

Jules Diaz
