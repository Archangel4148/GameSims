from Blackjack.blackjack_tools import Player, BlackjackDeck
PLAYER_COUNT = 4


def main():
    # Create a list of players (and a dealer)
    dealer = Player(name="Dealer")
    players = [Player(f"Player {i + 1}") for i in range(PLAYER_COUNT)]

    # Create a deck and deal a hand to each player
    deck = BlackjackDeck()
    deck.deal_hands([dealer, *players])

    for player in (dealer, *players):
        print(player, player.hand_values)


if __name__ == '__main__':
    main()
