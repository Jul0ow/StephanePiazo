#!/usr/bin/env python
"""
Script de vérification des URLs configurées.

Ce script teste la disponibilité et la validité des URLs configurées
pour le téléchargement des données DVF et de la Carte des loyers.
"""

import sys
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import (
    DVF_BASE_URL,
    DVF_CUSTOM_URLS,
    IDF_DEPARTMENTS,
    RENT_CSV_URLS,
    RENT_CUSTOM_URLS,
)

console = Console()


def check_url(url: str, timeout: int = 10) -> tuple[bool, Optional[str], Optional[int]]:
    """
    Vérifie si une URL est accessible.

    Args:
        url: URL à vérifier
        timeout: Timeout en secondes

    Returns:
        (accessible, message_erreur, taille_fichier)
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        if response.status_code == 200:
            size = int(response.headers.get("content-length", 0))
            return True, None, size
        elif response.status_code == 405:  # HEAD non supporté, essayer GET
            response = requests.get(url, timeout=timeout, stream=True)
            if response.status_code == 200:
                size = int(response.headers.get("content-length", 0))
                return True, None, size
        
        return False, f"HTTP {response.status_code}", None
    
    except requests.exceptions.Timeout:
        return False, "Timeout", None
    except requests.exceptions.ConnectionError:
        return False, "Connexion impossible", None
    except requests.exceptions.RequestException as e:
        return False, str(e), None
    except Exception as e:
        return False, f"Erreur: {e}", None


def format_size(size: Optional[int]) -> str:
    """Formate la taille en octets de manière lisible."""
    if size is None:
        return "?"
    
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    
    return f"{size:.1f} TB"


def check_rent_urls():
    """Vérifie les URLs de la Carte des loyers."""
    console.print("\n[bold cyan]🏠 Vérification des URLs de la Carte des loyers[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Année", style="cyan", width=8)
    table.add_column("Source", style="yellow", width=10)
    table.add_column("Status", width=15)
    table.add_column("Taille", width=12)
    table.add_column("URL", overflow="fold")
    
    # URLs par défaut
    for year, url in RENT_CSV_URLS.items():
        accessible, error, size = check_url(url)
        
        status = "[green]✓ Accessible[/green]" if accessible else f"[red]✗ {error}[/red]"
        
        table.add_row(
            str(year),
            "Défaut",
            status,
            format_size(size),
            url
        )
    
    # URLs custom
    for year, url in RENT_CUSTOM_URLS.items():
        accessible, error, size = check_url(url)
        
        status = "[green]✓ Accessible[/green]" if accessible else f"[red]✗ {error}[/red]"
        
        table.add_row(
            str(year),
            "Custom",
            status,
            format_size(size),
            url
        )
    
    if not RENT_CSV_URLS and not RENT_CUSTOM_URLS:
        console.print("[yellow]⚠ Aucune URL configurée[/yellow]")
        return
    
    console.print(table)


def check_dvf_urls():
    """Vérifie les URLs DVF."""
    console.print("\n[bold cyan]📊 Vérification des URLs DVF[/bold cyan]\n")
    
    # URLs par défaut (tester un échantillon)
    console.print("[yellow]URLs par défaut (échantillon: Paris 75, année 2023):[/yellow]")
    
    sample_year = 2023
    sample_dept = "75"
    default_url = f"{DVF_BASE_URL}/{sample_year}/departements/{sample_dept}.csv.gz"
    
    accessible, error, size = check_url(default_url)
    
    if accessible:
        console.print(f"  [green]✓ URL de base accessible[/green]")
        console.print(f"  URL: {default_url}")
        console.print(f"  Taille: {format_size(size)}")
    else:
        console.print(f"  [red]✗ URL de base non accessible: {error}[/red]")
        console.print(f"  URL: {default_url}")
    
    # URLs custom
    if DVF_CUSTOM_URLS:
        console.print("\n[yellow]URLs custom configurées:[/yellow]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Année", style="cyan", width=8)
        table.add_column("Type", style="yellow", width=15)
        table.add_column("Détails", overflow="fold")
        
        for year, config in DVF_CUSTOM_URLS.items():
            if isinstance(config, dict):
                # URLs spécifiques par département
                for dept, url in config.items():
                    accessible, error, size = check_url(url)
                    status = "✓ Accessible" if accessible else f"✗ {error}"
                    
                    table.add_row(
                        str(year),
                        f"Dept {dept}",
                        f"{status} | {format_size(size)} | {url}"
                    )
            
            elif isinstance(config, str):
                # Template d'URL
                # Tester avec le département 75
                url = config.format(dept="75")
                accessible, error, size = check_url(url)
                status = "✓ Accessible" if accessible else f"✗ {error}"
                
                table.add_row(
                    str(year),
                    "Template",
                    f"{status} (test avec 75) | {format_size(size)} | {config}"
                )
        
        console.print(table)
    else:
        console.print("[yellow]  Aucune URL custom configurée[/yellow]")


def check_config_file():
    """Vérifie l'existence du fichier config_urls.py."""
    console.print("\n[bold cyan]⚙️  Vérification de la configuration[/bold cyan]\n")
    
    config_file = Path(__file__).parent.parent / "config_urls.py"
    config_example = Path(__file__).parent.parent / "config_urls.example.py"
    
    if config_file.exists():
        console.print("[green]✓ config_urls.py existe[/green]")
        console.print(f"  Chemin: {config_file}")
        
        # Lire et afficher un aperçu
        content = config_file.read_text()
        lines = [l for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]
        
        if lines:
            console.print("\n[yellow]Aperçu du contenu:[/yellow]")
            for line in lines[:5]:  # Afficher les 5 premières lignes
                console.print(f"  {line}")
            if len(lines) > 5:
                console.print(f"  ... ({len(lines) - 5} lignes supplémentaires)")
    else:
        console.print("[yellow]⚠ config_urls.py n'existe pas[/yellow]")
        
        if config_example.exists():
            console.print(f"[blue]ℹ️  Créez-le à partir de l'exemple:[/blue]")
            console.print(f"  cp config_urls.example.py config_urls.py")
        else:
            console.print(f"[red]✗ config_urls.example.py introuvable[/red]")


