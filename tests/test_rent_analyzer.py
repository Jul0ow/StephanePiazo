"""Tests pour l'analyseur de loyers."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.analysis.rent_analyzer import RentAnalyzer
from src.models.city import RentStats


@pytest.fixture
def sample_rent_data():
    """Crée un jeu de données de test pour les loyers."""
    return pd.DataFrame({
        "id_zone": ["ZONE_001", "ZONE_002", "ZONE_003"],
        "INSEE_C": ["75056", "92050", "93001"],
        "LIBGEO": ["Paris", "Nanterre", "Aubervilliers"],
        "EPCI": ["EPCI1", "EPCI2", "EPCI3"],
        "DEP": ["75", "92", "93"],
        "REG": ["11", "11", "11"],
        "loypredm2": [28.5, 22.3, 18.7],
        "lwr_IPm2": [26.0, 20.5, 17.0],
        "upr_IPm2": [31.0, 24.1, 20.4],
        "TYPPRED": ["Commune", "Commune", "maile"],
        "nbobs_com": [150, 80, 25],
        "nbobs_mail": [150, 80, 120],
        "R2_adj": [0.75, 0.62, 0.48],
    })


@pytest.fixture
def mock_rent_analyzer(tmp_path, sample_rent_data):
    """Crée un analyseur de loyers mocké pour les tests."""
    analyzer = RentAnalyzer(year=2024, data_dir=tmp_path)
    
    # Mock de la méthode load_data
    with patch.object(analyzer.downloader, 'load_rent_data', return_value=sample_rent_data):
        analyzer.data = sample_rent_data
        analyzer.data_idf = sample_rent_data  # Pour les tests, tout est IDF
    
    return analyzer


class TestRentAnalyzer:
    """Tests pour la classe RentAnalyzer."""

    def test_initialization(self, tmp_path):
        """Test l'initialisation de l'analyseur."""
        analyzer = RentAnalyzer(year=2024, data_dir=tmp_path)
        
        assert analyzer.year == 2024
        assert analyzer.data_dir == tmp_path
        assert analyzer.data is None
        assert analyzer.data_idf is None

    def test_load_data(self, tmp_path, sample_rent_data):
        """Test le chargement des données."""
        analyzer = RentAnalyzer(year=2024, data_dir=tmp_path)
        
        with patch.object(analyzer.downloader, 'load_rent_data', return_value=sample_rent_data):
            data = analyzer.load_data()
            
            assert len(data) == 3
            assert "loypredm2" in data.columns
            assert analyzer.data is not None

    def test_get_city_rent_stats_by_name(self, mock_rent_analyzer):
        """Test la récupération des stats par nom de ville."""
        rent_stats = mock_rent_analyzer.get_city_rent_stats(city_name="Paris")
        
        assert rent_stats is not None
        assert isinstance(rent_stats, RentStats)
        assert rent_stats.loyer_moyen_m2 == 28.5
        assert rent_stats.loyer_bas_m2 == 26.0
        assert rent_stats.loyer_haut_m2 == 31.0
        assert rent_stats.type_prediction == "Commune"
        assert rent_stats.nb_observations_commune == 150
        assert rent_stats.r2_ajuste == 0.75

    def test_get_city_rent_stats_by_insee(self, mock_rent_analyzer):
        """Test la récupération des stats par code INSEE."""
        rent_stats = mock_rent_analyzer.get_city_rent_stats(insee_code="92050")
        
        assert rent_stats is not None
        assert rent_stats.loyer_moyen_m2 == 22.3
        assert rent_stats.nb_observations_commune == 80

    def test_get_city_rent_stats_not_found(self, mock_rent_analyzer):
        """Test quand la ville n'est pas trouvée."""
        rent_stats = mock_rent_analyzer.get_city_rent_stats(city_name="VilleInexistante")
        
        assert rent_stats is None

    def test_get_city_rent_stats_no_criteria(self, mock_rent_analyzer):
        """Test qu'une erreur est levée sans critère de recherche."""
        with pytest.raises(ValueError, match="Vous devez fournir city_name ou insee_code"):
            mock_rent_analyzer.get_city_rent_stats()

    def test_is_reliable_stats(self, mock_rent_analyzer):
        """Test la méthode is_reliable."""
        # Paris devrait être fiable (R2=0.75, obs=150)
        paris_stats = mock_rent_analyzer.get_city_rent_stats(city_name="Paris")
        assert paris_stats.is_reliable is True
        
        # Aubervilliers ne devrait pas être fiable (R2=0.48 < 0.5)
        auber_stats = mock_rent_analyzer.get_city_rent_stats(city_name="Aubervilliers")
        assert auber_stats.is_reliable is False

    def test_compare_cities(self, mock_rent_analyzer):
        """Test la comparaison de villes."""
        comparison = mock_rent_analyzer.compare_cities(["Paris", "Nanterre"])
        
        assert len(comparison) == 2
        assert "loyer_moyen_m2" in comparison.columns
        assert "fiable" in comparison.columns
        
        # Vérifier que Paris est en premier (loyer plus élevé)
        assert comparison.iloc[0]["commune"] == "Paris"

    def test_compare_cities_with_not_found(self, mock_rent_analyzer):
        """Test la comparaison avec des villes non trouvées."""
        comparison = mock_rent_analyzer.compare_cities(
            ["Paris", "VilleInexistante", "Nanterre"]
        )
        
        # Devrait retourner seulement les villes trouvées
        assert len(comparison) == 2

    def test_get_top_cities_high(self, mock_rent_analyzer):
        """Test récupération des loyers les plus élevés."""
        top = mock_rent_analyzer.get_top_cities(n=2, ascending=False)
        
        assert len(top) == 2
        assert top.iloc[0]["commune"] == "Paris"  # Le plus élevé
        assert top.iloc[0]["loyer_moyen_m2"] == 28.5

    def test_get_top_cities_low(self, mock_rent_analyzer):
        """Test récupération des loyers les plus bas."""
        top = mock_rent_analyzer.get_top_cities(n=2, ascending=True)
        
        assert len(top) == 2
        assert top.iloc[0]["commune"] == "Aubervilliers"  # Le plus bas
        assert top.iloc[0]["loyer_moyen_m2"] == 18.7

    def test_get_top_cities_by_department(self, mock_rent_analyzer):
        """Test filtrage par département."""
        top = mock_rent_analyzer.get_top_cities(n=10, department_code="75")
        
        assert len(top) == 1
        assert top.iloc[0]["departement"] == "75"

    def test_get_department_statistics(self, mock_rent_analyzer):
        """Test des statistiques par département."""
        stats = mock_rent_analyzer.get_department_statistics("75")
        
        assert not stats.empty
        assert stats.iloc[0]["nb_communes"] == 1
        assert stats.iloc[0]["loyer_moyen"] == 28.5

    def test_get_department_statistics_not_found(self, mock_rent_analyzer):
        """Test statistiques pour département inexistant."""
        stats = mock_rent_analyzer.get_department_statistics("99")
        
        assert stats.empty

    def test_get_idf_statistics(self, mock_rent_analyzer):
        """Test des statistiques IDF globales."""
        with patch("src.analysis.rent_analyzer.IDF_DEPARTMENTS", {"75": "Paris", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis"}):
            stats = mock_rent_analyzer.get_idf_statistics()
            
            assert len(stats) == 3
            assert "department_code" in stats.columns
            assert "loyer_moyen" in stats.columns


class TestRentStats:
    """Tests pour la classe RentStats."""

    def test_rent_stats_creation(self):
        """Test la création d'un objet RentStats."""
        stats = RentStats(
            loyer_moyen_m2=25.0,
            loyer_bas_m2=23.0,
            loyer_haut_m2=27.0,
            type_prediction="Commune",
            nb_observations_commune=100,
            r2_ajuste=0.8,
        )
        
        assert stats.loyer_moyen_m2 == 25.0
        assert stats.loyer_bas_m2 == 23.0
        assert stats.loyer_haut_m2 == 27.0

    def test_rent_stats_is_reliable_true(self):
        """Test fiabilité avec bonnes conditions."""
        stats = RentStats(
            loyer_moyen_m2=25.0,
            nb_observations_commune=50,
            r2_ajuste=0.7,
        )
        
        assert stats.is_reliable is True

    def test_rent_stats_is_reliable_false_r2(self):
        """Test fiabilité avec R2 trop faible."""
        stats = RentStats(
            loyer_moyen_m2=25.0,
            nb_observations_commune=50,
            r2_ajuste=0.3,  # < 0.5
        )
        
        assert stats.is_reliable is False

    def test_rent_stats_is_reliable_false_observations(self):
        """Test fiabilité avec pas assez d'observations."""
        stats = RentStats(
            loyer_moyen_m2=25.0,
            nb_observations_commune=20,  # < 30
            r2_ajuste=0.7,
        )
        
        assert stats.is_reliable is False

    def test_rent_stats_is_reliable_missing_data(self):
        """Test fiabilité avec données manquantes."""
        stats = RentStats(loyer_moyen_m2=25.0)
        
        assert stats.is_reliable is False

    def test_rent_stats_repr_with_data(self):
        """Test la représentation string avec données."""
        stats = RentStats(
            loyer_moyen_m2=25.0,
            loyer_bas_m2=23.0,
            loyer_haut_m2=27.0,
            type_prediction="Commune",
            nb_observations_commune=100,
        )
        
        repr_str = repr(stats)
        assert "25.00€/m²" in repr_str
        assert "Commune" in repr_str

    def test_rent_stats_repr_no_data(self):
        """Test la représentation string sans données."""
        stats = RentStats()
        
        assert repr(stats) == "RentStats(no data)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
