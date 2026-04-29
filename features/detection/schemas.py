from dataclasses import dataclass


@dataclass
class PetCandidate:
    pet_type: str
    confidence: float
    is_polluted: bool = False


@dataclass
class BattleDecision:
    is_shiny: bool
    confidence: float = 0.0
    reason: str = ""

