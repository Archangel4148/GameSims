from euchre_tools import Player, Team, EuchreDeck, create_teams, get_winning_card_index


def main():
    # Create a Euchre deck (pre-shuffled)
    deck = EuchreDeck()

    # Create four players and assign them into teams of two
    players: list[Player] = [Player(f"P{i + 1}", []) for i in range(4)]
    teams: list[Team] = create_teams(2, players)

    scores = [0] * len(teams)
    wins = [0] * len(teams)
    num_runs = 10000

    for _ in range(num_runs):

        deck.reset()

        game_over = False

        while not game_over:
            for team in teams:
                team.tricks_taken = 0
            # Re-deal
            deck.reset()
            deck.deal(5, players)

            # Keep track of turn order (changes each round depending on who takes the trick)
            turn_order = [0, 1, 2, 3]

            # Round loop (Always 5 rounds for 5 cards/hand
            for turn in range(5):
                # print("=== Round", turn + 1, "===")
                played_cards = []
                for player_index in turn_order:
                    played_cards.append(players[player_index].hand.pop())
                    # print(f"{players[player_index].name} played the {played_cards[-1]}")

                winner = players[get_winning_card_index(played_cards)]
                for team in teams:
                    if winner in team.members:
                        team.tricks_taken += 1
                        # print(team.name, "takes the trick!\n")
                        break

            tricks_taken_by_team = [team.tricks_taken for team in teams]
            winning_team = teams[tricks_taken_by_team.index(max(tricks_taken_by_team))]
            if winning_team.tricks_taken == 5:
                winning_team.score += 2
                # print(f"-- {winning_team.name} gets 2 points ({winning_team.score}) --\n")
            else:
                winning_team.score += 1
                # print(f"-- {winning_team.name} gets 1 point ({winning_team.score}) --\n")

            if max([team.score for team in teams]) >= 10:
                game_over = True

        teams_by_score = [team.score for team in teams]
        winner = teams_by_score.index(max(teams_by_score))
        wins[winner] += 1
        for i, team in enumerate(teams):
            # print(team.name, "-", team.score)
            scores[i] += team.score
            team.score = 0

    # Print the results of the games
    print("Number of Runs:", num_runs)
    for i, team in enumerate(teams):
        print(f"{team.name} Average Score: {scores[i] / num_runs}")
        print(f"{team.name} Num Wins: {wins[i]}")
        print(f"{team.name} Win Percentage: {wins[i] / num_runs * 100}%\n")

if __name__ == '__main__':
    main()
