import dataclasses

from playing_card_tools import Card


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None

@dataclasses.dataclass
class Team:
    def __init__(self, members: list[Player], name: str):
        self.name = name
        self.members = members
        self.score = 0

