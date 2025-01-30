import dataclasses

from playing_card_tools import Card


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None
    hand_value: int = 0

    def __post_init__(self):
        if self.hand is None:
            self.hand = []

    def __str__(self):
        return f"{self.name}: {[str(card) for card in self.hand]}"
