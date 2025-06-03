import dataclasses
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    deck: list[Card] | None = None
    card_count: int = 0

    def __post_init__(self):
        self.deck = []

    def __str__(self):
        return f"{self.name}: ({self.card_count}) {[str(card) for card in self.deck] if self.deck else []}"


class WarDeck(Deck):
    def __init__(self):
        super().__init__()

    def deal(self, players: list[Player]):
        # Designate a "dealer" to ensure a random deal order
        dealer = random.randint(0, len(players) - 1)
        deal_order = players[dealer + 1:] + players[:dealer + 1]
        # Deal the entire deck one at a time
        for i in range(len(self.cards)):
            # Deal the top card of the deck
            card_dealt = self.draw_card()
            current_player = deal_order[i % len(players)]
            current_player.deck.append(card_dealt)
            current_player.card_count += 1


def resolve_war(players: list[Player], involved_cards: list[Card]) -> tuple[Player, list[Card]]:
    # Accumulate all cards involved in the war
    won_cards = involved_cards

    while True:
        played_cards = []

        for i, player in enumerate(players):
            # Check if the player can continue the war
            if player.card_count < 4:
                # If not, the other player wins and takes all remaining cards
                other_player = players[1 - i]
                won_cards += player.deck
                player.deck = []
                player.card_count = 0
                return other_player, won_cards

            # Each player places three face-down cards and one face-up card
            for _ in range(3):
                won_cards.append(player.deck.pop())
                player.card_count -= 1

            # Play the deciding card for the current war
            played_cards.append(player.deck.pop())
            player.card_count -= 1

        # Compare the face-up cards
        if played_cards[0] == played_cards[1]:
            # If there's a tie, add played cards to the pot and continue the loop
            won_cards += played_cards
        else:
            # Determine the winner based on the face-up cards
            card_values = [card.value for card in played_cards]
            winner = players[card_values.index(max(card_values))]
            won_cards += played_cards
            return winner, won_cards

