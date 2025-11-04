# Module d'Analyse des Loyers - Documentation Technique

## Architecture du Module

```
src/
├── data/
│   └── rent_downloader.py      # Téléchargement des données Carte des loyers
├── analysis/
│   ├── rent_analyzer.py        # Analyse des données de loyers
│   └── combined_analyzer.py    # Analyse combinée DVF + Loyers
└── models/
    └── city.py                 # Modèles: RentStats, CityStats (étendu)
```

---

## Classes Principales

### 1. RentDownloader

**Fichier**: `src/data/rent_downloader.py`

**Responsabilité**: Télécharger et gérer les données de la Carte des loyers depuis data.gouv.fr.

#### Méthodes Publiques

```python
class RentDownloader:
    def __init__(self, data_dir: Optional[Path] = None)
    
    def download_rent_data(self, year: int = 2024) -> Optional[Path]
    """Télécharge les données depuis l'URL par défaut."""
    
    def download_rent_data_from_url(self, url: str, year: int = 2024) -> Optional[Path]
    """Télécharge depuis une URL personnalisée."""
    
    def load_rent_data(self, year: int = 2024) -> pd.DataFrame
    """Charge les données depuis le fichier local."""
    
    def filter_idf_data(self, df: pd.DataFrame) -> pd.DataFrame
    """Filtre pour ne garder que l'Île-de-France."""
    
    def save_as_parquet(self, df: pd.DataFrame, year: int = 2024) -> Path
    """Sauvegarde en format Parquet optimisé."""
```

#### Exemple d'Usage

```python
downloader = RentDownloader()

# Télécharger
url = "https://URL_DU_FICHIER.csv"
downloader.download_rent_data_from_url(url, year=2024)

# Charger et filtrer
df = downloader.load_rent_data(year=2024)
df_idf = downloader.filter_idf_data(df)

# Sauvegarder
downloader.save_as_parquet(df_idf, year=2024)
```

---

### 2. RentStats

**Fichier**: `src/models/city.py`

**Responsabilité**: Représenter les statistiques de loyers d'une commune.

#### Structure

```python
@dataclass
class RentStats:
    loyer_moyen_m2: Optional[float]          # Loyer moyen €/m²/mois
    loyer_bas_m2: Optional[float]            # Borne basse intervalle 95%
    loyer_haut_m2: Optional[float]           # Borne haute intervalle 95%
    type_prediction: Optional[str]           # "Commune", "epci", "maile"
    nb_observations_commune: Optional[int]   # Nb observations commune
    nb_observations_maille: Optional[int]    # Nb observations maille
    r2_ajuste: Optional[float]               # R² ajusté (0-1)
    id_maille: Optional[str]                 # Identifiant de la maille
    
    @property
    def is_reliable(self) -> bool:
        """Retourne True si R² ≥ 0.5 et observations ≥ 30."""
```

#### Exemple d'Usage

```python
stats = RentStats(
    loyer_moyen_m2=25.5,
    loyer_bas_m2=23.0,
    loyer_haut_m2=28.0,
    type_prediction="Commune",
    nb_observations_commune=120,
    r2_ajuste=0.75
)

print(f"Fiable: {stats.is_reliable}")  # True
print(f"Loyer annuel: {stats.loyer_moyen_m2 * 12}€/m²")  # 306.0€/m²
```

---

### 3. RentAnalyzer

**Fichier**: `src/analysis/rent_analyzer.py`

**Responsabilité**: Analyser les données de loyers et calculer des statistiques.

#### Méthodes Publiques

```python
class RentAnalyzer:
    def __init__(self, year: int = 2024, data_dir: Optional[Path] = None)
    
    def load_data(self) -> pd.DataFrame
    """Charge les données brutes."""
    
    def load_idf_data(self) -> pd.DataFrame
    """Charge et filtre pour l'IDF."""
    
    def get_city_rent_stats(
        self, 
        city_name: Optional[str] = None,
        insee_code: Optional[str] = None
    ) -> Optional[RentStats]
    """Récupère les stats pour une ville."""
    
    def get_department_statistics(self, department_code: str) -> pd.DataFrame
    """Calcule les stats agrégées par département."""
    
    def get_idf_statistics(self) -> pd.DataFrame
    """Calcule les stats pour toute l'IDF."""
    
    def compare_cities(self, city_names: list[str]) -> pd.DataFrame
    """Compare plusieurs villes."""
    
    def get_top_cities(
        self,
        n: int = 10,
        department_code: Optional[str] = None,
        ascending: bool = False
    ) -> pd.DataFrame
    """Récupère les top villes par loyer."""
    
    def export_to_excel(
        self,
        output_file: Path,
        department_code: Optional[str] = None
    ) -> None
    """Exporte vers Excel multi-feuilles."""
```

