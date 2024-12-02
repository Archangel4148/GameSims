class Card:
    def __init__(self, suit_value: str):
        self.value: int = 0
        self.name: str = "NO_NAME"
        self.suit: str = "NO_SUIT"
        self.color: str = "NO_COLOR"

        value_string, suit_string = suit_value[0], suit_value[1]

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

    def get_full_card_name(self):
        return f"{self.name} of {self.suit}"


class Deck:
    def __init__(self):
        self.cards: list[Card]
