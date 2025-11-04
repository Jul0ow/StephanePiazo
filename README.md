# Statistiques Immobilières Île-de-France

Projet Python pour analyser les prix immobiliers (achat et location) en Île-de-France à partir des données ouvertes du gouvernement français.

## 🎯 Objectifs

- **Prix d'achat**: Analyser les prix au m² à partir des données DVF (Demandes de Valeurs Foncières)
- **Loyers**: Analyser les prix de location à partir de la Carte des loyers
- **Rendement locatif**: Calculer et comparer les rendements entre communes
- **Visualisations**: Créer des analyses visuelles et comparatives

## 🚀 Démarrage Rapide

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

### Analyse des Loyers

```python
from src.analysis.rent_analyzer import RentAnalyzer

# Créer l'analyseur
analyzer = RentAnalyzer(year=2024)

# Analyser une ville
paris_rent = analyzer.get_city_rent_stats(city_name="Paris")
print(f"Loyer moyen: {paris_rent.loyer_moyen_m2:.2f}€/m²/mois")

# Comparer plusieurs villes
comparison = analyzer.compare_cities(["Paris", "Versailles", "Nanterre"])
print(comparison)
```

### Analyse des Prix d'Achat (DVF)

```python
from src.data.dvf_downloader import DVFDownloader

# Télécharger les données DVF
downloader = DVFDownloader()
downloader.download_idf_data(year=2023)
```

### Calcul de Rendement Locatif

```python
from src.analysis.combined_analyzer import CombinedAnalyzer

# Analyseur combiné
combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

# Calculer le rendement
rendement = combined.calculate_rental_yield(
    city_name="Versailles",
    prix_achat_m2=5500
)
print(f"Rendement brut: {rendement['rendement_brut_pct']:.2f}%")
```

### Exemple Complet

```bash
# Lancer l'analyse complète des loyers
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
- ✅ Calcul des loyers moyen/bas/haut au m²
- ✅ Indicateur de fiabilité (R², nb observations)
- ✅ Comparaison entre communes
- ✅ Top des loyers par département
- ✅ Export Excel multi-feuilles

### Analyses Combinées
- ✅ Calcul du rendement locatif brut
- ✅ Identification des meilleures opportunités
- ✅ Rapports de comparaison détaillés
- 🚧 Visualisations cartographiques
- 🚧 Prédictions ML

## 📚 Documentation

### Guides Principaux
- 📖 [Guide Complet du Projet](.continue/rules/CONTINUE.md) - Architecture et développement
- 📖 [Guide d'Analyse des Loyers](docs/GUIDE_LOYERS.md) - Utilisation du module de loyers
- 📖 [Documentation Technique du Module Loyers](docs/RENT_MODULE_README.md) - API et architecture
- 📖 [Démarrage Rapide](QUICKSTART.md) - Premiers pas

### Exemples
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
