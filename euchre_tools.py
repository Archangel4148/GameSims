import dataclasses

from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None

    def __post_init__(self):
        if self.hand is None:
            self.hand = []

    def __str__(self):
        return f"{self.name}: {[str(card) for card in self.hand]}"


@dataclasses.dataclass
class Team:
    name: str
    members: list[Player]
    score = 0

    def __str__(self):
        return f"{self.name}: {', '.join(map(str, self.members))}"


class EuchreDeck(Deck):
    def __init__(self):
        euchre_deck_list = [
            "9S", "10S", "JS", "QS", "KS", "AS",
            "9C", "10C", "JC", "QC", "KC", "AC",
            "9D", "10D", "JD", "QD", "KD", "AD",
            "9H", "10H", "JH", "QH", "KH", "AH"
        ]
        super().__init__(standard_deck=False, deck_list=euchre_deck_list)

    def deal(self, num_cards: int, players: list[Player]):
        for _ in range(num_cards):
            for player in players:
                player.hand.append(self.draw_card())


def create_teams(num_teams: int, players: list[Player]):
    if len(players) > 4:
        raise ValueError("Too many players (maximum of 4)")
    return [Team(f"Team {i + 1}", players[i::num_teams]) for i in range(num_teams)]

def get_winning_card_index(played_cards: list[Card]):
    # For now, just returning the highest value card index
    value_list = [card.value for card in played_cards]

    return value_list.index(max(value_list))