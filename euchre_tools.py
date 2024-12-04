import dataclasses

from playing_card_tools import Card, Deck


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


@dataclasses.dataclass
class Team:
    name: str
    members: list[Player]
    tricks_taken: int = 0
    score: int = 0

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
                card = self.draw_card()
                player.hand.append(card)
                player.hand_value += card.value



def create_teams(num_teams: int, players: list[Player]):
    if len(players) > 4:
        raise ValueError("Too many players (maximum of 4)")
    return [Team(f"Team {i + 1}", players[i::num_teams]) for i in range(num_teams)]

def get_winning_card_index(played_cards: list[Card]):
    """For now, highest card wins"""

    # Get the list of indices where the max value appears
    value_list = [card.value for card in played_cards]
    max_value_indices = [i for i, value in enumerate(value_list) if value == max(value_list)]

    if len(max_value_indices) == 1:
        # If there's only one winning card, return it
        return max_value_indices[0]

    # Otherwise, use the suit as a tie-breaker
    suit_priority = {'Spades': 4, 'Clubs': 3, 'Diamonds': 2, 'Hearts': 1}

    # Sort the tied cards by their suit priority (highest priority wins)
    sorted_tied_cards = sorted(
        [played_cards[i] for i in max_value_indices],
        key=lambda card: suit_priority[card.suit],
        reverse=True
    )

    # Return the index of the card with the highest suit priority
    return played_cards.index(sorted_tied_cards[0])