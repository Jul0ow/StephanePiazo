# 🚀 Quick Start - Analyse Immobilière Île-de-France

Guide de démarrage rapide pour analyser les prix d'achat (DVF) et les loyers (Carte des loyers) en Île-de-France.

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

## 🏠 Analyse des Loyers (Recommandé pour commencer)

### Étape 1: Télécharger les données

#### Option A: Téléchargement automatique (Recommandé)

```python
from src.data.rent_downloader import RentDownloader

downloader = RentDownloader()
downloader.download_rent_data(year=2024)
```

#### Option B: Téléchargement manuel

⚠️ Si l'URL par défaut ne fonctionne pas:

1. **Trouvez la bonne URL**: 
   - Allez sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
   - Cliquez sur le fichier CSV et copiez l'URL

2. **Option 2A: Utilisez l'URL directement**:
```python
downloader = RentDownloader()
downloader.download_rent_data(
    year=2024,
    custom_url="https://votre-url-exacte.csv"
)
```

3. **Option 2B: Configurez l'URL (pour une utilisation répétée)**:
```bash
# Créer le fichier de configuration
cp config_urls.example.py config_urls.py

# Éditer config_urls.py et ajouter:
# RENT_CUSTOM_URLS = {
#     2024: "https://votre-url-exacte.csv",
# }
```

4. **Option 2C: Téléchargement manuel**:
   - Téléchargez le CSV depuis le site
   - Placez-le dans: `data/raw/carte_loyers_2024.csv`

📚 **Plus d'infos**: Voir [docs/CUSTOM_URLS.md](docs/CUSTOM_URLS.md)

### Étape 2: Lancer l'analyse

```bash
# Analyse complète des loyers en IDF
python examples/analyze_rents.py
```

Ce script va:
- ✅ Charger les données de loyers
- ✅ Analyser toutes les communes d'IDF
- ✅ Générer des comparaisons et classements
- ✅ Créer un rapport Excel détaillé

### Analyse Rapide en Python

```python
from src.analysis.rent_analyzer import RentAnalyzer

# Créer l'analyseur
analyzer = RentAnalyzer(year=2024)

# Analyser Paris
paris = analyzer.get_city_rent_stats(city_name="Paris")
print(f"Loyer moyen Paris: {paris.loyer_moyen_m2:.2f}€/m²/mois")
print(f"Loyer annuel: {paris.loyer_moyen_m2 * 12:.2f}€/m²/an")

# Comparer plusieurs villes
comparison = analyzer.compare_cities([
    "Paris", "Versailles", "Saint-Denis", "Nanterre"
])
print(comparison)

# Top 10 des loyers les plus élevés
top10 = analyzer.get_top_cities(n=10, ascending=False)
print(top10)
```

## 📊 Analyse des Prix d'Achat (DVF)

### Pipeline Complet (Automatique)

```bash
# Tout en une seule commande (téléchargement, nettoyage, analyse)
python main.py --year 2023 --full-pipeline
```

### Étape par Étape

```python
from src.data.dvf_downloader import DVFDownloader

# 1. Télécharger les données DVF
downloader = DVFDownloader()
downloader.download_idf_data(year=2023)

# 2. Charger les données
df = downloader.load_idf_data(year=2023)
print(f"Chargé: {len(df)} transactions")

# 3. Sauvegarder en Parquet (optimisé)
downloader.save_as_parquet(df, year=2023)
```

## 💰 Calcul de Rendement Locatif

```python
from src.analysis.combined_analyzer import CombinedAnalyzer

# Créer l'analyseur combiné
combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

# Calculer le rendement pour Versailles
rendement = combined.calculate_rental_yield(
    city_name="Versailles",
    prix_achat_m2=5500  # Prix d'achat estimé
)

if rendement:
    print(f"Prix d'achat: {rendement['prix_achat_m2']}€/m²")
    print(f"Loyer mensuel: {rendement['loyer_mensuel_m2']:.2f}€/m²")
    print(f"Rendement brut: {rendement['rendement_brut_pct']:.2f}%")
    print(f"Fiable: {rendement['fiable']}")
```

## 📁 Résultats et Outputs

Après l'exécution, vous trouverez :

### Données de Loyers
- **Données brutes** : `data/raw/carte_loyers_2024.csv`
- **Données traitées** : `data/raw/carte_loyers_2024.parquet`
- **Rapport Excel** : `outputs/reports/analyse_loyers_idf_2024.xlsx`
  - Feuille 1: Données détaillées par commune
  - Feuille 2: Statistiques par département
  - Feuille 3: Top 20 loyers élevés
  - Feuille 4: Top 20 loyers bas

