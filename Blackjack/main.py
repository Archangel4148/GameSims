from Blackjack.blackjack_tools import Player

PLAYER_COUNT = 4


def main():
    dealer = Player(name="Dealer")
    players = [Player(f"Player {i + 1}") for i in range(PLAYER_COUNT)]

    for player in (dealer, *players):
        print(player)


if __name__ == '__main__':
    main()
