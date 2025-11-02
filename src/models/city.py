"""Modèles pour représenter les villes et leurs statistiques."""

from dataclasses import dataclass
from typing import Optional


@dataclass
<<<<<<< HEAD
class PropertyTypeStats:
    """Statistiques pour un type de bien (appartement ou maison)."""

    prix_moyen_m2: Optional[float] = None
    prix_min_m2: Optional[float] = None
    prix_max_m2: Optional[float] = None
    nombre_transactions: int = 0
    surface_moyenne: Optional[float] = None

    def __repr__(self) -> str:
        if self.prix_moyen_m2:
            return (
                f"PropertyTypeStats(moyen={self.prix_moyen_m2:.0f}€/m², "
                f"min={self.prix_min_m2:.0f}€/m², max={self.prix_max_m2:.0f}€/m², "
                f"transactions={self.nombre_transactions})"
            )
        return "PropertyTypeStats(no data)"


@dataclass
=======
>>>>>>> b635870c043313b779e3bb0e5486256e81c809f2
class CityStats:
    """Statistiques immobilières d'une ville."""

    prix_moyen_m2: float
    prix_median_m2: float
    prix_min_m2: float
    prix_max_m2: float
    nombre_transactions: int
    surface_moyenne: float
<<<<<<< HEAD
    appartements: Optional[PropertyTypeStats] = None
    maisons: Optional[PropertyTypeStats] = None

    def __repr__(self) -> str:
        base = (
            f"CityStats(prix_moyen={self.prix_moyen_m2:.0f}€/m², "
            f"transactions={self.nombre_transactions}"
        )
        if self.appartements and self.appartements.prix_moyen_m2:
            base += f", appart={self.appartements.prix_moyen_m2:.0f}€/m²"
        if self.maisons and self.maisons.prix_moyen_m2:
            base += f", maison={self.maisons.prix_moyen_m2:.0f}€/m²"
        return base + ")"
=======
    prix_moyen_appartement_m2: Optional[float] = None
    prix_moyen_maison_m2: Optional[float] = None

    def __repr__(self) -> str:
        return (
            f"CityStats(prix_moyen={self.prix_moyen_m2:.0f}€/m², "
            f"transactions={self.nombre_transactions})"
        )
>>>>>>> b635870c043313b779e3bb0e5486256e81c809f2


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
