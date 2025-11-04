# 📡 Configuration des URLs Personnalisées

Ce guide explique comment configurer des URLs personnalisées pour télécharger les données DVF et de la Carte des loyers.

## 🎯 Pourquoi utiliser des URLs personnalisées ?

- **URLs changeantes**: Les URLs officielles peuvent changer sur data.gouv.fr
- **Serveur miroir**: Utiliser vos propres serveurs ou miroirs alternatifs
- **Données archivées**: Accéder à des versions spécifiques des données
- **Performance**: Utiliser des serveurs plus rapides ou géographiquement proches
- **Environnement déconnecté**: Travailler avec des données locales

---

## 🚀 Méthode 1: Fichier de Configuration (Recommandé)

### Étape 1: Créer le fichier de configuration

```bash
# Copier le fichier d'exemple
cp config_urls.example.py config_urls.py
```

### Étape 2: Éditer config_urls.py

```python
# config_urls.py

# URLs pour la Carte des loyers
RENT_CUSTOM_URLS = {
    2024: "https://static.data.gouv.fr/resources/carte-des-loyers/votre-url.csv",
    2025: "https://static.data.gouv.fr/resources/carte-des-loyers/votre-url-2025.csv",
}

# URLs pour les données DVF
# Format 1: Template avec {dept}
DVF_CUSTOM_URLS = {
    2023: "https://votre-serveur.com/dvf/2023/{dept}.csv.gz",
}

# Format 2: URLs spécifiques par département
DVF_CUSTOM_URLS = {
    2024: {
        "75": "https://votre-serveur.com/paris_2024.csv.gz",
        "92": "https://votre-serveur.com/hauts_de_seine_2024.csv.gz",
    }
}
```

### Étape 3: Utiliser normalement

```python
from src.data.rent_downloader import RentDownloader
from src.data.dvf_downloader import DVFDownloader

# Les URLs custom sont automatiquement chargées
downloader = RentDownloader()
downloader.download_rent_data(year=2024)  # Utilise l'URL custom

dvf_downloader = DVFDownloader()
dvf_downloader.download_idf_data(year=2023)  # Utilise les URLs custom
```

---

## 💡 Méthode 2: URLs Inline (Pour tests ponctuels)

### Carte des loyers

```python
from src.data.rent_downloader import RentDownloader

downloader = RentDownloader()

# Passer l'URL directement
custom_url = "https://static.data.gouv.fr/resources/carte-des-loyers/fichier.csv"
downloader.download_rent_data(year=2024, custom_url=custom_url)
```

### Données DVF

```python
from src.data.dvf_downloader import DVFDownloader

downloader = DVFDownloader()

# Pour un département spécifique
url = "https://votre-serveur.com/dvf/75.csv.gz"
downloader.download_department_data(
    department="75",
    year=2023,
    custom_url=url
)

# Pour tous les départements IDF
custom_urls = {
    "75": "https://serveur.com/paris.csv.gz",
    "92": "https://serveur.com/hauts_de_seine.csv.gz",
    # ... autres départements
}
downloader.download_idf_data(year=2023, custom_urls=custom_urls)
```

---

## 🔍 Comment trouver les bonnes URLs ?

### Pour la Carte des loyers

1. Aller sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/)
2. Cliquer sur le fichier CSV souhaité
3. Clic droit sur "Télécharger" → "Copier l'adresse du lien"
4. Coller l'URL dans votre configuration

**Exemple d'URL valide (2024):**
```
https://static.data.gouv.fr/resources/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/20241001-093315/indicateurs-loyers-par-commune.csv
```

### Pour les données DVF

1. Aller sur [data.gouv.fr DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)
2. Naviguer vers les fichiers par département
3. Structure de l'URL officielle:
   ```
   https://files.data.gouv.fr/geo-dvf/latest/csv/{ANNÉE}/departements/{DEPT}.csv.gz
   ```

**Exemples d'URLs valides:**
```
# Paris 2023
https://files.data.gouv.fr/geo-dvf/latest/csv/2023/departements/75.csv.gz

# Hauts-de-Seine 2024
https://files.data.gouv.fr/geo-dvf/latest/csv/2024/departements/92.csv.gz
```

---

## 📋 Exemples d'Usage

### Exemple 1: Configuration mixte

```python
# config_urls.py

# Loyers: utiliser une URL custom pour 2024
RENT_CUSTOM_URLS = {
    2024: "https://mon-serveur.com/loyers_2024.csv",
}

# DVF: utiliser template pour tous les départements en 2023
DVF_CUSTOM_URLS = {
    2023: "https://mon-serveur.com/dvf/{dept}.csv.gz",
}
```

### Exemple 2: Serveur local

