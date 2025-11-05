# Migration vers les Données de Loyers 2024 (Appartements + Maisons Séparés)

## 📋 Vue d'Ensemble

À partir de 2024, les données de la Carte des loyers sont fournies en **deux fichiers séparés** :
- Un fichier pour les **appartements**
- Un fichier pour les **maisons**

Le code a été mis à jour pour gérer automatiquement cette séparation.

---

## 🔄 Changements Principaux

### 1. Configuration (config.py)

#### Avant (2023 et antérieur)
```python
RENT_CSV_URLS = {
    2023: "https://url/fichier_unique.csv",
}
```

#### Après (2024)
```python
RENT_CSV_URLS = {
    2024: {
        "appartements": "https://url/appartements.csv",
        "maisons": "https://url/maisons.csv",
    },
}
```

### 2. Téléchargement (RentDownloader)

#### Avant
```python
downloader = RentDownloader()
file = downloader.download_rent_data(year=2024)
# Retourne: Path vers un fichier unique
```

#### Après
```python
downloader = RentDownloader()
files = downloader.download_rent_data(year=2024)
# Retourne: dict{"appartements": Path, "maisons": Path}
```

### 3. Chargement des Données (RentDownloader)

#### Nouvelles Options

```python
# Option 1: Charger TOUS les types de biens (par défaut)
df = downloader.load_rent_data(year=2024)
# Contient une colonne "type_bien" avec "appartements" ou "maisons"

# Option 2: Charger uniquement les appartements
df_appart = downloader.load_rent_data(year=2024, property_type="appartements")

# Option 3: Charger uniquement les maisons
df_maisons = downloader.load_rent_data(year=2024, property_type="maisons")
```

### 4. Analyse (RentAnalyzer)

#### Récupération des Statistiques

```python
analyzer = RentAnalyzer(year=2024)

# Option 1: Stats globales (tous types confondus si année < 2024)
stats = analyzer.get_city_rent_stats(city_name="Paris")

# Option 2: Stats PAR TYPE (si données séparées)
stats = analyzer.get_city_rent_stats(city_name="Paris")
# Retourne: {"appartements": RentStats, "maisons": RentStats}

# Option 3: Stats pour un type spécifique
stats_appart = analyzer.get_city_rent_stats(
    city_name="Paris", 
    property_type="appartements"
)
# Retourne: RentStats
```

#### Comparaison de Villes

```python
# Comparer tous types confondus
df = analyzer.compare_cities(["Paris", "Versailles"])

# Comparer uniquement les appartements
df = analyzer.compare_cities(
    ["Paris", "Versailles"], 
    property_type="appartements"
)
```

#### Top Villes

```python
# Top 10 loyers appartements
top_appart = analyzer.get_top_cities(
    n=10, 
    property_type="appartements"
)

# Top 10 loyers maisons
top_maisons = analyzer.get_top_cities(
    n=10, 
    property_type="maisons"
)
```

---

## 🚀 Guide de Migration

### Étape 1: Mettre à Jour config.py (ou config_urls.py)

Si vous avez des URLs personnalisées, mettez-les à jour :

```python
# config_urls.py
RENT_CUSTOM_URLS = {
    2024: {
        "appartements": "https://votre-url/appartements.csv",
        "maisons": "https://votre-url/maisons.csv",
    },
}
```

### Étape 2: Télécharger les Nouvelles Données

```bash
python examples/download_and_analyze_rents_2024.py
```

Ou dans votre code :

```python
from src.data.rent_downloader import RentDownloader

downloader = RentDownloader()
result = downloader.download_rent_data(year=2024)

if isinstance(result, dict):
    print("Fichiers téléchargés:")
    for ptype, path in result.items():
        print(f"  {ptype}: {path}")
```

### Étape 3: Adapter Votre Code Existant

#### Si vous voulez les données combinées (comportement par défaut)

```python
analyzer = RentAnalyzer(year=2024)
data = analyzer.load_idf_data()
# data contient une colonne "type_bien" supplémentaire
```

#### Si vous voulez analyser séparément

```python
analyzer = RentAnalyzer(year=2024)

# Statistiques appartements
stats_appart = analyzer.get_city_rent_stats(
    city_name="Paris",
    property_type="appartements"
)

# Statistiques maisons
stats_maisons = analyzer.get_city_rent_stats(
    city_name="Paris",
    property_type="maisons"
)
```

---

## 📊 Exemple Complet

```python
from src.analysis.rent_analyzer import RentAnalyzer
from src.data.rent_downloader import RentDownloader

# 1. Télécharger
downloader = RentDownloader()
downloader.download_rent_data(year=2024)

# 2. Analyser
analyzer = RentAnalyzer(year=2024)

# 3. Comparer appartements vs maisons pour Paris
paris_stats = analyzer.get_city_rent_stats(city_name="Paris")

if isinstance(paris_stats, dict):
    for ptype, stats in paris_stats.items():
        print(f"{ptype.upper()}: {stats.loyer_moyen_m2:.2f} €/m²")
else:
    print(f"Loyer moyen: {paris_stats.loyer_moyen_m2:.2f} €/m²")

# 4. Top 10 appartements les plus chers
top_appart = analyzer.get_top_cities(
    n=10, 
    property_type="appartements",
    ascending=False
)
print(top_appart)

# 5. Export vers Excel (avec séparation par type)
analyzer.export_to_excel("loyers_2024.xlsx")
```

---

## ⚠️ Points d'Attention

### Rétrocompatibilité

Le code reste compatible avec les anciennes années (< 2024) qui ont un fichier unique :

```python
# Fonctionne toujours pour 2023
analyzer_2023 = RentAnalyzer(year=2023)
stats = analyzer_2023.get_city_rent_stats(city_name="Paris")
# Retourne: RentStats (pas de dict)
```

### Gestion des Erreurs

```python
stats = analyzer.get_city_rent_stats(
    city_name="Paris",
    property_type="appartements"
)

if stats is None:
    print("Aucune donnée trouvée")
elif isinstance(stats, dict):
    print("Plusieurs types disponibles")
    for ptype, s in stats.items():
        print(f"{ptype}: {s.loyer_moyen_m2} €/m²")
else:
    print(f"Loyer moyen: {stats.loyer_moyen_m2} €/m²")
```

### Colonne "type_bien"

Les DataFrames chargés depuis 2024 contiennent une colonne supplémentaire :

```python
data = analyzer.load_idf_data()
print(data["type_bien"].unique())
# ['appartements', 'maisons']

# Filtrer manuellement si besoin
data_appart = data[data["type_bien"] == "appartements"]
```

---

## 🔗 Ressources

- **Script de démonstration** : `examples/download_and_analyze_rents_2024.py`
- **Documentation complète** : `docs/GUIDE_LOYERS.md`
- **URLs personnalisées** : `docs/CUSTOM_URLS.md`
- **Source des données** : [data.gouv.fr - Carte des loyers 2024](https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/)

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que vous avez téléchargé les données : `python examples/download_and_analyze_rents_2024.py`
2. Vérifiez les URLs dans `config.py` ou créez `config_urls.py`
3. Consultez les logs : `logging.basicConfig(level=logging.DEBUG)`
4. Vérifiez les fichiers téléchargés dans `data/raw/`

---

**Date de mise à jour** : 2025-01-02  
**Version** : 2.0.0 (Support fichiers séparés)
