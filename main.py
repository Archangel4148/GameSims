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
            trump_suit = deck.peek().suit

            # Initial turn order (changes each round depending on who takes the trick)
            turn_order = [0, 1, 2, 3]

            # Round loop (Always 5 rounds for 5 cards/hand)
            for game_round in range(5):
                # print("=== Round", game_round + 1, "===")
                # print("Trump:", trump_suit)

                played_cards = []
                current_winner = None
                for turn_index, player_index in enumerate(turn_order):
                    player = players[player_index]
                    # Each player plays a card based on the state of the game on their turn
                    card = select_best_play(
                        hand=player.hand,
                        played_cards=played_cards,
                        leading_player=players[turn_order[0]],
                        trump_suit=trump_suit,
                        is_first_play=(turn_index == 0),
                        player_position=turn_index,
                        current_winner=current_winner,
                    )
                    player.hand.remove(card)
                    played_cards.append((card, player))
                    # print(f"{players[player_index].name} played the {played_cards[-1][0]}")

                    # Update the player that is "winning" after each card is played
                    current_winner = evaluate_hand_winner(played_cards, trump_suit)
                    # print("Current Winner:", current_winner[1].name)

                # After all players have played, the current winner takes the trick
                trick_taker = current_winner[1]
                trick_taker_index = players.index(trick_taker)

                # Update the turn order: trick taker goes first in the next round
                turn_order = turn_order[trick_taker_index:] + turn_order[:trick_taker_index]

                # Update tricks taken
                trick_taker.team.tricks_taken += 1

            # Decide which team took the most tricks
            tricks_taken_by_team = [team.tricks_taken for team in teams]
            winning_team = teams[tricks_taken_by_team.index(max(tricks_taken_by_team))]

            # Add detection for if a team was Euchred (lost 5-0), updating scores accordingly
            if winning_team.tricks_taken == 5:
                winning_team.score += 2
            else:
                winning_team.score += 1

            # If either team reaches 10 points, the game ends
            if max([team.score for team in teams]) >= 10:
                game_over = True

        # Update team wins
        teams_by_score = [team.score for team in teams]
        winning_team_index = teams_by_score.index(max(teams_by_score))
        team_wins[winning_team_index] += 1

        # Update team score and player hand values (for averaging)
        for i, team in enumerate(teams):
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
