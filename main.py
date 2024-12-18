import concurrent.futures
from random import randint

from euchre_tools import Player, Team, EuchreDeck, create_teams, evaluate_hand_winner, select_best_play, \
    get_relative_value, decide_trump

VERBOSE = False
RUN_COUNT = 10000  # Number of full games to simulate

if VERBOSE and RUN_COUNT > 1:
    RUN_COUNT = 1


# Function to run a single simulation
def run_game_simulation(num_teams: int, num_players: int):
    # Create new player, team, and deck objects for each simulation
    players: list[Player] = [Player(f"P{i + 1}", []) for i in range(num_players)]
    teams: list[Team] = create_teams(num_teams, players)
    deck = EuchreDeck()
    if VERBOSE:
        print("Teams:")
        for team in teams:
            print(team)
        print()

    game_over = False
    player_hand_values = [0] * len(players)
    rounds_played = 0
    winning_index = None

    # Select a random dealer
    dealer = randint(0, 3)

    # The player to the left of the dealer starts play
    leader = (dealer + 1) % 4

    # Game loop (Keep playing until a team wins 10 points)
    while not game_over:
        if VERBOSE:
            print("=== Round", rounds_played + 1, "===")
        # Reset the game variables for each simulation
        for team in teams:
            team.tricks_taken = 0
        for player in players:
            player.hand_value = 0  # Reset player hand values

        # Re-deal
        deck.reset()
        deck.deal(5, players)

        # Select trump
        trump_suit = decide_trump(deck.peek(), players, players[dealer % 4], VERBOSE)
        if VERBOSE:
            print(f"\nTrump: {trump_suit}\n")

        # Update player hand and card values based on trump suit
        for player in players:
            for card in player.hand:
                card.value = get_relative_value(card, trump_suit)
            player.hand_value = sum(card.value for card in player.hand)

        rounds_played += 1
        dealer += 1

        # Round loop (5 plays per hand)
        for game_round in range(5):
            plays = []
            current_winner = None

            # Set turn order based on the current leader
            turn_order = [leader, (leader + 1) % 4, (leader + 2) % 4, (leader + 3) % 4]

            for turn_index, player_index in enumerate(turn_order):
                # Player turn (Select best card to play)
                player = players[player_index]
                card = select_best_play(
                    hand=player.hand,
                    suit_count=player.suit_count,
                    plays_made=plays,
                    leading_player=players[turn_order[0]],
                    trump_suit=trump_suit,
                    is_first_play=(turn_index == 0),
                    player_position=turn_index,
                    current_winner=current_winner,
                )

                if VERBOSE:
                    print(player)
                    print(f"{player.name} plays the {card}\n")

                # Play the card
                player.hand.remove(card)
                player.suit_count[card.suit] -= 1
                plays.append((card, player))

                # Update current winner
                current_winner = evaluate_hand_winner(plays)

            # Determine trick taker and adjust turn order
            trick_taker = current_winner[1]
            trick_taker_index = players.index(trick_taker)
            leader = trick_taker_index

            # Update tricks taken for the team of the trick_taker
            trick_taker.team.tricks_taken += 1

            # print(f"Trick taker: {trick_taker.name}\n====================\n")

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
            player_hand_values[i] += player.hand_value

        if winning_team.score >= 10:
            game_over = True

    team_scores = [team.score for team in teams]
    player_hand_values = [hand_value / rounds_played for hand_value in player_hand_values]

    # Return team scores and player hand values to be used in aggregation
    return winning_index, team_scores, player_hand_values


# Main function using parallelism for simulations
def main():
    num_teams = 2
    num_players = 4

    # Initialize cumulative totals
    cumulative_team_scores = [0] * num_teams
    cumulative_team_wins = [0] * num_teams
    cumulative_player_hand_values = [0] * num_players
    cumulative_score_combo_counts = {}

    # Use ThreadPoolExecutor to parallelize simulations
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(run_game_simulation, num_teams, num_players) for _ in range(RUN_COUNT)]

        # Collect and process results after all simulations are done
        for future in concurrent.futures.as_completed(results):
            winning_team_index, team_scores_run, player_hand_values_run = future.result()

            # Accumulate team scores and wins
            for i, score in enumerate(team_scores_run):
                cumulative_team_scores[i] += score
            # Accumulate team score combo
            team_scores_run.sort()
            score_combo = "-".join(map(str, team_scores_run))
            try:
                cumulative_score_combo_counts[score_combo] += 1
            except KeyError:
                cumulative_score_combo_counts[score_combo] = 1

            # Accumulate team wins based on the winning team
            cumulative_team_wins[winning_team_index] += 1

            # Accumulate player hand values
            for i, hand_value in enumerate(player_hand_values_run):
                cumulative_player_hand_values[i] += hand_value

    # Print results after all runs
    print("Number of Runs:", RUN_COUNT, "\n")
    for i in range(num_teams):
        print(f"Team {i + 1} Average Score: {cumulative_team_scores[i] / RUN_COUNT}")
        print(f"Team {i + 1} Total Wins: {cumulative_team_wins[i]}")
        print(f"Team {i + 1} Win Percentage: {cumulative_team_wins[i] / RUN_COUNT * 100}%\n")

    # Sort the score combos by occurrence in descending order
    most_common_combos = sorted(cumulative_score_combo_counts, key=cumulative_score_combo_counts.get, reverse=True)

    # Get the top 3 most common combos
    top_three_combos = most_common_combos[:3]

    # Print the top 3 most common score combos and their occurrences
    print("Top 3 most common score combinations:")
    for i, combo in enumerate(top_three_combos):
        print(f"{i+1}. {combo} with {cumulative_score_combo_counts[combo]} occurrences")
    print()

    for i in range(num_players):
        print(f"Player {i + 1} Average Hand Value: {cumulative_player_hand_values[i] / RUN_COUNT}")


if __name__ == '__main__':
    main()
