from Blackjack.blackjack_tools import Player, BlackjackDeck, decide_play, evaluate_result

PLAYER_COUNT = 4


def main():
    # Create a list of players (and a dealer)
    dealer = Player(name="Dealer")
    players = [Player(f"Player {i + 1}") for i in range(PLAYER_COUNT)]

    # Create a deck and deal a hand to each player
    deck = BlackjackDeck()
    deck.deal_hands([dealer, *players])

    # Each player takes their turn, and then the dealer plays
    for player in (*players, dealer):
        while True:
            print(player, f"({player.total_value})")
            # Each player decides their play based on their hand and the dealer's upcard
            play = decide_play(player.hand_values, dealer.hand_values[0], player == dealer)
            if play == "hit":
                deck.hit(player)
                print(f"{player.name} hits -> {str(player.hand[-1])} ({player.total_value})")
            elif play == "stand":
                print(f"{player.name} stands with {player.total_value}")
                score = evaluate_result(player)
                break
        print()


if __name__ == '__main__':
    main()
