from dataclasses import dataclass


class PetHunterEvent:
    pass


@dataclass(frozen=True)
class BindWindowRequested(PetHunterEvent):
    window_name: str

