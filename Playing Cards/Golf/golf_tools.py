import dataclasses
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    grid: list[Card | None] = None
    face_up_cards: list[bool] = None

    def __post_init__(self):
        self.grid = [None] * 6
        self.face_up_cards = [False] * 6

    def __str__(self):
        result = f"{self.name}:\n"
        cards_per_row = 3
        max_card_length = 20

        for i, card in enumerate(self.grid):
            card_string = f"{str(card)}({'^' if self.face_up_cards[i] else 'v'})"
            result += f"{card_string:<{max_card_length + 1}}"
            if (i + 1) % cards_per_row == 0:
                result += "\n"

        return result

    def print_grid(self, show_hidden=False):
        cards_per_row = 3
        max_card_length = 20
        result = ""
        for i, card in enumerate(self.grid):
            card_string = f"{str(card) if self.face_up_cards[i] or show_hidden else '|||||||||||||'}"
            result += f"{card_string:<{max_card_length + 1}}"
            if (i + 1) % cards_per_row == 0:
                result += "\n"
        print(result)

    def get_score(self, include_hidden=False):
        score = 0
        columns = [[], [], []]

        for i, card in enumerate(self.grid):
            if card is not None:
                if self.face_up_cards[i] or include_hidden:
                    columns[i % 3].append(card)  # Update the columns list
                    score += card.value
                    # If a column contains matching cards, cancel out both of them
                    if len(columns[i % 3]) == 2 and columns[i % 3][0].name == columns[i % 3][1].name:
                        score += -2 * columns[i % 3][0].value
        return score


class GolfDeck(Deck):
    def __init__(self):
        super().__init__()
        for card in self.cards:
            # Update the value of each card for Golf
            if card.value in (11, 12):
                card.value = 10
            elif card.value == 13:
                card.value = 0
            elif card.value == 14:
                card.value = 1
            elif card.value == 2:
                card.value = -2

    def deal_grids(self, players: list[Player]):
        for player in players:
            player.grid = []
        # Deal six cards to each player
        for i in range(6):
            for player in players:
                drawn_card = self.draw_card()
                player.grid.append(drawn_card)