### Données DVF (Prix d'Achat)
- **Données brutes** : `data/raw/dvf_2023_XX.csv` (par département)
- **Données nettoyées** : `data/processed/dvf_2023_idf_clean.parquet`
- **Rapport Excel** : `outputs/reports/analyse_idf_2023.xlsx`

### Analyses Combinées
- **Rapport complet** : `outputs/reports/analyse_complete_idf_2024.xlsx`

## 📓 Exploration Interactive

Pour explorer les données avec Jupyter :

```bash
# Lancer Jupyter
jupyter notebook

# Ou directement le notebook d'exploration
jupyter notebook notebooks/exploration.ipynb
```

**Notebooks disponibles**:
- `exploration.ipynb`: Exploration générale des données
- À créer: `rent_analysis.ipynb`: Analyse approfondie des loyers
- À créer: `investment_opportunities.ipynb`: Identification des meilleures opportunités

## 📝 Exemples de Code Détaillés

### Exemple 1: Comparer les Loyers et Rendements

```python
from src.analysis.rent_analyzer import RentAnalyzer
from src.analysis.combined_analyzer import CombinedAnalyzer

# Analyser les loyers
rent_analyzer = RentAnalyzer(year=2024)

# Liste de villes à comparer
villes = ["Paris", "Versailles", "Saint-Denis", "Nanterre", "Montreuil"]

# Comparer les loyers
print("\n=== COMPARAISON DES LOYERS ===")
for ville in villes:
    stats = rent_analyzer.get_city_rent_stats(city_name=ville)
    if stats:
        print(f"{ville:20s}: {stats.loyer_moyen_m2:6.2f}€/m²/mois "
              f"(Annuel: {stats.loyer_moyen_m2 * 12:7.2f}€/m²) "
              f"- Fiable: {stats.is_reliable}")

# Calculer les rendements (avec prix fictifs)
combined = CombinedAnalyzer(dvf_year=2023, rent_year=2024)
prix_estimés = {
    "Paris": 10000,
    "Versailles": 5500,
    "Saint-Denis": 3500,
    "Nanterre": 4500,
    "Montreuil": 4000
}

print("\n=== RENDEMENTS LOCATIFS ESTIMÉS ===")
for ville, prix in prix_estimés.items():
    rendement = combined.calculate_rental_yield(
        city_name=ville, 
        prix_achat_m2=prix
    )
    if rendement:
        print(f"{ville:20s}: {rendement['rendement_brut_pct']:5.2f}% "
              f"(Prix: {prix:,}€/m², Loyer: {rendement['loyer_mensuel_m2']:.2f}€/m²)")
```

### Exemple 2: Analyser un Département

```python
from src.analysis.rent_analyzer import RentAnalyzer

analyzer = RentAnalyzer(year=2024)

# Statistiques pour les Hauts-de-Seine (92)
print("\n=== HAUTS-DE-SEINE (92) ===")

# Stats globales
dept_stats = analyzer.get_department_statistics("92")
print(dept_stats)

# Top 10 des villes
top10 = analyzer.get_top_cities(n=10, department_code="92", ascending=False)
print("\nTop 10 des loyers dans le 92:")
print(top10)
```

### Exemple 3: Export et Visualisation

```python
from src.analysis.rent_analyzer import RentAnalyzer
from pathlib import Path
import matplotlib.pyplot as plt

analyzer = RentAnalyzer(year=2024)

# Export vers Excel
output = Path("outputs/reports/loyers_idf_2024.xlsx")
analyzer.export_to_excel(output)
print(f"Rapport exporté: {output}")

# Créer un graphique de comparaison
villes = ["Paris", "Boulogne-Billancourt", "Neuilly-sur-Seine", 
          "Versailles", "Saint-Denis", "Créteil"]

loyers = []
noms = []

for ville in villes:
    stats = analyzer.get_city_rent_stats(city_name=ville)
    if stats:
        loyers.append(stats.loyer_moyen_m2)
        noms.append(ville)

# Graphique
plt.figure(figsize=(12, 6))
plt.bar(noms, loyers, color='steelblue')
plt.xlabel('Commune')
plt.ylabel('Loyer moyen (€/m²/mois)')
plt.title('Comparaison des loyers moyens en Île-de-France')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('outputs/visualizations/comparaison_loyers.png', dpi=300)
print("Graphique sauvegardé: outputs/visualizations/comparaison_loyers.png")
```

