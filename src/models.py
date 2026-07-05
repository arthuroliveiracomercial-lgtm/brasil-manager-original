from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tactic:
    mentalidade: str = "Equilibrada"
    estilo: str = "Equilibrado"
    linha_defensiva: str = "Normal"
    pressao: str = "Normal"
    ritmo: str = "Normal"
    foco_ataque: str = "Misto"
    tipo_passe: str = "Misto"


@dataclass(frozen=True)
class MatchResult:
    match_id: str
    home_id: str
    away_id: str
    home_goals: int
    away_goals: int
    events: tuple[str, ...]
    home_strength: float
    away_strength: float
    statistics: dict = field(default_factory=dict)
    scorers: tuple[str, ...] = ()
    best_player: str = ""


FORMATIONS = {
    "4-4-2": ["GOL", "LAT", "ZAG", "ZAG", "LAT", "MC", "MC", "PE", "PD", "ATA", "ATA"],
    "4-3-3": ["GOL", "LAT", "ZAG", "ZAG", "LAT", "VOL", "MC", "MEI", "PE", "PD", "ATA"],
    "4-2-3-1": ["GOL", "LAT", "ZAG", "ZAG", "LAT", "VOL", "VOL", "PE", "MEI", "PD", "ATA"],
    "3-5-2": ["GOL", "ZAG", "ZAG", "ZAG", "ALA", "VOL", "MC", "MEI", "ALA", "ATA", "ATA"],
    "4-1-4-1": ["GOL", "LAT", "ZAG", "ZAG", "LAT", "VOL", "MC", "MC", "PE", "PD", "ATA"],
    "4-3-1-2": ["GOL", "LAT", "ZAG", "ZAG", "LAT", "VOL", "MC", "MC", "MEI", "ATA", "ATA"],
}
