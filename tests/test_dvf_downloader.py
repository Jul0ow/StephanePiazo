"""Tests pour le module DVFDownloader."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.data.dvf_downloader import DVFDownloader


@pytest.fixture
def downloader(tmp_path):
    """Fixture pour créer un downloader avec un répertoire temporaire."""
    return DVFDownloader(data_dir=tmp_path)


def test_downloader_init(tmp_path):
    """Test l'initialisation du downloader."""
    downloader = DVFDownloader(data_dir=tmp_path)
    assert downloader.data_dir == tmp_path
    assert downloader.data_dir.exists()


def test_download_department_data_file_exists(downloader, tmp_path):
    """Test quand le fichier existe déjà."""
    # Créer un fichier existant
    existing_file = tmp_path / "dvf_2023_75.csv"
    existing_file.write_text("test")
    
    result = downloader.download_department_data("75", 2023)
    
    assert result == existing_file
    assert result.exists()


@patch('src.data.dvf_downloader.requests.get')
def test_download_department_data_success(mock_get, downloader, tmp_path):
    """Test téléchargement réussi."""
    # Mock de la réponse HTTP
    mock_response = Mock()
    mock_response.headers = {"content-length": "100"}
    mock_response.iter_content = lambda chunk_size: [b"test data"]
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    result = downloader.download_department_data("75", 2023)
    
    assert result is not None
    assert result.exists()
    assert mock_get.called


@patch('src.data.dvf_downloader.requests.get')
def test_download_department_data_failure(mock_get, downloader):
    """Test échec de téléchargement."""
    mock_get.side_effect = Exception("Network error")
    
    result = downloader.download_department_data("75", 2023)
    
    assert result is None


def test_load_idf_data_no_files(downloader):
    """Test chargement quand aucun fichier n'existe."""
    with pytest.raises(FileNotFoundError):
        downloader.load_idf_data(2023)
