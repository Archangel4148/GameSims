import dataclasses
import random

from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None
    hand_values: list[int] | None = None

    def __post_init__(self):
        if self.hand is None:
            self.hand = []
        if self.hand_values is None:
            self.hand_values = []

    def __str__(self):
        return f"{self.name}: {[str(card) for card in self.hand]}"


class BlackjackDeck(Deck):
    def __init__(self):
        super().__init__()

    def deal_hands(self, players: list[Player]):
        for _ in range(2):
            for player in players:
                drawn_card = self.draw_card()
                player.hand.append(drawn_card)
                player.hand_values.append(get_card_value(drawn_card))

    def hit(self, player: Player):
        hit_card = self.draw_card()
        player.hand.append(hit_card)
        player.hand_values.append(get_card_value(hit_card))


def get_card_value(card: Card) -> int:
    # Face cards are worth 10, everything else is face value
    if card.value < 11:
        return card.value
    elif card.value == 14:
        return 11
    else:
        return 10
