from collections import deque

from War.war_tools import WarDeck, Player, resolve_war


def run_simulation(player_count: int, round_threshold: int):
    # This simulation currently only supports 2 player games of War
    players = [Player(f"Player {i + 1}") for i in range(player_count)]

    # Create a deck and deal it evenly to both players
    deck = WarDeck()
    deck.deal(players)
    dealt_hands = [[str(card) for card in player.deck] for player in players]

    # Initialize result variables
    card_counts = [player.card_count for player in players]
    overall_winner = None
    rounds = 0
    war_count = 0
    player_wins = [0] * len(players)
    is_cyclic = False

    # Storage for game states to detect cycles
    seen_states = deque(maxlen=10000)

    while min(card_counts) > 0 and rounds < round_threshold:
        # Keep track of the current game state for cycle detection
        game_state = (tuple(players[0].deck), tuple(players[1].deck))

        if game_state in seen_states:
            is_cyclic = True
            return is_cyclic, players, dealt_hands, None, war_count, player_wins, rounds
        seen_states.append(game_state)

        rounds += 1
        # Each player plays a card from the top of their deck
        winning_card = None
        all_plays = []
        for player in players:
            played_card = player.deck.pop()
            player.card_count -= 1
            all_plays.append(played_card)

            if winning_card is None:
                winning_card = played_card
            elif played_card.value > winning_card.value:
                winning_card = played_card

        # Evaluate the winner and which cards they won
        if all_plays[0].value == all_plays[1].value:
            # Handle ties with a "War"
            war_count += 1
            war_winner, won_cards = resolve_war(players, all_plays)

        else:
            # Otherwise, simply list the winner
            war_winner = players[all_plays.index(winning_card)]
            won_cards = all_plays

        # Add the won cards to the bottom of the winner's deck
        war_winner.deck = won_cards + war_winner.deck
        war_winner.card_count += len(won_cards)
        player_wins[players.index(war_winner)] += 1

        # Update card counts for tracking
        card_counts = [player.card_count for player in players]
        if 0 in card_counts:
            overall_winner = war_winner

    return is_cyclic, players, dealt_hands, overall_winner, war_count, player_wins, rounds


if __name__ == "__main__":
    # Initialize resulting variables
    current_round_count = 0
    current_war_count = 0
    is_cyclic = None
    current_player_wins = None
    current_players = None
    current_winner = None
    dealt_hands = None
    game_number = 0
    round_threshold = 10000

    while current_round_count < round_threshold and not is_cyclic:
        is_cyclic, current_players, dealt_hands, current_winner, current_war_count, current_player_wins, current_round_count = run_simulation(
            2, round_threshold)
        game_number += 1

    if is_cyclic:
        print(f"\nDetected a cycle after {current_round_count} rounds. This game will never end.")
    else:
        print(f"\nGame number {game_number} ended after {current_round_count} rounds")
    print(f"War Count: {current_war_count}\n")
    print("=== Player Info ===", end="")
    for win_count, player, dealt_hand in zip(current_player_wins, current_players, dealt_hands):
        print(f"\n{player.name}: {win_count} wins")
        print(f"Dealt Hand: ({len(dealt_hand)}) {dealt_hand}")
    print("===================")

    if current_round_count == round_threshold:
        print(
            f"\nEnding simulation after game exceeded the threshold of {round_threshold} rounds without a winner.")
    elif not is_cyclic:
        print(f"\nFinal Winner: {current_winner.name}")
