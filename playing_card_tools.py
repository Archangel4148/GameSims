import random
from random import randint


class Card:
    def __init__(self, suit_value: str):
        self.value: int = 0
        self.name: str = "NO_NAME"
        self.suit: str = "NO_SUIT"
        self.color: str = "NO_COLOR"

        value_string, suit_string = suit_value[:-1], suit_value[-1]

        try:
            self.value = int(value_string)
            self.name = value_string
        except ValueError:
            face_cards = ("J", "Q", "K", "A")
            face_card_names = ("Jack", "Queen", "King", "Ace")
            self.value = face_cards.index(value_string) + 11
            self.name = face_card_names[face_cards.index(value_string)]

        suits = ("S", "C", "D", "H")
        suit_names = ("Spades", "Clubs", "Diamonds", "Hearts")
        try:
            self.suit = suit_names[suits.index(suit_string)]
            self.color = "Black" if self.suit in ("Spades", "Clubs") else "Red"
        except ValueError:
            raise ValueError(f"Invalid Suit, \'{suit_string}\'")

    def __str__(self):
        # Return the full card name when printing the Card object
        return f"{self.name} of {self.suit}"


class Deck:
    def __init__(self, standard_deck: bool = True, deck_list: list | None = None):
        self.cards: list[Card] = []
        self.deck_list: list[str] = []

        if standard_deck:
            values = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
            suits = ("S", "C", "D", "H")

            # Generate the full deck of 52 cards
            self.deck_list = [f"{value}{suit}" for value in values for suit in suits]
        else:
            self.deck_list = deck_list

        # Fill the deck with cards, and shuffle it to start
        self.fill(self.deck_list)
        self.shuffle()

    def fill(self, deck_list: list[str]):
        self.cards = [Card(s) for s in deck_list]

    def reset(self):
        """Resets the deck to its original deck list, and reshuffles"""
        self.fill(self.deck_list)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        """Draws and returns the top card of the deck"""
        try:
            return self.cards.pop()
        except IndexError:
            raise IndexError("Trying to draw a card from an empty deck")

    def peek(self):
        if len(self.cards) > 0:
            return self.cards[-1]
        else:
            return "There aren't any cards in the deck to look at"

    def __str__(self):
        return "\n".join([str(card) for card in self.cards])
