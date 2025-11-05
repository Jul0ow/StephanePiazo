"""Script pour tester l'encodage des fichiers CSV de loyers."""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.rent_downloader import RentDownloader
from src.utils.config import RAW_DATA_DIR

def detect_file_encoding(file_path: Path) -> str:
    """
    Détecte l'encodage d'un fichier en essayant plusieurs options.
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        Nom de l'encodage détecté
    """
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Lire les 100 premières lignes
                for _ in range(100):
                    f.readline()
            print(f"✓ {file_path.name}: encodage détecté = {encoding}")
            return encoding
        except UnicodeDecodeError:
            continue
    
    print(f"❌ {file_path.name}: aucun encodage compatible trouvé")
    return None


def main():
    """Test des encodages des fichiers de loyers."""
    print("=" * 80)
    print("TEST DES ENCODAGES DES FICHIERS DE LOYERS")
    print("=" * 80)
    
    # Chercher les fichiers CSV de loyers
    csv_files = list(RAW_DATA_DIR.glob("carte_loyers_*.csv"))
    
    if not csv_files:
        print("\n❌ Aucun fichier de loyers trouvé dans", RAW_DATA_DIR)
        print("\nTéléchargez d'abord les données avec:")
        print("  python main.py --rent-year 2024 --download-rent")
        return
    
    print(f"\n📁 Répertoire: {RAW_DATA_DIR}")
    print(f"📄 Fichiers trouvés: {len(csv_files)}\n")
    
    for csv_file in sorted(csv_files):
        detect_file_encoding(csv_file)
    
    print("\n" + "=" * 80)
    print("TEST DU CHARGEMENT AVEC PANDAS")
    print("=" * 80 + "\n")
    
    # Test du chargement
    downloader = RentDownloader()
    
    try:
        df = downloader.load_rent_data(year=2024)
        print(f"\n✓ Chargement réussi!")
        print(f"  • {len(df)} lignes")
        print(f"  • Colonnes: {df.columns.tolist()[:5]}...")
        
        if "type_bien" in df.columns:
            print(f"  • Types de bien: {df['type_bien'].unique().tolist()}")
        
        print(f"\n📊 Aperçu des données:")
        print(df.head(3))
        
    except Exception as e:
        print(f"\n❌ Erreur lors du chargement: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