#### Exemple d'Usage Complet

```python
from src.analysis.rent_analyzer import RentAnalyzer

# Initialiser
analyzer = RentAnalyzer(year=2024)

# Charger les données
data = analyzer.load_idf_data()
print(f"Chargé: {len(data)} communes")

# Analyser une ville
paris = analyzer.get_city_rent_stats(city_name="Paris")
if paris:
    print(f"Loyer Paris: {paris.loyer_moyen_m2:.2f}€/m²")
    print(f"Fiable: {paris.is_reliable}")

# Comparer des villes
comparison = analyzer.compare_cities([
    "Paris", "Versailles", "Nanterre"
])
print(comparison)

# Top 10
top10 = analyzer.get_top_cities(n=10, ascending=False)
print(top10)

# Export Excel
analyzer.export_to_excel(Path("output.xlsx"))
```

---

### 4. CombinedAnalyzer

**Fichier**: `src/analysis/combined_analyzer.py`

**Responsabilité**: Combiner les analyses DVF (prix d'achat) et loyers.

#### Méthodes Publiques

```python
class CombinedAnalyzer:
    def __init__(self, dvf_year: int = 2023, rent_year: int = 2024)
    
    def get_city_complete_stats(
        self,
        city_name: Optional[str] = None,
        insee_code: Optional[str] = None
    ) -> Optional[dict]
    """Récupère toutes les stats (achat + loyers)."""
    
    def calculate_rental_yield(
        self,
        city_name: Optional[str] = None,
        insee_code: Optional[str] = None,
        prix_achat_m2: Optional[float] = None
    ) -> Optional[dict]
    """Calcule le rendement locatif brut."""
    
    def get_best_rental_yield_cities(
        self,
        n: int = 20,
        department_code: Optional[str] = None,
        prix_achat_dict: Optional[dict] = None
    ) -> pd.DataFrame
    """Trouve les meilleures opportunités de rendement."""
    
    def create_comparison_report(
        self,
        city_names: list[str],
        output_file: Optional[Path] = None
    ) -> pd.DataFrame
    """Crée un rapport de comparaison complet."""
    
    def export_combined_data(
        self,
        output_file: Optional[Path] = None,
        department_code: Optional[str] = None
    ) -> None
    """Exporte toutes les données combinées."""
```

#### Exemple d'Usage

```python
from src.analysis.combined_analyzer import CombinedAnalyzer

# Initialiser
combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

# Calculer un rendement
rendement = combined.calculate_rental_yield(
    city_name="Versailles",
    prix_achat_m2=5500  # Prix d'achat estimé
)

if rendement:
    print(f"Rendement brut: {rendement['rendement_brut_pct']:.2f}%")
    print(f"Loyer mensuel: {rendement['loyer_mensuel_m2']:.2f}€/m²")
    print(f"Loyer annuel: {rendement['loyer_annuel_m2']:.2f}€/m²")

# Comparer plusieurs villes
comparison = combined.create_comparison_report(
    city_names=["Paris", "Lyon", "Marseille"],
    output_file=Path("comparison.xlsx")
)

# Export complet
combined.export_combined_data(
    output_file=Path("analyse_complete.xlsx")
)
```

---

## Schéma de Données

### Mapping des Colonnes CSV → RentStats

| Colonne CSV | Attribut RentStats | Type | Description |
|-------------|-------------------|------|-------------|
| `loypredm2` | `loyer_moyen_m2` | float | Loyer moyen €/m²/mois |
| `lwr_IPm2` | `loyer_bas_m2` | float | Borne basse 95% |
| `upr_IPm2` | `loyer_haut_m2` | float | Borne haute 95% |
| `TYPPRED` | `type_prediction` | str | Type: Commune/epci/maile |
| `nbobs_com` | `nb_observations_commune` | int | Nb observations commune |
| `nbobs_mail` | `nb_observations_maille` | int | Nb observations maille |
| `R2_adj` | `r2_ajuste` | float | R² ajusté (0-1) |
| `id_zone` | `id_maille` | str | Identifiant maille |

### Intégration avec CityStats

```python
@dataclass
class CityStats:
    # Données DVF (existant)
    prix_moyen_m2: float
    prix_median_m2: float
    # ... autres attributs DVF
    
    # NOUVEAU: Données de loyers
    loyers: Optional[RentStats] = None  # ← Ajouté
```

Usage:

```python
city = City(
    name="Paris",
    code_insee="75056",
    department="Paris",
    department_code="75",
    stats=CityStats(
        prix_moyen_m2=10000,
        prix_median_m2=9500,
        # ... autres stats DVF
        loyers=RentStats(
            loyer_moyen_m2=28.5,
            loyer_bas_m2=26.0,
            loyer_haut_m2=31.0,
            # ...
        )
    )
)

# Accès aux loyers
if city.stats and city.stats.loyers:
    loyer = city.stats.loyers.loyer_moyen_m2
```

---

## Flux de Données

```
┌─────────────────────────────────────────────────────────────┐
│                     1. TÉLÉCHARGEMENT                       │
│   data.gouv.fr → RentDownloader → data/raw/carte_loyers_*.csv│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     2. CHARGEMENT                           │
│   CSV → pandas DataFrame → Filtrage IDF → DataFrame IDF    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     3. ANALYSE                              │
│   RentAnalyzer:                                             │
│   - get_city_rent_stats() → RentStats                       │
│   - compare_cities() → DataFrame                            │
│   - get_top_cities() → DataFrame                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  4. ANALYSE COMBINÉE                        │
│   CombinedAnalyzer:                                         │
│   - calculate_rental_yield()                                │
│   - get_best_rental_yield_cities()                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     5. EXPORT                               │
│   Excel / CSV / JSON → outputs/reports/                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Variables dans `src/utils/config.py`

```python
# URLs
RENT_DATA_BASE_URL: str = "https://www.data.gouv.fr/..."
RENT_YEARS_AVAILABLE: list[int] = [2024]

# Seuils de filtrage
MIN_RENT_M2: float = 5.0      # Loyer minimum €/m²
MAX_RENT_M2: float = 100.0    # Loyer maximum €/m²

# Seuils de fiabilité
MIN_R2_THRESHOLD: float = 0.5       # R² minimum
MIN_OBSERVATIONS: int = 30          # Observations minimum
```

### Personnaliser les Seuils

```python
from src.models.city import RentStats

# Modifier les seuils de fiabilité
class CustomRentStats(RentStats):
    @property
    def is_reliable(self) -> bool:
        if not self.r2_ajuste or not self.nb_observations_commune:
            return False
        # Seuils personnalisés
        return self.r2_ajuste >= 0.6 and self.nb_observations_commune >= 50
```

---

## Tests

### Structure des Tests

```
tests/
└── test_rent_analyzer.py
    ├── TestRentAnalyzer
    │   ├── test_initialization()
    │   ├── test_load_data()
    │   ├── test_get_city_rent_stats_by_name()
    │   ├── test_get_city_rent_stats_by_insee()
    │   ├── test_compare_cities()
    │   ├── test_get_top_cities()
    │   └── ...
    └── TestRentStats
        ├── test_rent_stats_creation()
        ├── test_is_reliable_true()
        ├── test_is_reliable_false_r2()
        └── ...
```

### Exécuter les Tests

```bash
# Tous les tests du module loyers
pytest tests/test_rent_analyzer.py -v

# Avec couverture
pytest tests/test_rent_analyzer.py --cov=src.analysis.rent_analyzer --cov-report=html

# Un test spécifique
pytest tests/test_rent_analyzer.py::TestRentAnalyzer::test_get_city_rent_stats_by_name -v
```

---

## Performance et Optimisation

### Optimisations Implémentées

1. **Chargement paresseux**: Les données ne sont chargées qu'au premier appel
2. **Cache interne**: `self.data` et `self.data_idf` mis en cache
3. **Format Parquet**: Compression et chargement plus rapides que CSV
4. **Filtrage efficient**: Utilisation de pandas vectorisé

### Benchmarks Estimés

| Opération | Temps (données complètes) |
|-----------|---------------------------|
| Téléchargement CSV | ~5-10 secondes |
| Chargement CSV → DataFrame | ~2-3 secondes |
| Filtrage IDF | ~100 ms |
| get_city_rent_stats() | ~10 ms |
| compare_cities(10 villes) | ~50 ms |
| export_to_excel() | ~1-2 secondes |

### Conseils d'Optimisation

```python
# ✓ Bon: Charger une fois, réutiliser
analyzer = RentAnalyzer(year=2024)
data = analyzer.load_idf_data()  # Chargé une fois

for city in cities:
    stats = analyzer.get_city_rent_stats(city_name=city)  # Utilise le cache
    
# ✗ Mauvais: Créer un nouvel analyzer à chaque fois
for city in cities:
    analyzer = RentAnalyzer(year=2024)  # ← Recharge à chaque fois!
    stats = analyzer.get_city_rent_stats(city_name=city)
```

---

## Gestion des Erreurs

### Erreurs Courantes et Solutions

#### 1. FileNotFoundError

```python
try:
    data = analyzer.load_rent_data(year=2024)
except FileNotFoundError:
    print("Téléchargez d'abord les données:")
    print("downloader.download_rent_data(year=2024)")
```

#### 2. Commune non trouvée

```python
stats = analyzer.get_city_rent_stats(city_name="Commune")
if stats is None:
    print("Commune non trouvée ou pas de données disponibles")
    # Stratégie alternative: regarder les communes voisines
```

#### 3. Données non fiables

```python
stats = analyzer.get_city_rent_stats(city_name="Commune")
if stats and not stats.is_reliable:
    print(f"⚠ Données peu fiables:")
    print(f"  R²: {stats.r2_ajuste} (min: 0.5)")
    print(f"  Observations: {stats.nb_observations_commune} (min: 30)")
    print(f"  Type: {stats.type_prediction}")
```

---

## Extensibilité

### Ajouter de Nouvelles Analyses

```python
# Dans rent_analyzer.py

class RentAnalyzer:
    # ... méthodes existantes
    
    def get_rent_evolution(self, city_name: str, years: list[int]) -> pd.DataFrame:
        """Nouvelle méthode: Évolution des loyers sur plusieurs années."""
        results = []
        for year in years:
            analyzer_year = RentAnalyzer(year=year)
            stats = analyzer_year.get_city_rent_stats(city_name=city_name)
            if stats:
                results.append({
                    "year": year,
                    "loyer_moyen_m2": stats.loyer_moyen_m2
                })
        return pd.DataFrame(results)
```

### Ajouter de Nouveaux Attributs à RentStats

```python
# Dans models/city.py

@dataclass
class RentStats:
    # ... attributs existants
    
    # Nouveaux attributs
    surface_reference: Optional[str] = None  # "T1-T2", "T3+", etc.
    encadrement_loyer: Optional[bool] = None  # Zone encadrée?
    
    @property
    def loyer_mensuel_reference(self) -> Optional[float]:
        """Calcule le loyer pour une surface de référence."""
        if self.loyer_moyen_m2 and self.surface_reference:
            # Logique selon la surface
            pass
```

---

## Maintenance

### Checklist de Mise à Jour Annuelle

Quand une nouvelle Carte des loyers est publiée:

1. ✅ Mettre à jour `RENT_YEARS_AVAILABLE` dans `config.py`
2. ✅ Vérifier l'URL de téléchargement dans `rent_downloader.py`
3. ✅ Télécharger les nouvelles données
4. ✅ Vérifier la structure du CSV (nouvelles colonnes?)
5. ✅ Exécuter les tests: `pytest tests/test_rent_analyzer.py`
6. ✅ Mettre à jour la documentation
7. ✅ Comparer avec l'année précédente pour détecter les anomalies

### Logs et Debugging

Activer les logs détaillés:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

analyzer = RentAnalyzer(year=2024)
# Affichera des logs détaillés
```

---

## Contribuer

### Standards de Code

- **Type hints**: Toutes les fonctions publiques
- **Docstrings**: Format Google ou NumPy
- **Tests**: Couverture > 80% pour nouveau code
- **Linting**: Passer `ruff check src/`

### Pull Request Process

1. Créer une branche: `git checkout -b feature/nouvelle-analyse`
2. Développer avec tests
3. Exécuter `pytest` et `ruff check`
4. Créer une PR avec description détaillée

---

**Dernière mise à jour**: 2025-01-02  
**Mainteneur**: Équipe StephanePiazo  
**License**: MIT
