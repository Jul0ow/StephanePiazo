"""Modèles pour représenter les villes et leurs statistiques."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CityStats:
    """Statistiques immobilières d'une ville."""

    prix_moyen_m2: float
    prix_median_m2: float
    prix_min_m2: float
    prix_max_m2: float
    nombre_transactions: int
    surface_moyenne: float
    prix_moyen_appartement_m2: Optional[float] = None
    prix_moyen_maison_m2: Optional[float] = None

    def __repr__(self) -> str:
        return (
            f"CityStats(prix_moyen={self.prix_moyen_m2:.0f}€/m², "
            f"transactions={self.nombre_transactions})"
        )


@dataclass
class City:
    """Représentation d'une ville avec ses données immobilières."""

    name: str
    code_insee: str
    department: str
    department_code: str
    stats: Optional[CityStats] = None

    def __repr__(self) -> str:
        stats_str = f", stats={self.stats}" if self.stats else ""
        return f"City(name='{self.name}', dept={self.department_code}{stats_str})"

    @property
    def full_name(self) -> str:
        """Nom complet avec département."""
        return f"{self.name} ({self.department_code})"
