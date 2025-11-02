# Guide du Projet - Statistiques Immobilières Île-de-France

## 1. Vue d'Ensemble du Projet

### Description
Ce projet Python permet d'effectuer des analyses statistiques sur les villes d'Île-de-France en utilisant les données de la base DVF (Demandes de Valeurs Foncières) du gouvernement français. L'objectif principal est d'extraire et d'analyser les prix d'achat au mètre carré (moyen, haut, bas) pour différentes communes.

### Technologies Clés
- **Langage**: Python 3.9+
- **Gestion des données**: pandas, numpy
- **Requêtes HTTP**: requests
- **Visualisation**: matplotlib, seaborn
- **API**: Base DVF (open data gouv.fr)

### Architecture
```
Architecture en couches:
├── Data Layer: Téléchargement et stockage des données DVF
├── Processing Layer: Nettoyage et transformation des données
├── Analysis Layer: Calcul des statistiques (prix min/max/moyen au m²)
└── Presentation Layer: Export et visualisation des résultats
```

---

## 2. Démarrage

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Connexion internet (pour télécharger les données DVF)
- ~500MB d'espace disque pour les données

### Installation

1. **Cloner le dépôt**
```bash
git clone <url-du-depot>
cd StephanePiazo
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

### Usage de Base

#### Télécharger les données DVF
```python
from src.data.dvf_downloader import DVFDownloader

downloader = DVFDownloader()
downloader.download_idf_data(year=2023)
```

#### Analyser les prix au m²
```python
from src.analysis.price_analyzer import PriceAnalyzer

analyzer = PriceAnalyzer()
stats = analyzer.get_city_stats("Paris")
print(f"Prix moyen: {stats['prix_moyen_m2']}€/m²")
```

### Exécution des Tests
```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=src tests/

# Tests d'un module spécifique
pytest tests/test_dvf_downloader.py
```

---

## 3. Structure du Projet

### Organisation des Répertoires

```
StephanePiazo/
├── .continue/
│   └── rules/              # Documentation et règles du projet
│       └── CONTINUE.md     # Ce fichier
├── src/                    # Code source principal
│   ├── __init__.py
│   ├── data/              # Modules de gestion des données
│   │   ├── __init__.py
│   │   ├── dvf_downloader.py    # Téléchargement des données DVF
│   │   └── data_cleaner.py      # Nettoyage des données
│   ├── analysis/          # Modules d'analyse statistique
│   │   ├── __init__.py
│   │   ├── price_analyzer.py    # Analyse des prix au m²
│   │   └── statistics.py        # Calculs statistiques généraux
│   ├── models/            # Structures de données et modèles
│   │   ├── __init__.py
│   │   └── city.py             # Modèle City
│   └── utils/             # Utilitaires divers
│       ├── __init__.py
│       └── config.py           # Configuration globale
├── data/                  # Données téléchargées (ignoré par git)
│   ├── raw/              # Données brutes DVF
│   └── processed/        # Données traitées
├── tests/                 # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── test_dvf_downloader.py
│   └── test_price_analyzer.py
├── notebooks/             # Jupyter notebooks pour exploration
│   └── exploration.ipynb
├── outputs/              # Résultats des analyses
│   ├── reports/          # Rapports générés
│   └── visualizations/   # Graphiques
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt      # Dépendances Python
└── pyproject.toml       # Configuration du projet
```

### Fichiers Clés

- **src/data/dvf_downloader.py**: Gestion du téléchargement des données DVF depuis l'API gouvernementale
- **src/analysis/price_analyzer.py**: Calculs statistiques sur les prix (min/max/moyen au m²)
- **src/models/city.py**: Représentation d'une ville avec ses statistiques
- **src/utils/config.py**: Configuration (URLs API, chemins de fichiers, départements IDF)
- **requirements.txt**: Liste des dépendances Python
- **tests/**: Tests unitaires pour assurer la qualité du code

---

## 4. Flux de Développement

### Standards de Code
- **Style**: PEP 8 (validation avec `ruff` ou `black`)
- **Type hints**: Utiliser les annotations de type Python
- **Docstrings**: Format Google ou NumPy pour toutes les fonctions publiques
- **Naming conventions**:
  - Classes: PascalCase (ex: `PriceAnalyzer`)
  - Fonctions/variables: snake_case (ex: `calculate_average_price`)
  - Constantes: UPPER_SNAKE_CASE (ex: `IDF_DEPARTMENTS`)

### Approche de Test
- Tests unitaires avec `pytest`
- Couverture minimum: 80%
- Tests d'intégration pour les flux complets
- Mocks pour les appels API externes

### Processus de Build et Déploiement
1. **Développement local**: Travail dans une branche feature
2. **Tests**: Exécution de la suite de tests
3. **Linting**: Vérification du code avec ruff/black
4. **PR Review**: Revue de code par les pairs
5. **Merge**: Fusion dans main après validation

### Guidelines de Contribution
1. Créer une branche depuis `main`: `git checkout -b feature/nom-feature`
2. Commiter régulièrement avec des messages clairs
3. Ajouter des tests pour les nouvelles fonctionnalités
4. Mettre à jour la documentation si nécessaire
5. Créer une Pull Request avec description détaillée

---

## 5. Concepts Clés

### Terminologie du Domaine

- **DVF (Demandes de Valeurs Foncières)**: Base de données publique contenant les transactions immobilières en France
- **Prix au m²**: Prix moyen par mètre carré d'un bien immobilier
- **Île-de-France (IDF)**: Région comprenant 8 départements (75, 77, 78, 91, 92, 93, 94, 95)
- **Mutation**: Transaction immobilière enregistrée dans la base DVF
- **Nature de mutation**: Type de transaction (vente, échange, etc.)
- **Valeur foncière**: Montant de la transaction immobilière

### Abstractions Principales

#### City (Modèle)
Représente une ville avec ses statistiques immobilières:
```python
@dataclass
class City:
    name: str
    code_insee: str
    department: str
    stats: CityStats
