from Blackjack.blackjack_tools import Player, BlackjackDeck, decide_play

PLAYER_COUNT = 8
VERBOSE = True


def main():
    # Create a list of players (and a dealer)
    dealer = Player(name="Dealer")
    players = [Player(f"Player {i + 1}") for i in range(PLAYER_COUNT)]

    # Create a deck and deal a hand to each player
    deck = BlackjackDeck()
    deck.deal_hands([dealer, *players])

    # Each player takes their turn, and then the dealer plays
    for player in (*players, dealer):
        vprint(f"{player} ({player.total_value})")
        while True:
            # Each player decides their play based on their hand and the dealer's upcard
            play = decide_play(player.hand_values, dealer.hand_values[0], player == dealer)
            if play == "hit":
                deck.hit(player)
                vprint(f"{player.name} hits, taking a {str(player.hand[-1])} ({player.total_value})")
            elif play == "stand":
                vprint(f"{player.name} stands with {player.total_value}.")
                break
            elif play == "bust":
                vprint(f"{player.name} busts, with a total of {player.total_value}.")
                player.total_value = 0
                break
        vprint()

    # Handling wins/losses
    winners = []
    pushes = []
    losers = []
    for player in players:
        # Compare each player with the dealer
        if player.total_value > dealer.total_value:
            # Player wins, add them to the list, along with if they were dealt a Blackjack
            winners.append((player.name, player.total_value == 21 and len(player.hand) == 2))
        elif player.total_value == dealer.total_value:
            # Hand is a push, no winner
            pushes.append(player.name)
        else:
            # Dealer wins
            losers.append(player.name)

    vprint(f"Winners: {winners}")
    vprint(f"Pushes: {pushes}")
    vprint(f"Losers: {losers}")


def vprint(text: str = ""):
    if VERBOSE:
        print(text)


if __name__ == '__main__':
    main()
