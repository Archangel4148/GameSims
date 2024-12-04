import dataclasses
import random

from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None
    hand_value: int = 0
    team = None

    def __post_init__(self):
        if self.hand is None:
            self.hand = []

    def __str__(self):
        return f"{self.name}: {[str(card) for card in self.hand]}"

    def set_team(self, team):
        self.team = team


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
    teams = [Team(f"Team {i + 1}", players[i::num_teams]) for i in range(num_teams)]
    for team in teams:
        for player in team.members:
            player.set_team(team)
    return teams


def evaluate_hand_winner(played_cards: list[tuple[Card, Player]], trump_suit: str) -> tuple[Card, Player]:
    """For now, highest card wins"""

    # Get the effective value of each card
    relative_values = []
    for play in played_cards:
        card = play[0]
        if card.suit == trump_suit:
            relative_values.append(card.value + 6)
        else:
            relative_values.append(card.value)

    max_value_indices = [i for i, value in enumerate(relative_values) if value == max(relative_values)]

    if len(max_value_indices) == 1:
        # If there's only one winning card, return it
        return played_cards[max_value_indices[0]]
    else:
        # If there is a tie (Nobody plays trump), choose the winner at random
        return played_cards[random.choice(max_value_indices)]


def select_best_play(hand: list[Card], played_cards: list[tuple[Card, Player]], leading_player: Player,
                     trump_suit: str, is_first_play: bool, player_position: int,
                     current_winner: Player | None) -> Card:
    """
    Select the best card to play in the current trick of Euchre.

    Parameters:
    - hand: A list of Cards the player currently has.
    - played_cards: A list of Cards that have been played in the current trick.
    - leading_player: The Player who led the trick.
    - trump_suit: The current trump suit (if any).
    - first_round: Whether this is the first card being played in the round.
    - player_position: The current position of the player in the turn order.
    - current_winner: The Player who is currently winning the trick (if applicable).

    Returns:
    - The best Card to play from the hand.
    """

    trump_cards = [(i, card) for i, card in enumerate(hand) if card.suit == trump_suit]
    if trump_cards:
        trump_values = [trump[1].value for trump in trump_cards]
        trump_indices = [trump[0] for trump in trump_cards]
        max_index = trump_values.index(max(trump_values))
        play = hand[trump_indices[max_index]]
    else:
        play = random.choice(hand)

    return play
