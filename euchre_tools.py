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

    def get_strongest_suit(self) -> tuple[str, int]:
        # Define a dictionary to hold the strength of each suit if it were trump
        suit_strength = {
            "Spades": 0,
            "Clubs": 0,
            "Diamonds": 0,
            "Hearts": 0
        }

        # Evaluate the strength for each suit
        for suit in suit_strength:
            for card in self.hand:
                # We pass the current suit as the trump suit to get the relative value of each card
                suit_strength[suit] += get_relative_value(card, suit)

        # Find the suit with the highest strength
        strongest_suit = max(suit_strength, key=suit_strength.get)

        return strongest_suit, suit_strength[strongest_suit]


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
        # Deal <num_cards> cards to each player
        for _ in range(num_cards):
            for player in players:
                card = self.draw_card()
                player.hand.append(card)
                # Update player's suit count and hand value
                player.suit_count[card.suit] += 1
                player.hand_value += card.value


def create_teams(num_teams: int, players: list[Player]):
    # Separate players into <num_teams> teams
    if len(players) > 4:
        raise ValueError("Too many players (maximum of 4)")
    teams = [Team(f"Team {i + 1}", players[i::num_teams]) for i in range(num_teams)]
    for team in teams:
        for player in team.members:
            player.set_team(team)
    return teams


def get_relative_value(card: Card, trump_suit: str) -> int:
    # Get the relative value of a card based on the trump suit
    suit_pairs = {"Spades": "Clubs", "Clubs": "Spades", "Hearts": "Diamonds", "Diamonds": "Hearts"}
    relative_value = card.value

    if card.suit == trump_suit:
        relative_value += 6
        if card.value == 11:
            relative_value += 5
    elif card.suit == suit_pairs[trump_suit] and card.value == 11:
        relative_value += 10

    return relative_value


def evaluate_hand_winner(played_cards: list[tuple[Card, Player]]) -> tuple[Card, Player]:
    """Returns the card that won the trick and the player who played it."""

    card_values = [card.value for card, _ in played_cards]

    # Find the index of the card with the highest value
    max_value_index = card_values.index(max(card_values))

    return played_cards[max_value_index]


def select_best_play(hand: list[Card], suit_count: dict[str, int], plays_made: list[tuple[Card, Player]],
                     leading_player: Player,
                     trump_suit: str, is_first_play: bool, player_position: int,
                     current_winner: Player | None) -> Card:
    """
    Select the best card to play in the current trick of Euchre.

    Parameters:
    - hand: A list of Cards the player currently has
    - suit_count: A dictionary of the number of cards of each suit in the player's hand
    - played_cards: A list of Cards that have been played in the current trick
    - leading_player: The Player who led the trick
    - trump_suit: The current trump suit (if any)
    - first_round: Whether this is the first card being played in the round
    - player_position: The current position of the player in the turn order
    - current_winner: The Player who is currently winning the trick (if applicable)

    Returns:
    - The best card to play from the hand (Card object)
    """

    hand_values = [card.value for card in hand]

    if not is_first_play:
        matching_cards = [(i, card) for i, card in enumerate(hand) if card.suit == plays_made[0][0].suit]
    else:
        matching_cards = []

    # Get a list of trump cards (including the off-suit left bower)
    trump_cards = [(i, card) for i, card in enumerate(hand) if card.value >= 15]

    # print("Trump suit:", trump_suit)
    # print("Hand:", [str(card) for card in hand])
    # print("Trump cards:", [str(card) for card, _ in trump_cards])
    # print("Matching cards:", [str(card) for card, _ in matching_cards])

    # Logic for leading player
    if is_first_play:
        # Play the highest card that isn't trump, unless it is the right bower
        non_trump_cards = [(i, card) for i, card in enumerate(hand) if card.value < 15]
        has_right_bower = hand_values.count(22) == 1

        if has_right_bower:
            # Lead with the right bower if you have it (Guaranteed win)
            play = hand[hand_values.index(22)]
        elif non_trump_cards:
            # Play the highest non-trump card
            non_trump_values = [card.value for _, card in non_trump_cards]
            play_index = non_trump_values.index(max(non_trump_values))
            play = hand[non_trump_cards[play_index][0]]
        else:
            # If there are no non-trump cards, play the highest trump
            play = hand[hand_values.index(max(hand_values))]
    else:
        # Logic for all other players
        if matching_cards:
            # You must match suit, if possible
            matching_values = [match[1].value for match in matching_cards]
            matching_indices = [match[0] for match in matching_cards]
            # If your match is higher than the highest card played, play it
            if max(matching_values) > max([card.value for card, _ in plays_made]):
                play_index = matching_values.index(max(matching_values))
            # Otherwise, play your lowest matching card
            else:
                play_index = matching_values.index(min(matching_values))

            play = hand[matching_indices[play_index]]
        elif trump_cards:
            # If you cannot match suit, play trump
            trump_values = [trump[1].value for trump in trump_cards]
            trump_indices = [trump[0] for trump in trump_cards]

            # If your trump is higher than the highest card played, play it
            if max(trump_values) > max([card.value for card, _ in plays_made]):
                play_index = trump_values.index(max(trump_values))
                play = hand[trump_indices[play_index]]
            else:
                # If your trump still can't win, play a trash card from your hand
                play = hand[hand_values.index(min(hand_values))]

        else:
            # If you can't match suit or play trump, throw out a trash card
            play = hand[hand_values.index(min(hand_values))]
            # Cards that don't match suit or trump are worthless
            play.value = 0

    # print(f"Play: {play} ({play.value})")
    return play


def decide_trump(shown_card: Card, players: list[Player], dealer: Player) -> str:
    """
    Decide the trump suit for the round based on the shown (flipped) card and player decisions.

    Arguments:
    - shown_card: The card flipped from the kitty, a Card object.
    - players: A list of Player objects, including the dealer.
    - dealer: The Player object representing the dealer.

    Returns:
    - trump_suit: The chosen trump suit as a string.
    """

    # Identify the suit of the shown card
    shown_suit = shown_card.suit

    # The player to the left of the dealer starts the decision process
    start_index = (players.index(dealer) + 1) % len(players)

    # Initialize trump_suit to None
    trump_suit = None
    passed_players = []

    print("Dealer:", dealer.name)
    print("Flipped Card:", shown_card)

    # Go around the table and let players decide whether to pass or have the dealer pick up the card
    for i in range(len(players)):
        current_player = players[(start_index + i) % len(players)]
        goal_suit, goal_strength = current_player.get_strongest_suit()

        if shown_suit == goal_suit:
            print(f"{current_player.name} decides trump to be {shown_suit}")
            return shown_suit
        else:
            print(f"{current_player.name} passes ({goal_suit})")

    print("Nobody wanted", shown_suit, "to be trump...")

    # Go around the table again and allow players to choose trump
    for i in range(len(players)):
        current_player = players[(start_index + i) % len(players)]
        goal_suit, goal_strength = current_player.get_strongest_suit()

        # Player decides to choose trump based on their current hand (dealer must choose if it makes it back to them)
        if goal_strength > 10 or i == len(players) - 1:
            print(f"{current_player.name} chooses {goal_suit} ({goal_strength})")
            return goal_suit
        else:
            # If a player's hand is too bad, just pass (no specific suit would win them the round)
            print(f"{current_player.name} passes ({goal_strength})")
