# 🚀 Quick Start - Analyse DVF Île-de-France

Guide de démarrage rapide pour commencer à analyser les données immobilières.

## Installation (5 minutes)

```bash
# 1. Créer l'environnement virtuel
python -m venv .venv

# 2. Activer l'environnement
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

## Utilisation Rapide

### Option 1: Pipeline Complet (Automatique)

```bash
# Tout en une seule commande (téléchargement, nettoyage, analyse)
python main.py --year 2023 --full-pipeline
```

### Option 2: Étape par Étape

```bash
# 1. Télécharger les données DVF
python main.py --year 2023 --download

# 2. Nettoyer les données
python main.py --year 2023 --clean

# 3. Analyser et générer les rapports
python main.py --year 2023 --analyze
```

### Option 3: Analyser une ville spécifique

```bash
python examples/analyze_city.py --city "Paris" --year 2023
```

## Résultats

Après l'exécution, vous trouverez :

- **Données brutes** : `data/raw/dvf_2023_XX.csv`
- **Données nettoyées** : `data/processed/dvf_2023_idf_clean.parquet`
- **Rapport Excel** : `outputs/reports/analyse_idf_2023.xlsx`

## Exploration Interactive

Pour explorer les données avec Jupyter :

```bash
jupyter notebook notebooks/exploration.ipynb
```

## Exemples de Code

### Analyser une ville

```python
from src.analysis.price_analyzer import PriceAnalyzer

analyzer = PriceAnalyzer()
analyzer.load_data(year=2023)

# Statistiques Paris
stats = analyzer.get_city_stats("Paris")
print(f"Prix moyen: {stats.prix_moyen_m2:,.0f}€/m²")
```

### Comparer plusieurs villes

```python
villes = ["Paris", "Versailles", "Saint-Denis"]
for ville in villes:
    stats = analyzer.get_city_stats(ville)
    if stats:
        print(f"{ville}: {stats.prix_moyen_m2:,.0f}€/m²")
```

### Analyser un département

```python
# Toutes les villes du 75 (Paris)
dept_stats = analyzer.get_department_stats("75")
print(dept_stats)
```

## Besoin d'Aide ?

- 📖 **Documentation complète** : `.continue/rules/CONTINUE.md`
- 🐛 **Dépannage** : Voir section 7 du guide CONTINUE.md
- 💬 **Questions** : Ouvrir une issue sur GitHub

## Prochaines Étapes

1. ✅ Explorez le notebook Jupyter pour des visualisations
2. ✅ Consultez le guide complet dans `.continue/rules/CONTINUE.md`
3. ✅ Personnalisez les analyses selon vos besoins
4. ✅ Ajoutez vos propres statistiques

---

**Temps estimé total** : 10-30 minutes (selon la vitesse de téléchargement)
