# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [Unreleased]

### ✨ Ajouté

#### Système d'URLs Personnalisées
- **Configuration externe via `config_urls.py`**: Nouveau système de configuration pour URLs custom
  - Fichier `config_urls.example.py` fourni comme template
  - Chargement automatique au démarrage du module
  - Fichier `config_urls.py` automatiquement ignoré par git (.gitignore)

- **Support des URLs custom dans `rent_downloader.py`**:
  - Nouveau paramètre `custom_url` dans `download_rent_data()`
  - Nouveau paramètre `force` pour forcer le re-téléchargement
  - Système de priorité: URL inline > config_urls.py > config.py
  - Gestion d'erreur améliorée avec messages explicites

- **Support des URLs custom dans `dvf_downloader.py`**:
  - Nouveau paramètre `custom_url` dans `download_department_data()`
  - Nouveau paramètre `custom_urls` (dict) dans `download_idf_data()`
  - Support de templates d'URL avec placeholder `{dept}`
  - Support de dictionnaires d'URLs par département

- **Configuration centralisée dans `config.py`**:
  - `DVF_CUSTOM_URLS`: Dict pour URLs DVF personnalisées
  - `RENT_CUSTOM_URLS`: Dict pour URLs de loyers personnalisées
  - Fonction `_load_custom_config()`: Charge automatiquement config_urls.py
  - Logs de confirmation lors du chargement des URLs custom

#### Documentation
- **`docs/CUSTOM_URLS.md`**: Guide complet pour les URLs personnalisées
  - Méthode de configuration via fichier (recommandée)
  - Méthode inline pour tests ponctuels
  - Comment trouver les bonnes URLs (data.gouv.fr)
  - Exemples pratiques pour tous les cas d'usage
  - Ordre de priorité des URLs
  - Bonnes pratiques et pièges à éviter
  - Guide de dépannage

- **`examples/download_with_custom_urls.py`**: 5 exemples pratiques
  - Téléchargement de loyers avec URL custom
  - Téléchargement DVF avec URLs par département
  - Utilisation du fichier config_urls.py
  - Vérification des URLs configurées
  - Téléchargement complet IDF avec config custom

#### Outils
- **`scripts/check_urls.py`**: Script de vérification des URLs
  - Vérifie l'accessibilité de toutes les URLs configurées
  - Affiche la taille des fichiers
  - Détecte les URLs obsolètes ou invalides
  - Interface CLI colorée avec `rich`
  - Résumé de la configuration active

#### Tests
- **`tests/test_custom_urls.py`**: Suite complète de tests (20+ tests)
  - Tests du système d'URLs custom pour loyers
  - Tests du système d'URLs custom pour DVF
  - Tests de chargement du fichier config_urls.py
  - Tests de priorité des URLs
  - Tests de validation des URLs
  - Couverture complète avec mocks

### 📝 Modifié

- **`README.md`**:
  - Nouvelle section "Configuration des URLs"
  - Lien vers la documentation CUSTOM_URLS.md
  - Mention du script check_urls.py dans les exemples

- **`.gitignore`**:
  - Ajout de `config_urls.py` (fichier de configuration locale)

- **`requirements.txt`**:
  - Ajout de `rich>=13.0.0` pour le script de vérification

### 🔧 Technique

- Système de priorité à 3 niveaux pour les URLs:
  1. URL passée en paramètre (priorité maximale)
  2. config_urls.py (configuration locale)
  3. config.py (configuration par défaut)

- Chargement dynamique de modules Python avec `importlib`
- Support de templates d'URL avec `str.format()`
- Gestion robuste des erreurs avec logs explicites

### 💡 Cas d'Usage

- **URLs changeantes**: S'adapter aux changements d'URLs sur data.gouv.fr
- **Serveurs miroirs**: Utiliser des serveurs alternatifs plus rapides
- **Données archivées**: Accéder à des versions spécifiques
- **Environnement déconnecté**: Travailler avec des données sur réseau local
- **Tests**: Utiliser des données de test sans modifier le code

---

## [0.2.0] - 2025-01-02

### ✨ Ajouté

#### Module d'Analyse des Loyers
- **`src/data/rent_downloader.py`**: Nouveau module pour télécharger les données de la Carte des loyers
  - Téléchargement depuis data.gouv.fr
  - Support pour téléchargement manuel et automatique
  - Filtrage automatique pour l'Île-de-France
  - Sauvegarde en format Parquet optimisé

- **`src/analysis/rent_analyzer.py`**: Analyseur complet de loyers
  - `get_city_rent_stats()`: Récupération des stats par commune (nom ou code INSEE)
  - `compare_cities()`: Comparaison de loyers entre plusieurs villes
  - `get_top_cities()`: Classement des loyers (plus élevés/bas)
  - `get_department_statistics()`: Statistiques agrégées par département
  - `get_idf_statistics()`: Vue d'ensemble de l'Île-de-France
  - `export_to_excel()`: Export multi-feuilles vers Excel

- **`src/analysis/combined_analyzer.py`**: Analyseur combiné DVF + Loyers
  - `calculate_rental_yield()`: Calcul du rendement locatif brut
  - `get_best_rental_yield_cities()`: Identification des meilleures opportunités
  - `create_comparison_report()`: Rapports de comparaison complets
  - `export_combined_data()`: Export des analyses combinées

