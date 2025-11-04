"""
Fichier de configuration des URLs personnalisées.

Ce fichier permet de définir des URLs personnalisées pour le téléchargement
des données DVF et de la Carte des loyers sans modifier le code source.

INSTRUCTIONS:
1. Copiez ce fichier en 'config_urls.py'
2. Modifiez les URLs selon vos besoins
3. Le fichier config_urls.py sera automatiquement ignoré par git (.gitignore)

UTILISATION:
- Les URLs définies ici ont la priorité sur celles du fichier config.py
- Vous pouvez définir des URLs pour toutes les années ou seulement certaines
"""

# =============================================================================
# CONFIGURATION DVF (Demandes de Valeurs Foncières)
# =============================================================================

# URLs personnalisées pour les données DVF
# Format 1: URL template avec {dept} pour remplacer le code département
# Format 2: Dictionnaire {code_dept: url} pour des URLs spécifiques
DVF_CUSTOM_URLS = {
    # Exemple avec template (l'URL sera formatée avec le code département)
    # 2023: "https://mon-serveur.com/dvf/2023/{dept}.csv.gz",
    
    # Exemple avec dictionnaire (URLs spécifiques par département)
    # 2024: {
    #     "75": "https://mon-serveur.com/dvf/paris_2024.csv.gz",
    #     "92": "https://mon-serveur.com/dvf/hauts_de_seine_2024.csv.gz",
    # },
}

# =============================================================================
# CONFIGURATION CARTE DES LOYERS
# =============================================================================

# URLs personnalisées pour la Carte des loyers
# Ces URLs remplaceront celles définies par défaut dans config.py
RENT_CUSTOM_URLS = {
    # Exemple pour 2024:
    # 2024: "https://static.data.gouv.fr/resources/carte-des-loyers/20241001-093315/indicateurs-loyers-par-commune.csv",
    
    # Exemple pour 2025 (quand disponible):
    # 2025: "https://static.data.gouv.fr/resources/carte-des-loyers/nouvelle-url.csv",
}

# =============================================================================
# NOTES
# =============================================================================

# Où trouver les URLs des données ?
# ----------------------------------
# 
# DVF (Demandes de Valeurs Foncières):
# - Site: https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/
# - API: https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/{dept}.csv.gz
# - Exemple: https://files.data.gouv.fr/geo-dvf/latest/csv/2023/departements/75.csv.gz
#
# Carte des loyers:
# - Site: https://www.data.gouv.fr/fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2024/
# - Cliquez sur le fichier CSV puis "Télécharger" pour copier l'URL
#
# Codes départements Île-de-France:
# - 75: Paris
# - 77: Seine-et-Marne
# - 78: Yvelines
# - 91: Essonne
# - 92: Hauts-de-Seine
# - 93: Seine-Saint-Denis
# - 94: Val-de-Marne
# - 95: Val-d'Oise
