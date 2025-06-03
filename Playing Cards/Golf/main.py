from random import randint

from golf_tools import Player, GolfDeck

if __name__ == '__main__':
    # Create players
    players = [Player(f"Player {i+1}") for i in range(4)]

    # Create a deck and deal the grids
    deck = GolfDeck()
    deck.deal_grids(players)

    # Discard the top card of the deck
    discard = deck.draw_card()

    for player in players:
        # Randomly select two cards to turn face-up
        positions = list(range(6))
        choices = [positions.pop(randint(0, len(positions)-1)), positions.pop(randint(0, len(positions)-1))]
        player.face_up_cards[choices[0]] = True
        player.face_up_cards[choices[1]] = True

        # Evaluate the player's score
        print("Score:", player.get_score(True))
        player.print_grid(True)