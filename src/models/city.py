"""Modèles pour représenter les villes et leurs statistiques."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PropertyTypeStats:
    """Statistiques pour un type de bien (appartement ou maison)."""

    prix_moyen_m2: Optional[float] = None
    prix_min_m2: Optional[float] = None
    prix_max_m2: Optional[float] = None
    nombre_transactions: int = 0
    nombre_t1: int = 0
    nombre_t2: int = 0
    nombre_t3: int = 0
    nombre_t4: int = 0
    nombre_t5_plus: int = 0
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
class RentStats:
    """Statistiques de loyers pour une ville (basé sur Carte des loyers)."""

    loyer_moyen_m2: Optional[float] = None  # loypredm2
    loyer_bas_m2: Optional[float] = None  # lwr_IPm2 (borne basse intervalle prédiction)
    loyer_haut_m2: Optional[float] = None  # upr_IPm2 (borne haute intervalle prédiction)
    type_prediction: Optional[str] = None  # TYPPRED: "Commune", "epci" ou "maile"
    nb_observations_commune: Optional[int] = None  # nbobs_com
    nb_observations_maille: Optional[int] = None  # nbobs_mail
    r2_ajuste: Optional[float] = None  # R2_adj (coefficient de détermination)
    id_maille: Optional[str] = None  # id_zone

    def __repr__(self) -> str:
        if self.loyer_moyen_m2:
            return (
                f"RentStats(moyen={self.loyer_moyen_m2:.2f}€/m², "
                f"bas={self.loyer_bas_m2:.2f}€/m², haut={self.loyer_haut_m2:.2f}€/m², "
                f"type={self.type_prediction}, obs={self.nb_observations_commune})"
            )
        return "RentStats(no data)"

    @property
    def is_reliable(self) -> bool:
        """Vérifie si les données sont fiables selon les critères de la Carte des loyers."""
        if not self.r2_ajuste or not self.nb_observations_commune:
            return False
        # Critères de fiabilité selon la documentation
        return self.r2_ajuste >= 0.5 and self.nb_observations_commune >= 30


@dataclass
class CityStats:
    """Statistiques immobilières d'une ville."""

    prix_moyen_m2: float
    prix_median_m2: float
    prix_min_m2: float
    prix_max_m2: float
    nombre_transactions: int
    nombre_t1: int
    nombre_t2: int
    nombre_t3: int
    nombre_t4: int
    nombre_t5_plus: int
    surface_moyenne: float
    appartements: Optional[PropertyTypeStats] = None
    maisons: Optional[PropertyTypeStats] = None
    loyers: Optional[RentStats] = None  # Ajout des statistiques de loyers

    def __repr__(self) -> str:
        base = (
            f"CityStats(prix_moyen={self.prix_moyen_m2:.0f}€/m², "
            f"transactions={self.nombre_transactions}"
        )
        if self.appartements and self.appartements.prix_moyen_m2:
            base += f", appart={self.appartements.prix_moyen_m2:.0f}€/m²"
        if self.maisons and self.maisons.prix_moyen_m2:
            base += f", maison={self.maisons.prix_moyen_m2:.0f}€/m²"
        if self.loyers and self.loyers.loyer_moyen_m2:
            base += f", loyer={self.loyers.loyer_moyen_m2:.2f}€/m²/mois"
        return base + ")"


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
