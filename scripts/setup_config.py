#!/usr/bin/env python
"""
Script d'aide à la configuration initiale du projet.

Ce script aide à:
- Créer le fichier config_urls.py à partir de l'exemple
- Tester les URLs par défaut
- Guider l'utilisateur pour configurer des URLs personnalisées
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.prompt import Confirm, Prompt
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠ Le package 'rich' n'est pas installé.")
    print("Installation: pip install rich")

console = Console() if RICH_AVAILABLE else None


def print_message(message: str, style: str = ""):
    """Affiche un message (avec ou sans rich)."""
    if RICH_AVAILABLE and console:
        console.print(message, style=style)
    else:
        print(message)


def check_config_file_exists() -> bool:
    """Vérifie si config_urls.py existe."""
    config_file = Path(__file__).parent.parent / "config_urls.py"
    return config_file.exists()


def create_config_from_template() -> bool:
    """Crée config_urls.py à partir du template."""
    project_root = Path(__file__).parent.parent
    example_file = project_root / "config_urls.example.py"
    config_file = project_root / "config_urls.py"
    
    if not example_file.exists():
        print_message("❌ Fichier config_urls.example.py introuvable!", "red")
        return False
    
    try:
        # Copier le fichier exemple
        config_file.write_text(example_file.read_text())
        print_message(f"✓ Fichier créé: {config_file}", "green")
        return True
    except Exception as e:
        print_message(f"❌ Erreur lors de la création: {e}", "red")
        return False


def show_url_finding_guide():
    """Affiche un guide pour trouver les URLs."""
    if RICH_AVAILABLE and console:
        console.print("\n[bold cyan]📍 Comment trouver les bonnes URLs[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Source", style="cyan", width=20)
        table.add_column("Étapes", overflow="fold")
        
        table.add_row(
            "Carte des loyers",
            "1. Allez sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-*\n"
            "2. Cliquez sur le fichier CSV souhaité\n"
            "3. Clic droit sur 'Télécharger' → 'Copier l'adresse du lien'\n"
            "4. Collez l'URL dans RENT_CUSTOM_URLS"
        )
        
        table.add_row(
            "DVF (achat)",
            "1. Allez sur https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/\n"
            "2. Structure: https://files.data.gouv.fr/geo-dvf/latest/csv/{ANNÉE}/departements/{DEPT}.csv.gz\n"
            "3. Exemple: .../2023/departements/75.csv.gz pour Paris 2023\n"
            "4. Utilisez {dept} comme placeholder pour le template"
        )
        
        console.print(table)
    else:
        print("\n📍 Comment trouver les bonnes URLs\n")
        print("CARTE DES LOYERS:")
        print("  1. Allez sur https://www.data.gouv.fr/fr/datasets/carte-des-loyers-*")
        print("  2. Cliquez sur le fichier CSV souhaité")
        print("  3. Clic droit sur 'Télécharger' → 'Copier l'adresse du lien'")
        print("  4. Collez l'URL dans RENT_CUSTOM_URLS\n")
        print("DVF (ACHAT):")
        print("  1. Structure: https://files.data.gouv.fr/geo-dvf/latest/csv/{ANNÉE}/departements/{DEPT}.csv.gz")
        print("  2. Exemple: .../2023/departements/75.csv.gz pour Paris 2023")
        print("  3. Utilisez {dept} comme placeholder pour le template\n")


def add_custom_url_interactive():
    """Mode interactif pour ajouter une URL custom."""
    if not RICH_AVAILABLE:
        print("\n⚠ Mode interactif nécessite 'rich'. Éditez config_urls.py manuellement.")
        return
    
    console.print("\n[bold cyan]➕ Ajout d'une URL personnalisée[/bold cyan]\n")
    
    # Demander le type de donnée
    data_type = Prompt.ask(
        "Type de donnée",
        choices=["loyers", "dvf"],
        default="loyers"
    )
    
    # Demander l'année
    year = Prompt.ask("Année", default="2024")
    
    # Demander l'URL
    url = Prompt.ask("URL complète")
    
    # Afficher le code à ajouter
    console.print("\n[yellow]Ajoutez ce code dans config_urls.py:[/yellow]\n")
    
    if data_type == "loyers":
        code = f"""
RENT_CUSTOM_URLS = {{
    {year}: "{url}",
}}
"""
    else:
        code = f"""
