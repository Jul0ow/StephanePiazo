# Guide d'Utilisation - Analyse Combinée Ventes + Loyers

Ce guide explique comment utiliser le nouveau système d'analyse combinée qui intègre les données de ventes (DVF) et de loyers (Carte des loyers).

## Vue d'ensemble

L'analyse combinée vous permet d'obtenir un **résumé complet par ville** comprenant :

### 📊 Pour chaque ville :

#### Vente (Données DVF)
- **Prix bas** : Prix minimum au m² observé
- **Prix moyen** : Prix moyen au m²
- **Prix haut** : Prix maximum au m² observé
- Nombre de transactions
- Statistiques par type de bien (appartements/maisons)

#### Location (Carte des loyers)
- **Loyer bas** : Loyer minimum au m²/mois
- **Loyer moyen** : Loyer moyen au m²/mois
- **Loyer haut** : Loyer maximum au m²/mois
- Fiabilité de la prédiction
- Nombre d'observations

#### Rendement Locatif
- **Rendement brut** : (Loyer annuel / Prix d'achat) × 100
- Permet d'identifier les opportunités d'investissement

---

## 🚀 Utilisation avec main.py

### Pipeline complet (recommandé)

Exécute toutes les étapes automatiquement :

```bash
python main.py --year 2023 --rent-year 2024 --full-pipeline
```

**Ce que fait cette commande :**
1. Télécharge les données DVF (ventes) pour 2023
2. Télécharge les données de loyers pour 2024
3. Nettoie les données DVF
4. Génère l'analyse combinée complète
5. Crée un fichier Excel avec tous les résultats

### Étapes individuelles

Si vous voulez contrôler chaque étape :

```bash
# 1. Télécharger les données de ventes
python main.py --year 2023 --download

# 2. Télécharger les données de loyers
python main.py --rent-year 2024 --download-rent

# 3. Nettoyer les données DVF
python main.py --year 2023 --clean

# 4. Lancer l'analyse combinée
python main.py --year 2023 --rent-year 2024 --analyze-combined
```

### Analyses séparées

```bash
# Analyser uniquement les ventes
python main.py --year 2023 --analyze

# Analyser uniquement les loyers
python main.py --rent-year 2024 --analyze-rent
```

---

## 📋 Format des résultats

### Fichier Excel généré

Le fichier `outputs/reports/analyse_complete_idf_2023_2024.xlsx` contient :

#### 📑 Feuille 1 : "Résumé complet"
Villes avec données complètes (vente + location), triées par rendement locatif.

| Colonne | Description |
|---------|-------------|
| `ville` | Nom de la commune |
| `code_insee` | Code INSEE |
| `departement` | Code département (75, 77, 78, 91, 92, 93, 94, 95) |
| `prix_vente_moyen_m2` | Prix de vente moyen (€/m²) |
| `prix_vente_bas_m2` | Prix de vente minimum (€/m²) |
| `prix_vente_haut_m2` | Prix de vente maximum (€/m²) |
| `loyer_moyen_m2` | Loyer moyen (€/m²/mois) |
| `loyer_bas_m2` | Loyer minimum (€/m²/mois) |
| `loyer_haut_m2` | Loyer maximum (€/m²/mois) |
| `rendement_brut_pct` | Rendement locatif brut (%) |
| `nb_transactions` | Nombre de transactions de vente |
| `loyer_fiable` | Fiabilité des données de loyer |

#### 📑 Feuille 2 : "Toutes les données"
Toutes les villes, même avec données partielles.

#### 📑 Feuille 3 : "Stats par département"
Statistiques agrégées par département.

---

## 💻 Utilisation en Python

### Exemple 1 : Résumé pour une ville

```python
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.rent_analyzer import RentAnalyzer

# Charger les analyseurs
price_analyzer = PriceAnalyzer()
price_analyzer.load_data(year=2023)

rent_analyzer = RentAnalyzer(year=2024)

# Obtenir les statistiques
city_name = "Paris"

# Ventes
vente_stats = price_analyzer.get_city_stats(city_name)
print(f"Prix de vente moyen: {vente_stats.prix_moyen_m2:.0f}€/m²")
print(f"Prix bas: {vente_stats.prix_min_m2:.0f}€/m²")
print(f"Prix haut: {vente_stats.prix_max_m2:.0f}€/m²")

# Loyers
loyer_stats = rent_analyzer.get_city_rent_stats(city_name=city_name)
print(f"Loyer moyen: {loyer_stats.loyer_moyen_m2:.2f}€/m²/mois")
print(f"Loyer bas: {loyer_stats.loyer_bas_m2:.2f}€/m²/mois")
print(f"Loyer haut: {loyer_stats.loyer_haut_m2:.2f}€/m²/mois")

# Rendement
if vente_stats and loyer_stats:
    loyer_annuel = loyer_stats.loyer_moyen_m2 * 12
    rendement = (loyer_annuel / vente_stats.prix_moyen_m2) * 100
    print(f"Rendement brut: {rendement:.2f}%")
```

### Exemple 2 : Utiliser l'analyseur combiné

```python
from src.analysis.combined_analyzer import CombinedAnalyzer

# Créer l'analyseur
analyzer = CombinedAnalyzer(dvf_year=2023, rent_year=2024)

# Obtenir les stats complètes pour une ville
stats = analyzer.get_city_complete_stats(city_name="Paris")
print(stats)

# Calculer le rendement locatif
rendement = analyzer.calculate_rental_yield(
    city_name="Paris",
    prix_achat_m2=10000  # ou None pour utiliser les données DVF
)
print(f"Rendement: {rendement['rendement_brut_pct']:.2f}%")

# Comparer plusieurs villes
cities = ["Paris", "Versailles", "Saint-Denis", "Créteil"]
comparison = analyzer.create_comparison_report(cities)
print(comparison)

# Exporter tout
analyzer.export_combined_data()
```

### Exemple 3 : Script complet de démonstration

Un script d'exemple complet est disponible :

```bash
python examples/combined_analysis_example.py
```

Ce script montre :
- Comment afficher un résumé détaillé pour une ville
- Comment comparer plusieurs villes
- Comment exporter l'analyse d'un département

---

## 📊 Interprétation des résultats

### Prix de vente (€/m²)
- **Prix bas** : Généralement biens anciens ou mal situés
- **Prix moyen** : Référence du marché
- **Prix haut** : Biens premium ou très bien situés

### Loyers (€/m²/mois)
- **Loyer bas** : Minimum attendu pour la zone
- **Loyer moyen** : Loyer de marché
- **Loyer haut** : Maximum pour biens de qualité

### Rendement locatif brut
- **< 3%** : Rendement faible (mais zone recherchée)
- **3-5%** : Rendement moyen en Île-de-France
- **5-7%** : Bon rendement
- **> 7%** : Excellent rendement (vérifier les risques)

⚠️ **Important** : Le rendement brut ne prend pas en compte :
- Les charges de copropriété
- Les taxes (taxe foncière)
- Les frais d'entretien
- Les périodes de vacance locative
- Les frais de gestion

Le rendement **net** est généralement 30-40% inférieur au rendement brut.

---

## 🔍 Cas d'usage

### 1. Investisseur locatif
Identifier les villes avec le meilleur rendement :

```bash
python main.py --year 2023 --rent-year 2024 --analyze-combined
```

Puis consulter la feuille "Résumé complet" triée par rendement.

### 2. Propriétaire bailleur
Estimer le loyer de marché pour votre ville :

```python
from src.analysis.rent_analyzer import RentAnalyzer

analyzer = RentAnalyzer(year=2024)
stats = analyzer.get_city_rent_stats(city_name="Versailles")
print(f"Loyer de marché: {stats.loyer_moyen_m2:.2f}€/m²/mois")
print(f"Fourchette: {stats.loyer_bas_m2:.2f} - {stats.loyer_haut_m2:.2f}€/m²/mois")
```

### 3. Analyse de marché
Comparer plusieurs zones :

```python
from examples.combined_analysis_example import compare_multiple_cities

cities = ["Paris", "Neuilly-sur-Seine", "Levallois-Perret", "Boulogne-Billancourt"]
compare_multiple_cities(cities)
```

### 4. Étude départementale
Analyser tout un département :

```python
from examples.combined_analysis_example import export_department_analysis

# Hauts-de-Seine (92)
export_department_analysis("92")
```

---

## ⚙️ Configuration

### Années de données

Par défaut :
- DVF (ventes) : 2023
- Loyers : 2024

Pour changer :

```bash
python main.py --year 2022 --rent-year 2023 --full-pipeline
```

### Filtrage par département

Dans vos scripts Python :

```python
# Filtrer un département spécifique
analyzer = RentAnalyzer(year=2024)
dept_stats = analyzer.get_department_statistics("75")  # Paris
```

---

## 🐛 Dépannage

### Erreur : "Données DVF non trouvées"
**Solution** : Téléchargez d'abord les données :
```bash
python main.py --year 2023 --download
python main.py --year 2023 --clean
```

### Erreur : "Données de loyers non trouvées"
**Solution** : Téléchargez les loyers :
```bash
python main.py --rent-year 2024 --download-rent
```

### Ville non trouvée
**Causes possibles** :
1. Nom de ville mal orthographié (vérifier les majuscules)
2. Ville non couverte par les données
3. Pas de transactions récentes dans cette ville

**Solution** : Vérifiez le nom exact :
```python
analyzer = RentAnalyzer(year=2024)
data = analyzer.load_idf_data()
print(data["LIBGEO"].unique())  # Liste toutes les villes
```

### Rendement aberrant
Si le rendement semble trop élevé ou trop bas, vérifiez :
- Le nombre de transactions (colonne `nb_transactions`)
- La fiabilité des loyers (colonne `loyer_fiable`)
- Comparez avec les villes voisines

---

## 📚 Ressources complémentaires

- [Guide de démarrage rapide](../QUICKSTART.md)
- [Documentation complète](../.continue/rules/CONTINUE.md)
- [Exemples de code](../examples/)
- [Configuration des URLs](./CUSTOM_URLS.md)

---

## 🤝 Contribution

Pour ajouter de nouvelles fonctionnalités à l'analyse combinée, consultez le fichier `src/analysis/combined_analyzer.py`.

Suggestions bienvenues :
- Calcul du rendement net
- Analyse temporelle (évolution des prix)
- Prédictions avec ML
- Visualisations graphiques

---

**Dernière mise à jour** : 2025-01-02
**Version** : 1.0.0