def show_summary():
    """Affiche un résumé des URLs disponibles."""
    console.print("\n[bold cyan]📋 Résumé de la configuration[/bold cyan]\n")
    
    summary = []
    
    # Loyers
    total_rent_urls = len(RENT_CSV_URLS) + len(RENT_CUSTOM_URLS)
    summary.append(f"Carte des loyers: {total_rent_urls} année(s) configurée(s)")
    
    if RENT_CUSTOM_URLS:
        summary.append(f"  └─ {len(RENT_CUSTOM_URLS)} URL(s) custom")
    
    # DVF
    if DVF_CUSTOM_URLS:
        custom_count = sum(
            len(config) if isinstance(config, dict) else 1
            for config in DVF_CUSTOM_URLS.values()
        )
        summary.append(f"DVF: {custom_count} URL(s) custom configurée(s)")
    else:
        summary.append("DVF: URLs par défaut uniquement")
    
    for line in summary:
        console.print(f"  {line}")


def main():
    """Point d'entrée principal."""
    console.print(Panel.fit(
        "[bold]Vérification des URLs de téléchargement[/bold]\n"
        "Ce script vérifie la disponibilité des URLs configurées",
        border_style="cyan"
    ))
    
    # Vérifier le fichier de config
    check_config_file()
    
    # Vérifier les URLs de loyers
    check_rent_urls()
    
    # Vérifier les URLs DVF
    check_dvf_urls()
    
    # Afficher le résumé
    show_summary()
    
    console.print("\n[green]✓ Vérification terminée[/green]\n")


if __name__ == "__main__":
    try:
        # Installer rich si nécessaire
        import rich
    except ImportError:
        print("⚠ Le package 'rich' est requis pour ce script.")
        print("Installation: pip install rich")
        sys.exit(1)
    
    main()
