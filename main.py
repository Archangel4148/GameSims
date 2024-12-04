from euchre_tools import Player, Team, EuchreDeck, create_teams, evaluate_hand_winner, select_best_play

RUN_COUNT = 1000

def main():
    # Create a Euchre deck (pre-shuffled)
    deck = EuchreDeck()

    # Create four players and assign them into teams of two
    players: list[Player] = [Player(f"P{i + 1}", []) for i in range(4)]
    teams: list[Team] = create_teams(2, players)

    # Tracking averages for post-analysis
    team_scores = [0] * len(teams)
    team_wins = [0] * len(teams)
    player_hand_values = [0] * len(players)

    for _ in range(RUN_COUNT):
        # Reset the deck before each game
        deck.reset()
        game_over = False

        # Game loop
        while not game_over:
            for team in teams:
                team.tricks_taken = 0
            for player in players:
                player.hand_value = 0
            # Re-deal
            deck.reset()
            deck.deal(5, players)

            # Initial turn order (changes each round depending on who takes the trick)
            turn_order = [0, 1, 2, 3]

            # Round loop (Always 5 rounds for 5 cards/hand
            for game_round in range(5):
                # print("=== Round", game_round + 1, "===")
                played_cards = []
                current_winner = None
                for turn_index, player_index in enumerate(turn_order):
                    player = players[player_index]
                    # Each player makes a play based on the state of the game on their turn
                    card = select_best_play(
                        hand=player.hand,
                        played_cards=played_cards,
                        leading_player=players[turn_order[0]],
                        trump_suit="NOT IMPLEMENTED YET",
                        is_first_play=(turn_index == 0),
                        player_position=turn_index,
                        current_winner=current_winner,
                    )
                    player.hand.remove(card)
                    played_cards.append((card, player))
                    # print(f"{players[player_index].name} played the {played_cards[-1][0]}")

                    current_winner = evaluate_hand_winner(played_cards)
                    # print("Current Winner:", current_winner[1].name)

                winner = current_winner[1]

                # Update the turn order: winner goes first in the next round
                winner_index = players.index(winner)
                turn_order = turn_order[winner_index:] + turn_order[:winner_index]

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
        team_wins[winner] += 1
        for i, team in enumerate(teams):
            # print(team.name, "-", team.score)
            team_scores[i] += team.score
            team.score = 0
        for i, player in enumerate(players):
            player_hand_values[i] += player.hand_value

    # Print the results of the games
    print("Number of Runs:", RUN_COUNT)
    for i, team in enumerate(teams):
        print(f"{team.name} Average Score: {team_scores[i] / RUN_COUNT}")
        print(f"{team.name} Num Wins: {team_wins[i]}")
        print(f"{team.name} Win Percentage: {team_wins[i] / RUN_COUNT * 100}%\n")

    for i, player in enumerate(players):
        print(f"{player.name} Average Hand Value: {player_hand_values[i] / RUN_COUNT}")

if __name__ == '__main__':
    main()
