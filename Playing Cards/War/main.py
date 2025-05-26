import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed

from War.war_tools import WarDeck, Player, resolve_war


def run_simulation(player_count: int, round_threshold: int, swap_order: bool = False):
    # Initialize players
    players = [Player(f"Player {i + 1}") for i in range(player_count)]
    deck = WarDeck()
    deck.deal(players)

    # If swapping order, reverse the player list
    if swap_order:
        players = players[::-1]

    card_counts = [player.card_count for player in players]
    rounds = 0
    war_count = 0
    player_wins = [0] * len(players)
    is_cyclic = False
    seen_states = deque(maxlen=10000)

    while min(card_counts) > 0 and rounds < round_threshold:
        game_state = (hash(tuple(players[0].deck)), hash(tuple(players[1].deck)))

        if game_state in seen_states:
            is_cyclic = True
            return is_cyclic, rounds, None
        seen_states.append(game_state)

        rounds += 1
        all_plays = []
        for player in players:
            played_card = player.deck.pop()
            player.card_count -= 1
            all_plays.append(played_card)

        if all_plays[0].value == all_plays[1].value:
            war_count += 1
            war_winner, won_cards = resolve_war(players, all_plays)
        else:
            winning_card = max(all_plays, key=lambda card: card.value)
            war_winner = players[all_plays.index(winning_card)]
            won_cards = all_plays

        war_winner.deck = won_cards + war_winner.deck
        war_winner.card_count += len(won_cards)
        player_wins[players.index(war_winner)] += 1
        card_counts = [player.card_count for player in players]

    # Return winner index after swapping back if necessary
    winner_index = players.index(max(players, key=lambda player: player.card_count))
    return is_cyclic, rounds, (1 - winner_index if swap_order else winner_index)


def simulate_games_parallel(games_to_simulate, round_threshold):
    results = {"win": 0, "cyclic": 0, "rounds": 0, "player_wins": [0] * 2, "round_counts": []}

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(run_simulation, 2, round_threshold, game_index % 2 == 1)
            for game_index in range(games_to_simulate)
        ]

        for future in as_completed(futures):
            is_cyclic, rounds, winner_index = future.result()
            results["rounds"] += rounds
            if is_cyclic:
                results["cyclic"] += 1
            else:
                results["win"] += 1
                results["round_counts"].append(rounds)  # Record round count if not cyclic

            if winner_index is not None:
                results["player_wins"][winner_index] += 1

    # Calculate max and min round counts for games that aren't cyclic
    if results["round_counts"]:
        results["max_rounds"] = max(results["round_counts"])
        results["min_rounds"] = min(results["round_counts"])
    else:
        results["max_rounds"] = results["min_rounds"] = 0  # No non-cyclic games

    return results


if __name__ == "__main__":
    ROUND_THRESHOLD = 10000
    GAMES_TO_SIMULATE = 10000

    print(f"Simulating {GAMES_TO_SIMULATE} games with a threshold of {ROUND_THRESHOLD} rounds...")
    start_time = time.time()

    results = simulate_games_parallel(GAMES_TO_SIMULATE, ROUND_THRESHOLD)

    time_elapsed = time.time() - start_time
    print(f"\nSimulation completed in {time_elapsed:.2f} seconds.\n")

    print(f"Games Simulated: {GAMES_TO_SIMULATE}")
    print(f"Win Count: {results['win']}")
    print(f"Cycle Count: {results['cyclic']}")
    print(f"Win Percentage: {results['win'] / GAMES_TO_SIMULATE * 100}%")
    print(f"Cycle Percentage: {results['cyclic'] / GAMES_TO_SIMULATE * 100}%")

    print(f"\n=== Player Statistics ===")
    for i, player_win_count in enumerate(results["player_wins"]):
        print(f"Player {i + 1}: {player_win_count} wins ({player_win_count / GAMES_TO_SIMULATE * 100}%)")
    print(f"\nAverage Rounds: {results['rounds'] / GAMES_TO_SIMULATE}")
    print(f"Maximum Rounds (excluding cycles): {results['max_rounds']}")
    print(f"Minimum Rounds (excluding cycles): {results['min_rounds']}")
