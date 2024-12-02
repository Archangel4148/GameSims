from euchre_tools import Player, Team, EuchreDeck
from playing_card_tools import Card, Deck


def main():
    # Create a Euchre deck (pre-shuffled)
    deck = EuchreDeck()

    players = [Player("P1", []), Player("P2", []), Player("P3", []), Player("P4", [])]
    teams = [Team(players[0:2], "Team 1"), Team(players[2:], "Team 2")]


if __name__ == '__main__':
    main()