### Exemple 4: Estimation pour un Appartement

```python
from src.analysis.rent_analyzer import RentAnalyzer

analyzer = RentAnalyzer(year=2024)

# Paramètres de l'appartement
ville = "Versailles"
surface = 65  # m²

stats = analyzer.get_city_rent_stats(city_name=ville)

if stats and stats.is_reliable:
    loyer_mensuel = stats.loyer_moyen_m2 * surface
    loyer_bas = stats.loyer_bas_m2 * surface
    loyer_haut = stats.loyer_haut_m2 * surface
    loyer_annuel = loyer_mensuel * 12
    
    print(f"\n{'='*60}")
    print(f"ESTIMATION LOYER - {ville.upper()}")
    print(f"Appartement de {surface}m²")
    print(f"{'='*60}")
    print(f"Loyer mensuel moyen:  {loyer_mensuel:,.0f} €")
    print(f"Fourchette estimée:   {loyer_bas:,.0f} € - {loyer_haut:,.0f} €")
    print(f"Loyer annuel:         {loyer_annuel:,.0f} €")
    print(f"\nDonnées fiables: ✓ Oui")
    print(f"  - R² ajusté: {stats.r2_ajuste:.3f}")
    print(f"  - Observations: {stats.nb_observations_commune}")
    print(f"  - Type: {stats.type_prediction}")
else:
    print(f"Données non disponibles ou peu fiables pour {ville}")
```

## 🛠️ Outils Utiles

### Vérifier les URLs configurées

```bash
# Vérifie l'accessibilité de toutes les URLs
python scripts/check_urls.py
```

Ce script affiche:
- ✅ URLs accessibles et leur taille
- ❌ URLs obsolètes ou invalides
- 📊 Résumé de la configuration

### Exemples de scripts

```bash
# Téléchargement avec URLs custom
python examples/download_with_custom_urls.py

# Analyse complète des loyers
python examples/analyze_rents.py
```

## 🧪 Tests

Vérifier que tout fonctionne correctement:

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src tests/

# Tests du module loyers uniquement
pytest tests/test_rent_analyzer.py -v

# Tests des URLs custom
pytest tests/test_custom_urls.py -v
```

## ⚠️ Problèmes Courants

### Erreur: Fichier carte_loyers_2024.csv non trouvé

**Solution**:
1. Allez sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
2. Téléchargez le fichier CSV
3. Placez-le dans `data/raw/carte_loyers_2024.csv`

### Erreur: Commune non trouvée

**Solutions**:
- Vérifiez l'orthographe exacte (majuscules, tirets)
- Utilisez le code INSEE si vous le connaissez
- Vérifiez que la commune est en Île-de-France

### Données non fiables (is_reliable = False)

**Interprétation**:
- R² < 0.5 ou observations < 30
- Utilisez quand même les données mais avec prudence
- Consultez les communes voisines pour comparaison

## 📚 Besoin d'Aide ?

- 📖 **Guide complet du projet** : `.continue/rules/CONTINUE.md`
- 📖 **Guide d'analyse des loyers** : `docs/GUIDE_LOYERS.md`
- 📖 **Documentation technique** : `docs/RENT_MODULE_README.md`
- 🐛 **Dépannage** : Voir section 7 du guide CONTINUE.md
- 💬 **Questions** : Ouvrir une issue sur GitHub

## 🎯 Prochaines Étapes

1. ✅ Explorez le script d'exemple: `python examples/analyze_rents.py`
2. ✅ Consultez le guide des loyers: `docs/GUIDE_LOYERS.md`
3. ✅ Expérimentez avec vos propres analyses
4. ✅ Créez des visualisations personnalisées
5. ✅ Intégrez les données DVF pour calculs de rendements

## 📊 Résumé des Commandes

```bash
# Analyse rapide des loyers
python examples/analyze_rents.py

# Tests
pytest

# Linter le code
ruff check src/

# Formater le code
black src/
```

---

**Temps estimé total** : 
- ⏱️ Analyse loyers seuls: 5-10 minutes
- ⏱️ Avec DVF: 30-60 minutes (téléchargement inclus)

**Sources de données**:
- 🏠 Loyers: Carte des loyers 2024 (data.gouv.fr)
- 🏡 Prix d'achat: Base DVF 2014-2024 (data.gouv.fr)
