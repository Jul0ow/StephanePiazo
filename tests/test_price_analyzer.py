"""Tests pour le module PriceAnalyzer."""

import pytest
import pandas as pd
from src.analysis.price_analyzer import PriceAnalyzer
from src.models.city import CityStats


@pytest.fixture
def sample_data():
    """Fixture avec des données de test."""
    return pd.DataFrame({
        'nom_commune': ['Paris', 'Paris', 'Versailles', 'Versailles'],
        'code_departement': ['75', '75', '78', '78'],
        'prix_m2': [10000, 12000, 8000, 9000],
        'surface_reelle_bati': [50, 60, 80, 90],
        'valeur_fonciere': [500000, 720000, 640000, 810000],
        'type_local': ['Appartement', 'Appartement', 'Maison', 'Maison']
    })


@pytest.fixture
def analyzer(sample_data):
    """Fixture pour créer un analyzer avec des données de test."""
    return PriceAnalyzer(df=sample_data)


def test_analyzer_init():
    """Test l'initialisation de l'analyzer."""
    analyzer = PriceAnalyzer()
    assert analyzer.df is None


def test_analyzer_with_data(sample_data):
    """Test l'initialisation avec des données."""
    analyzer = PriceAnalyzer(df=sample_data)
    assert analyzer.df is not None
    assert len(analyzer.df) == 4


def test_get_city_stats_paris(analyzer):
    """Test calcul des stats pour Paris."""
    stats = analyzer.get_city_stats("Paris")
    
    assert stats is not None
    assert isinstance(stats, CityStats)
    assert stats.prix_moyen_m2 == 11000  # (10000 + 12000) / 2
    assert stats.nombre_transactions == 2
    assert stats.prix_min_m2 == 10000
    assert stats.prix_max_m2 == 12000


def test_get_city_stats_case_insensitive(analyzer):
    """Test que la recherche est insensible à la casse."""
    stats_lower = analyzer.get_city_stats("paris")
    stats_upper = analyzer.get_city_stats("PARIS")
    
    assert stats_lower is not None
    assert stats_upper is not None
    assert stats_lower.prix_moyen_m2 == stats_upper.prix_moyen_m2


def test_get_city_stats_not_found(analyzer):
    """Test pour une ville inexistante."""
    stats = analyzer.get_city_stats("NonExistante")
    assert stats is None


def test_get_city_stats_no_data():
    """Test sans données chargées."""
    analyzer = PriceAnalyzer()
    
    with pytest.raises(ValueError, match="Aucune donnée chargée"):
        analyzer.get_city_stats("Paris")


def test_analyze_all_cities(analyzer):
    """Test analyse de toutes les villes."""
    results = analyzer.analyze_all_cities()
    
    assert len(results) == 2  # Paris et Versailles
    assert 'ville' in results.columns
    assert 'prix_moyen_m2' in results.columns
    assert 'nombre_transactions' in results.columns


def test_get_department_stats(analyzer):
    """Test statistiques par département."""
    results = analyzer.get_department_stats("75")
    
    assert len(results) == 1  # Uniquement Paris
    assert results.iloc[0]['ville'] == 'Paris'
    assert results.iloc[0]['prix_moyen_m2'] == 11000