DVF_CUSTOM_URLS = {{
    {year}: "{url}",
}}
"""
    
    console.print(Panel(code, title="Code à ajouter", border_style="green"))
    
    # Proposer d'ouvrir le fichier
    if Confirm.ask("\nVoulez-vous ouvrir config_urls.py pour édition?"):
        config_file = Path(__file__).parent.parent / "config_urls.py"
        import os
        os.system(f'notepad "{config_file}"' if sys.platform == "win32" else f'nano "{config_file}"')


def test_config():
    """Test la configuration actuelle."""
    print_message("\n🧪 Test de la configuration...\n", "cyan")
    
    try:
        from src.utils.config import RENT_CUSTOM_URLS, DVF_CUSTOM_URLS
        
        if RENT_CUSTOM_URLS:
            print_message(f"✓ {len(RENT_CUSTOM_URLS)} URL(s) custom pour loyers", "green")
            for year, url in RENT_CUSTOM_URLS.items():
                print_message(f"  - {year}: {url[:60]}...", "")
        else:
            print_message("ℹ Aucune URL custom pour loyers (utilise les URLs par défaut)", "yellow")
        
        if DVF_CUSTOM_URLS:
            print_message(f"\n✓ {len(DVF_CUSTOM_URLS)} config(s) custom pour DVF", "green")
            for year, config in DVF_CUSTOM_URLS.items():
                if isinstance(config, dict):
                    print_message(f"  - {year}: {len(config)} département(s) configuré(s)", "")
                else:
                    print_message(f"  - {year}: Template {config[:60]}...", "")
        else:
            print_message("\nℹ Aucune URL custom pour DVF (utilise les URLs par défaut)", "yellow")
        
        return True
    except Exception as e:
        print_message(f"\n❌ Erreur lors du chargement de la config: {e}", "red")
        return False


def main():
    """Point d'entrée principal."""
    if RICH_AVAILABLE and console:
        console.print(Panel.fit(
            "[bold]🛠️  Assistant de Configuration[/bold]\n"
            "Configuration des URLs personnalisées pour le téléchargement des données",
            border_style="cyan"
        ))
    else:
        print("\n" + "="*70)
        print("🛠️  Assistant de Configuration")
        print("Configuration des URLs personnalisées")
        print("="*70 + "\n")
    
    # Vérifier si config_urls.py existe
    config_exists = check_config_file_exists()
    
    if config_exists:
        print_message("\n✓ config_urls.py existe déjà", "green")
        
        if RICH_AVAILABLE:
            choice = Prompt.ask(
                "\nQue voulez-vous faire?",
                choices=["test", "edit", "add", "guide", "quit"],
                default="test"
            )
        else:
            print("\n1. test  - Tester la configuration")
            print("2. edit  - Éditer config_urls.py")
            print("3. add   - Ajouter une URL")
            print("4. guide - Afficher le guide")
            print("5. quit  - Quitter")
            choice = input("\nChoix: ").strip().lower() or "test"
        
        if choice == "test":
            test_config()
        elif choice == "edit":
            config_file = Path(__file__).parent.parent / "config_urls.py"
            print_message(f"\nÉditez: {config_file}", "cyan")
            if RICH_AVAILABLE and Confirm.ask("Ouvrir maintenant?"):
                import os
                os.system(f'notepad "{config_file}"' if sys.platform == "win32" else f'nano "{config_file}"')
        elif choice == "add":
            add_custom_url_interactive()
        elif choice == "guide":
            show_url_finding_guide()
        
    else:
        print_message("\n⚠ config_urls.py n'existe pas encore", "yellow")
        
        if RICH_AVAILABLE:
            if Confirm.ask("Voulez-vous le créer maintenant?", default=True):
                if create_config_from_template():
                    print_message("\n✓ Configuration créée avec succès!", "green")
                    print_message("\nProchaines étapes:", "cyan")
                    print_message("1. Éditez config_urls.py pour ajouter vos URLs", "")
                    print_message("2. Lancez: python scripts/check_urls.py", "")
                    print_message("3. Consultez: docs/CUSTOM_URLS.md", "")
            else:
                print_message("\nVous pouvez le créer manuellement avec:", "yellow")
                print_message("  cp config_urls.example.py config_urls.py", "")
        else:
            print("\nCréez le fichier avec:")
            print("  cp config_urls.example.py config_urls.py")
    
    if RICH_AVAILABLE and console:
        console.print("\n[bold green]✓ Assistant terminé[/bold green]\n")
    else:
        print("\n✓ Assistant terminé\n")


if __name__ == "__main__":
    main()
