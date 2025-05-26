import dataclasses

from playing_card_tools import Card, Deck


@dataclasses.dataclass
class Player:
    name: str = "NO_NAME"
    hand: list[Card] | None = None
    hand_values: list[int] | None = None
    total_value: int = 0

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
        for i in range(2):
            for player in players:
                drawn_card = self.draw_card()
                player.hand.append(drawn_card)
                player.hand_values.append(get_card_value(drawn_card))
                player.total_value = sum(player.hand_values)
                # If a player is dealt two Aces, treat one of them as a 1
                if player.total_value == 22:
                    player.hand_values[i] = 1
                    player.total_value -= 10

    def hit(self, player: Player):
        hit_card = self.draw_card()
        player.hand.append(hit_card)
        player.hand_values.append(get_card_value(hit_card))
        player.total_value = sum(player.hand_values)
        # Handle Aces ("soft hands")
        if player.total_value > 21 and 11 in player.hand_values:
            player.hand_values[player.hand_values.index(11)] = 1
            player.total_value = sum(player.hand_values)


def get_card_value(card: Card) -> int:
    # Face cards are worth 10, everything else is face value
    if card.value < 11:
        return card.value
    elif card.value == 14:
        return 11
    else:
        return 10


def decide_play(hand_values: list[int], dealer_upcard: int, is_dealer: bool = False) -> str:
    hand_total = sum(hand_values)  # Sum of the player's hand cards

    if not is_dealer:
        # Player's decision-making
        if hand_total <= 11:
            # Player will always hit if their total is 11 or less (no risk)
            return "hit"
        elif hand_total > 21:
            return "bust"
        elif hand_total >= 17:
            # Player will stand on 17 or more (safe enough not to bust)
            return "stand"
        elif hand_total == 12:
            # Special case: Player stands on 12 if the dealer's upcard is 4, 5, or 6
            if dealer_upcard in [4, 5, 6]:
                return "stand"
            else:
                return "hit"
        elif 13 <= hand_total <= 16:
            # Player will hit on 13-16 if the dealer's upcard is 7 or higher, otherwise stand
            if dealer_upcard >= 7:
                return "hit"
            else:
                return "stand"
        else:
            return "stand"  # Catch-all for any other unexpected scenarios
    else:
        # Dealer's decision-making (house rules)
        if hand_total <= 16:
            return "hit"
        elif hand_total > 21:
            return "bust"
        else:
            return "stand"
