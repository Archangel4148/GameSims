import dataclasses

from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None
    hand_value: int = 0
    suit_count: dict[str, int] | None = None
    team = None

    def __post_init__(self):
        if self.hand is None:
            self.hand = []
        if self.suit_count is None:
            self.suit_count = {
                "Spades": 0,
                "Clubs": 0,
                "Diamonds": 0,
                "Hearts": 0
            }

    def __str__(self):
        return f"{self.name}: {[str(card) for card in self.hand]}"

    def set_team(self, team):
        self.team = team


class SpadesDeck(Deck):
    def __init__(self):
        super().__init__()

    def deal(self, players: list[Player]):
        # Deal the entire deck one at a time
        for i in range(len(self.cards)):
            # Deal the top card of the deck
            card_dealt = self.draw_card()
            current_player = players[i % len(players)]
            current_player.hand.append(card_dealt)

            # Update player's suit count and hand value
            current_player.suit_count[card_dealt.suit] += 1
            current_player.hand_value += card_dealt.value