```

#### DVFDownloader
Responsable du téléchargement et de la mise en cache des données DVF:
- Gère les appels API vers data.gouv.fr
- Filtre les données par région (IDF) et année
- Sauvegarde en format Parquet pour optimiser le stockage

#### PriceAnalyzer
Calcule les statistiques sur les prix au m²:
- Prix moyen, médian, min, max par ville
- Évolution temporelle des prix
- Comparaisons inter-villes

### Patterns de Conception Utilisés

1. **Repository Pattern**: Pour l'accès aux données DVF
2. **Strategy Pattern**: Différentes stratégies de calcul statistique
3. **Factory Pattern**: Création d'analyseurs selon le type de bien
4. **Singleton**: Configuration globale unique

---

## 6. Tâches Courantes

### Ajouter une Nouvelle Statistique

1. Créer la fonction dans `src/analysis/price_analyzer.py`:
```python
def calculate_price_percentile(self, city: str, percentile: int) -> float:
    """Calcule le percentile des prix pour une ville."""
    df = self.data[self.data['commune'] == city]
    return df['prix_m2'].quantile(percentile / 100)
```

2. Ajouter des tests dans `tests/test_price_analyzer.py`
3. Documenter dans le README

### Télécharger des Données pour une Nouvelle Année

```python
from src.data.dvf_downloader import DVFDownloader

downloader = DVFDownloader()
# Télécharger 2024
downloader.download_idf_data(year=2024)
```

### Exporter les Résultats au Format Excel

```python
from src.analysis.price_analyzer import PriceAnalyzer

analyzer = PriceAnalyzer()
results = analyzer.analyze_all_cities()
results.to_excel('outputs/reports/statistiques_idf.xlsx', index=False)
```

### Créer une Visualisation

```python
import matplotlib.pyplot as plt
from src.analysis.price_analyzer import PriceAnalyzer