```python
# config_urls.py

# Utiliser des fichiers sur un serveur réseau local
RENT_CUSTOM_URLS = {
    2024: "http://192.168.1.100:8000/data/loyers_2024.csv",
}

DVF_CUSTOM_URLS = {
    2023: "http://192.168.1.100:8000/data/dvf/{dept}.csv.gz",
}
```

### Exemple 3: URLs spécifiques par département

```python
# config_urls.py

# Différentes sources pour différents départements
DVF_CUSTOM_URLS = {
    2023: {
        "75": "https://serveur-paris.com/dvf_2023.csv.gz",
        "92": "https://serveur-hauts-de-seine.com/dvf_2023.csv.gz",
        "93": "https://serveur-seine-saint-denis.com/dvf_2023.csv.gz",
        # Les autres départements utiliseront l'URL par défaut
    }
}
```

---

## 🔧 Ordre de Priorité des URLs

Le système charge les URLs dans cet ordre (du plus prioritaire au moins prioritaire):

1. **URL passée en paramètre** (`custom_url=...`)
2. **config_urls.py** (votre fichier de configuration locale)
3. **src/utils/config.py** (URLs par défaut du projet)

```python
# Exemple de priorité
downloader = RentDownloader()

# 1. Cette URL sera utilisée (priorité maximale)
downloader.download_rent_data(
    year=2024,
    custom_url="https://url-directe.com/loyers.csv"
)

# 2. Si custom_url n'est pas fourni, utilise config_urls.py
downloader.download_rent_data(year=2024)

# 3. Si config_urls.py n'existe pas ou ne contient pas l'année,
#    utilise l'URL par défaut de config.py
```

---

## ⚠️ Bonnes Pratiques

### ✅ À FAIRE

- **Versionner config_urls.example.py** (template)
- **Documenter les URLs** dans des commentaires
- **Tester les URLs** avant de les mettre en production
- **Utiliser HTTPS** quand c'est possible
- **Vérifier régulièrement** que les URLs sont toujours valides

### ❌ À NE PAS FAIRE

- **Ne PAS commiter config_urls.py** (déjà dans .gitignore)
- **Ne PAS mettre de credentials** dans les URLs (utiliser des variables d'environnement)
- **Ne PAS hardcoder** les URLs dans le code métier
- **Ne PAS oublier** de mettre à jour les URLs quand elles changent

---

## 🧪 Tester votre Configuration

```python
# test_custom_urls.py

from src.utils.config import DVF_CUSTOM_URLS, RENT_CUSTOM_URLS

print("🔍 Vérification de la configuration des URLs\n")

print("📊 DVF Custom URLs:")
if DVF_CUSTOM_URLS:
    for year, urls in DVF_CUSTOM_URLS.items():
        print(f"  Année {year}: {urls}")
else:
    print("  Aucune URL custom configurée")

print("\n🏠 Rent Custom URLs:")
if RENT_CUSTOM_URLS:
    for year, url in RENT_CUSTOM_URLS.items():
        print(f"  Année {year}: {url}")
else:
    print("  Aucune URL custom configurée")
```

---

## 🐛 Dépannage

### Erreur: "Aucune URL configurée pour l'année..."

**Cause**: L'année demandée n'est pas configurée

**Solution**:
```python
# Ajouter dans config_urls.py
RENT_CUSTOM_URLS = {
    2024: "https://votre-url.csv",
}
```

### Erreur: "Erreur téléchargement..."

**Causes possibles**:
- URL invalide ou changée
- Serveur inaccessible
- Problème de connexion internet

**Solutions**:
1. Vérifier que l'URL est correcte dans un navigateur
2. Tester avec `curl` ou `wget`:
   ```bash
   curl -I "https://votre-url.csv"
   ```
3. Vérifier les logs pour le message d'erreur exact

### Configuration non chargée

**Cause**: Le fichier config_urls.py contient des erreurs de syntaxe

**Solution**:
```bash
# Vérifier la syntaxe Python
python -m py_compile config_urls.py
```

---

## 📚 Ressources

- [Documentation data.gouv.fr](https://doc.data.gouv.fr/)
- [API DVF](https://app.dvf.etalab.gouv.fr/)
- [Carte des loyers](https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/)
- [Codes départements](https://fr.wikipedia.org/wiki/D%C3%A9partement_fran%C3%A7ais)

---

## 💬 Support

Si vous rencontrez des problèmes:

1. Vérifiez que les URLs sont valides
2. Consultez les logs d'erreur
3. Exécutez le script d'exemple: `python examples/download_with_custom_urls.py`
4. Ouvrez une issue sur GitHub avec:
   - L'URL utilisée (anonymisée si nécessaire)
   - Le message d'erreur complet
   - La version Python utilisée
