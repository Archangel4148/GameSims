from euchre_tools import Player, Team, EuchreDeck, create_teams, evaluate_hand_winner, select_best_play

RUN_COUNT = 1

import concurrent.futures  # for parallel execution


# Function to run a single simulation
def run_game_simulation(num_teams: int, num_players: int):
    # Create new player, team, and deck objects for each simulation
    players: list[Player] = [Player(f"P{i + 1}", []) for i in range(num_players)]
    teams: list[Team] = create_teams(num_teams, players)
    deck = EuchreDeck()

    game_over = False
    player_hand_values = [0] * len(players)

    while not game_over:
        # Reset the game variables for each simulation
        for team in teams:
            team.tricks_taken = 0
        for player in players:
            player.hand_value = 0  # Reset player hand value

        # Re-deal and set trump suit
        deck.reset()
        deck.deal(5, players)
        trump_suit = deck.peek().suit

        # Initialize turn order
        turn_order = [0, 1, 2, 3]

        # Round loop (5 rounds per hand)
        for game_round in range(5):
            played_cards = []
            current_winner = None
            for turn_index, player_index in enumerate(turn_order):
                player = players[player_index]
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
                current_winner = evaluate_hand_winner(played_cards, trump_suit)

            # Determine trick taker and adjust turn order
            trick_taker = current_winner[1]
            trick_taker_index = players.index(trick_taker)
            turn_order = turn_order[trick_taker_index:] + turn_order[:trick_taker_index]

            # Update tricks taken for the team of the trick_taker
            trick_taker.team.tricks_taken += 1

        # Final scoring
        tricks_taken_by_team = [team.tricks_taken for team in teams]
        winning_index = tricks_taken_by_team.index(max(tricks_taken_by_team))
        winning_team = teams[winning_index]

        if winning_team.tricks_taken == 5:
            winning_team.score += 2
        else:
            winning_team.score += 1

        # Add player hand values to cumulative totals
        for i, player in enumerate(players):
            print("Adding", player.hand_value)
            player_hand_values[i] += player.hand_value
        print(player_hand_values)

        if winning_team.score >= 10:
            game_over = True

    team_scores = [team.score for team in teams]
    # Return the results: team scores, and player hand values to be used in aggregation
    return winning_index, team_scores, player_hand_values


# Main function using parallelism for simulations
def main():

    num_teams = 2
    num_players = 4

    team_scores = [0] * num_teams
    team_wins = [0] * num_teams
    player_hand_values = [0] * num_players

    # Use ThreadPoolExecutor to parallelize simulations
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(run_game_simulation, num_teams, num_players) for _ in range(RUN_COUNT)]

        # Collect and process results after all futures are done
        for future in concurrent.futures.as_completed(results):
            winning_team_index, team_scores_run, player_hand_values_run = future.result()

            # Accumulate team scores and wins
            for i, score in enumerate(team_scores_run):
                team_scores[i] += score

            # Track team wins based on the winning team
            team_wins[winning_team_index] += 1

            # Accumulate player hand values
            for i, hand_value in enumerate(player_hand_values_run):
                player_hand_values[i] += hand_value

    # Print results after all runs
    print("Number of Runs:", RUN_COUNT)
    for i in range(num_teams):
        print(f"Team {i+1} Average Score: {team_scores[i] / RUN_COUNT}")
        print(f"Team {i+1} Num Wins: {team_wins[i]}")
        print(f"Team {i+1} Win Percentage: {team_wins[i] / RUN_COUNT * 100}%\n")

    print(player_hand_values)
    for i in range(num_players):
        print(f"Player {i+1} Average Hand Value: {player_hand_values[i] / RUN_COUNT}")


if __name__ == '__main__':
    main()
