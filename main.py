from euchre_tools import Player, Team, EuchreDeck, create_teams
from playing_card_tools import Card, Deck


def main():
    # Create a Euchre deck (pre-shuffled)
    deck = EuchreDeck()

    # Create four players and assign them into teams of two
    players = [Player(f"P{i + 1}", []) for i in range(4)]
    teams = create_teams(2, players)

    # Deal a hand of five cards to each player
    deck.deal(5, players)

    # Display each team (team name and members/hands)
    for team in teams:
        print(team)


if __name__ == '__main__':
    main()