#### Modèles de Données
- **`RentStats`** dans `src/models/city.py`: Nouveau modèle pour les statistiques de loyers
  - `loyer_moyen_m2`, `loyer_bas_m2`, `loyer_haut_m2`
  - `type_prediction`: "Commune", "epci" ou "maile"
  - `nb_observations_commune`, `nb_observations_maille`
  - `r2_ajuste`: Coefficient de détermination
  - Propriété `is_reliable`: Indicateur de fiabilité automatique

- **Extension de `CityStats`**: Ajout de l'attribut `loyers: Optional[RentStats]`

#### Configuration
- Nouvelles constantes dans `src/utils/config.py`:
  - `RENT_DATA_BASE_URL`: URL base pour la Carte des loyers
  - `RENT_YEARS_AVAILABLE`: Années disponibles
  - `MIN_RENT_M2`, `MAX_RENT_M2`: Seuils de filtrage
  - `MIN_R2_THRESHOLD`, `MIN_OBSERVATIONS`: Critères de fiabilité

#### Documentation
- **`docs/GUIDE_LOYERS.md`**: Guide complet d'utilisation du module loyers
  - Démarrage rapide
  - Analyses avancées
  - Calcul de rendement locatif
  - Exemples pratiques détaillés
  - Limites et précautions d'usage
  
- **`docs/RENT_MODULE_README.md`**: Documentation technique du module
  - Architecture et classes principales
  - API complète de chaque module
  - Schéma de données
  - Flux de données
  - Guide d'extensibilité
  - Maintenance

#### Exemples
- **`examples/analyze_rents.py`**: Script complet d'analyse des loyers
  - Analyse d'une ville spécifique (Paris)
  - Statistiques par département
  - Top 15 loyers élevés/bas
  - Comparaison de villes
  - Calcul de rendement locatif
  - Export vers Excel

#### Tests
- **`tests/test_rent_analyzer.py`**: Suite de tests complète
  - Tests de `RentAnalyzer`: 15+ tests
  - Tests de `RentStats`: 7+ tests
  - Couverture des cas d'erreur
  - Mocks pour tests sans données réelles

### 📝 Modifié

- **`README.md`**: 
  - Ajout de la section "Analyse des Loyers"
  - Nouveaux exemples de code
  - Structure du projet mise à jour
  - Stack technique étendu

- **`QUICKSTART.md`**: 
  - Nouvelle section dédiée aux loyers
  - Exemples de code étendus (4 exemples détaillés)
  - Guide de dépannage enrichi
  - Commandes de test et linting

- **`.continue/rules/CONTINUE.md`**:
  - Documentation du nouveau module loyers
  - Flux de données mis à jour
  - Références aux nouveaux guides

### 🔧 Technique

- Ajout du support pour les intervalles de prédiction (loyer bas/haut)
- Implémentation de la validation de fiabilité des données
- Optimisation du chargement avec cache interne
- Support du format Parquet pour performances accrues

### 📊 Sources de Données

- **Nouvelle source**: Carte des loyers 2024 (data.gouv.fr)
  - Indicateurs de loyers d'annonce par commune
  - Données basées sur leboncoin et Groupe SeLoger (2018-2024)
  - Loyers charges comprises, biens non meublés
  - Mise à jour T3 2024

---

## [0.1.0] - 2024-12-XX

### ✨ Ajouté

#### Fonctionnalités de Base
- Module de téléchargement des données DVF
- Analyseur de prix d'achat au m²
- Modèles de données (`City`, `CityStats`, `PropertyTypeStats`)
- Configuration centralisée
- Structure de projet complète

#### Documentation
- README principal
- Guide QUICKSTART
- Guide complet du projet (CONTINUE.md)

#### Tests
- Tests unitaires pour DVF downloader
- Tests pour price analyzer
- Configuration pytest

### 🛠️ Infrastructure

- Configuration Git et .gitignore
- Structure des dossiers (data/, outputs/, tests/)
- Requirements.txt avec dépendances de base
- Licence MIT

---

## Types de Changements

- **✨ Ajouté**: Nouvelles fonctionnalités
- **📝 Modifié**: Changements de fonctionnalités existantes
- **🗑️ Supprimé**: Fonctionnalités retirées
- **🐛 Corrigé**: Corrections de bugs
- **🔒 Sécurité**: Corrections de vulnérabilités
- **📚 Documentation**: Ajouts ou modifications de documentation
- **🔧 Technique**: Changements techniques sans impact utilisateur
- **⚡ Performance**: Améliorations de performance

---

## Roadmap (Prochaines Versions)

### [0.3.0] - Prévu Q1 2025
- 📊 Visualisations cartographiques interactives
- 📈 Graphiques d'évolution temporelle des prix
- 🔍 Recherche avancée avec filtres multiples
- 💾 Base de données SQLite pour performance

### [0.4.0] - Prévu Q2 2025
- 🤖 Modèles ML pour prédiction de prix
- 📧 Système d'alertes pour opportunités
- 🌐 API REST pour accès programmatique
- 📱 Dashboard web interactif

### [0.5.0] - Prévu Q3 2025
- 🗺️ Extension à d'autres régions françaises
- 📊 Analyse comparative inter-régions
- 💡 Recommandations d'investissement personnalisées
- 📝 Rapports PDF automatisés

---

**Note**: Les dates de roadmap sont indicatives et peuvent être ajustées.
