# Statistiques Immobilières Île-de-France

Projet Python pour analyser les prix immobiliers en Île-de-France à partir des données DVF (Demandes de Valeurs Foncières).

## 🎯 Objectif

Extraire et analyser les prix d'achat au mètre carré (moyen, haut, bas) pour les villes d'Île-de-France en utilisant la base de données ouverte DVF du gouvernement français.

## 🚀 Démarrage Rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Télécharger les données DVF pour 2023
python -m src.data.dvf_downloader --year 2023

# Analyser les prix pour une ville
python -m src.analysis.price_analyzer --city "Paris"
```

## 📊 Fonctionnalités

- ✅ Téléchargement automatique des données DVF
- ✅ Calcul des prix min/max/moyen au m²
- ✅ Statistiques par ville et département
- ✅ Export des résultats (CSV, Excel)
- 🚧 Visualisations interactives (à venir)
- 🚧 Prédictions ML (à venir)

## 📚 Documentation

Consultez le [Guide Complet du Projet](.continue/rules/CONTINUE.md) pour:
- Architecture détaillée
- Guide de développement
- Tâches courantes
- Dépannage

## 🛠️ Stack Technique

- Python 3.9+
- pandas & numpy
- requests
- matplotlib & seaborn
- pytest

## 📦 Structure

```
src/
├── data/          # Téléchargement et nettoyage des données
├── analysis/      # Analyses statistiques
├── models/        # Modèles de données
└── utils/         # Utilitaires
```

## 📄 License

MIT License - voir [LICENSE](LICENSE)

## 👨‍💻 Auteur

Jules Diaz