analyzer = PriceAnalyzer()
cities = ['Paris', 'Versailles', 'Saint-Denis']
prices = [analyzer.get_average_price(city) for city in cities]

plt.bar(cities, prices)
plt.title('Prix moyen au m² par ville')
plt.ylabel('Prix (€/m²)')
plt.savefig('outputs/visualizations/comparison.png')
```

### Nettoyer les Données Téléchargées

```bash
# Supprimer les données brutes
rm -rf data/raw/*

# Garder uniquement les données traitées
# (elles seront régénérées au prochain téléchargement)
```

---

## 7. Dépannage

### Problèmes Courants

#### Erreur: "API DVF ne répond pas"
**Cause**: Le service data.gouv.fr peut être temporairement indisponible
**Solution**: 
- Vérifier l'état du service: https://status.data.gouv.fr/
- Réessayer après quelques minutes
- Utiliser les données en cache si disponibles

#### Erreur: "MemoryError lors du traitement"
**Cause**: Les fichiers DVF sont volumineux (plusieurs Go)
**Solution**:
```python
# Traiter par chunks
analyzer = PriceAnalyzer(chunk_size=100000)
```

#### Les prix semblent aberrants
**Cause**: Données mal nettoyées ou transactions atypiques
**Solution**:
- Vérifier les filtres dans `data_cleaner.py`
- Exclure les outliers extrêmes:
```python
# Exclure les prix < 500€/m² et > 20000€/m²
df = df[(df['prix_m2'] >= 500) & (df['prix_m2'] <= 20000)]
```

#### Tests échouent sur CI/CD
**Cause**: Dépendances manquantes ou versions incompatibles
**Solution**:
```bash
# Régénérer requirements.txt
pip freeze > requirements.txt

# Ou utiliser poetry pour la gestion des dépendances
poetry export -f requirements.txt --output requirements.txt
```

### Conseils de Débogage

1. **Activer les logs détaillés**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Inspecter les données brutes**:
```python
import pandas as pd
df = pd.read_parquet('data/raw/dvf_2023.parquet')
print(df.head())
print(df.info())
```

3. **Utiliser le debugger Python**:
```python
import pdb; pdb.set_trace()  # Point d'arrêt
```

---

## 8. Références

### Documentation Officielle

- **Base DVF**: https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/
- **API DVF**: https://app.dvf.etalab.gouv.fr/
- **Documentation pandas**: https://pandas.pydata.org/docs/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html

### Ressources Utiles

- **Données géographiques IDF**: https://www.data.gouv.fr/fr/organizations/region-ile-de-france/
- **Codes INSEE des communes**: https://www.insee.fr/fr/information/3720946
- **Guide DVF**: https://doc-datafoncier.cerema.fr/dv3f/tuto/tuto_qgis_dv3f

### APIs et Services

- **API Geo Gouv**: https://geo.api.gouv.fr/ (pour enrichir les données géographiques)
- **API Cadastre**: https://cadastre.data.gouv.fr/

### Outils de Développement

- **pytest**: https://docs.pytest.org/
- **ruff**: https://docs.astral.sh/ruff/
- **pandas profiling**: https://github.com/ydataai/ydata-profiling (pour analyse exploratoire)

---

## Notes Importantes

### Limitations Connues
- Les données DVF ne contiennent pas toutes les transactions (certaines sont confidentielles)
- Délai de publication: ~6 mois après la transaction
- Qualité variable selon les départements

### Prochaines Étapes Suggérées
1. Ajouter l'analyse des types de biens (appartements vs maisons)
2. Implémenter des prédictions de prix avec ML
3. Créer un dashboard interactif avec Streamlit
4. Ajouter des comparaisons avec d'autres régions françaises

### Contact et Support
- Mainteneur: Jules Diaz
- License: MIT (voir LICENSE)

---

**Dernière mise à jour**: 2025-01-02
**Version du projet**: 0.1.0
