"""Tests pour les URLs personnalisées."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.data.dvf_downloader import DVFDownloader
from src.data.rent_downloader import RentDownloader


class TestRentDownloaderCustomURLs:
    """Tests pour le téléchargement de la Carte des loyers avec URLs custom."""

    @patch("src.data.rent_downloader.requests.get")
    def test_download_with_custom_url(self, mock_get, tmp_path):
        """Test téléchargement avec URL personnalisée."""
        # Préparer le mock
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Créer le downloader
        downloader = RentDownloader(data_dir=tmp_path)

        # Télécharger avec URL custom
        custom_url = "https://custom-server.com/loyers_2024.csv"
        result = downloader.download_rent_data(year=2024, custom_url=custom_url)

        # Vérifications
        assert result is not None
        assert result.exists()
        assert result.name == "carte_loyers_2024.csv"
        mock_get.assert_called_once_with(custom_url, stream=True, timeout=60)

    @patch("src.data.rent_downloader.requests.get")
    def test_download_without_custom_url_uses_config(self, mock_get, tmp_path):
        """Test que le téléchargement utilise la config si pas d'URL custom."""
        # Préparer le mock
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Créer le downloader
        downloader = RentDownloader(data_dir=tmp_path)

        # Télécharger sans URL custom (utilise RENT_CSV_URLS)
        result = downloader.download_rent_data(year=2024)

        # Vérifier qu'une requête a été faite
        assert mock_get.called
        assert result is not None

    def test_download_without_configured_year_fails(self, tmp_path):
        """Test qu'une erreur est retournée si l'année n'est pas configurée."""
        downloader = RentDownloader(data_dir=tmp_path)

        # Essayer de télécharger une année non configurée
        result = downloader.download_rent_data(year=2099)

        # Doit retourner None (pas d'URL configurée)
        assert result is None

    @patch("src.data.rent_downloader.requests.get")
    def test_download_force_redownload(self, mock_get, tmp_path):
        """Test que force=True force le re-téléchargement."""
        # Créer un fichier existant
        existing_file = tmp_path / "carte_loyers_2024.csv"
        existing_file.write_text("old data")

        # Préparer le mock
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content = lambda chunk_size: [b"new data"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        downloader = RentDownloader(data_dir=tmp_path)

        # Télécharger avec force=True
        custom_url = "https://custom-server.com/loyers_2024.csv"
        result = downloader.download_rent_data(
            year=2024, custom_url=custom_url, force=True
        )

        # Vérifier que le téléchargement a été fait
        assert result is not None
        assert mock_get.called

    def test_download_skip_if_exists_and_no_force(self, tmp_path):
        """Test que le téléchargement est ignoré si le fichier existe et force=False."""
        # Créer un fichier existant
        existing_file = tmp_path / "carte_loyers_2024.csv"
        existing_file.write_text("existing data")

        downloader = RentDownloader(data_dir=tmp_path)

        # Essayer de télécharger (devrait retourner le fichier existant)
        custom_url = "https://custom-server.com/loyers_2024.csv"
        result = downloader.download_rent_data(
            year=2024, custom_url=custom_url, force=False
        )

        # Vérifier que le fichier existant est retourné
        assert result == existing_file


class TestDVFDownloaderCustomURLs:
    """Tests pour le téléchargement DVF avec URLs custom."""

    @patch("src.data.dvf_downloader.requests.get")
    @patch("src.data.dvf_downloader.gzip.open")
    def test_download_department_with_custom_url(
        self, mock_gzip_open, mock_get, tmp_path
    ):
        """Test téléchargement d'un département avec URL custom."""
        # Préparer le mock
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock gzip
        mock_gzip_file = Mock()
        mock_gzip_open.return_value.__enter__ = Mock(return_value=mock_gzip_file)
        mock_gzip_open.return_value.__exit__ = Mock(return_value=False)

        # Créer le downloader
        downloader = DVFDownloader(data_dir=tmp_path)

        # Télécharger avec URL custom
        custom_url = "https://custom-server.com/paris.csv.gz"
        result = downloader.download_department_data(
            department="75", year=2023, custom_url=custom_url
        )

        # Vérifications
        assert result is not None
        mock_get.assert_called_once_with(custom_url, stream=True, timeout=30)

    @patch("src.data.dvf_downloader.requests.get")
    @patch("src.data.dvf_downloader.gzip.open")
    def test_download_idf_with_custom_urls_dict(
        self, mock_gzip_open, mock_get, tmp_path
    ):
        """Test téléchargement IDF avec dictionnaire d'URLs custom."""
        # Préparer le mock
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock gzip
        mock_gzip_file = Mock()
        mock_gzip_open.return_value.__enter__ = Mock(return_value=mock_gzip_file)
        mock_gzip_open.return_value.__exit__ = Mock(return_value=False)

        # Créer le downloader
        downloader = DVFDownloader(data_dir=tmp_path)

        # URLs custom pour quelques départements
        custom_urls = {
            "75": "https://server1.com/paris.csv.gz",
            "92": "https://server2.com/hauts_de_seine.csv.gz",
        }

        # Télécharger IDF avec URLs custom
        with patch.object(downloader, "download_department_data") as mock_download:
            mock_download.return_value = tmp_path / "test.csv"
            downloader.download_idf_data(year=2023, custom_urls=custom_urls)

            # Vérifier que les URLs custom ont été passées
            calls = mock_download.call_args_list
            assert len(calls) == 8  # 8 départements IDF

            # Vérifier que les URLs custom ont été utilisées pour 75 et 92
            dept_75_call = [c for c in calls if c[0][0] == "75"][0]
            dept_92_call = [c for c in calls if c[0][0] == "92"][0]

            assert dept_75_call[1]["custom_url"] == custom_urls["75"]
            assert dept_92_call[1]["custom_url"] == custom_urls["92"]


class TestConfigFileLoading:
    """Tests pour le chargement du fichier config_urls.py."""

    def test_config_file_loading(self, tmp_path, monkeypatch):
        """Test que le fichier config_urls.py est chargé correctement."""
        # Créer un fichier config_urls.py temporaire
        config_content = """
# Configuration de test
RENT_CUSTOM_URLS = {
    2024: "https://test-server.com/loyers.csv",
}

DVF_CUSTOM_URLS = {
    2023: "https://test-server.com/dvf/{dept}.csv.gz",
}
"""
        config_file = tmp_path / "config_urls.py"
        config_file.write_text(config_content)

        # Changer le PROJECT_ROOT temporairement
        monkeypatch.setattr("src.utils.config.PROJECT_ROOT", tmp_path)

        # Recharger le module config
        import importlib
        import src.utils.config

        importlib.reload(src.utils.config)

        # Vérifier que les URLs custom ont été chargées
        assert 2024 in src.utils.config.RENT_CUSTOM_URLS
        assert src.utils.config.RENT_CUSTOM_URLS[2024] == "https://test-server.com/loyers.csv"


class TestCustomURLsPriority:
    """Tests pour vérifier l'ordre de priorité des URLs."""

    @patch("src.data.rent_downloader.requests.get")
    def test_inline_url_has_priority_over_config(self, mock_get, tmp_path):
        """Test que l'URL passée en paramètre a la priorité sur la config."""
        # Préparer le mock
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        downloader = RentDownloader(data_dir=tmp_path)

        # URL custom inline (devrait avoir la priorité)
        inline_url = "https://inline-server.com/loyers.csv"

        # Télécharger
        downloader.download_rent_data(year=2024, custom_url=inline_url)

        # Vérifier que l'URL inline a été utilisée
        mock_get.assert_called_once_with(inline_url, stream=True, timeout=60)


class TestURLValidation:
    """Tests pour la validation des URLs."""

    @patch("src.data.rent_downloader.requests.get")
    def test_invalid_url_returns_none(self, mock_get, tmp_path):
        """Test qu'une URL invalide retourne None."""
        # Simuler une erreur de connexion
        mock_get.side_effect = Exception("Connection error")

        downloader = RentDownloader(data_dir=tmp_path)

        # Essayer de télécharger avec une URL invalide
        result = downloader.download_rent_data(
            year=2024, custom_url="https://invalid-url.com/file.csv"
        )

        # Doit retourner None
        assert result is None

    @patch("src.data.dvf_downloader.requests.get")
    def test_dvf_invalid_url_returns_none(self, mock_get, tmp_path):
        """Test qu'une URL DVF invalide retourne None."""
        # Simuler une erreur 404
        mock_get.side_effect = Exception("404 Not Found")

        downloader = DVFDownloader(data_dir=tmp_path)

        # Essayer de télécharger avec une URL invalide
        result = downloader.download_department_data(
            department="75",
            year=2023,
            custom_url="https://invalid-url.com/paris.csv.gz",
        )

        # Doit retourner None
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
