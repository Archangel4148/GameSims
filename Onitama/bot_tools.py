import math
import random

from Onitama.game_tools import BoardState, get_valid_targets_by_card, mailbox_to_coord, is_victory, \
    apply_move, PLAYABLE_INDICES


def get_valid_moves_for_piece(board_state: BoardState, start_idx) -> list[tuple[int, int, str]]:
    valid_moves = []
    player_hand = board_state.p1_cards if board_state.is_p1_turn else board_state.p2_cards
    space = board_state.mailbox_board[start_idx]

    if space is None or space == "." or space.islower() != board_state.is_p1_turn:
        return []
    for card in player_hand:
        valid_targets = get_valid_targets_by_card(board_state, start_idx, card)
        for target in valid_targets:
            valid_moves.append((start_idx, target, card))

    return valid_moves


def get_all_valid_moves(board_state: BoardState) -> list[tuple[int, int, str]]:
    valid_moves = []
    for i in PLAYABLE_INDICES:
        valid_moves += get_valid_moves_for_piece(board_state, i)
    return valid_moves


def evaluate_heuristic(state: BoardState, precomputed_moves: list[tuple[int, int, str]] = None) -> float:
    evaluation = 0
    for i in PLAYABLE_INDICES:
        space = state.mailbox_board[i]
        if space == ".":
            continue

        is_mine = space.islower() == state.is_p1_turn

        # Count material
        space_value = 100 if space in "sS" else 500
        evaluation += space_value if is_mine else -space_value

        # Reward master proximity to the goal
        if space.lower() == "m" and is_mine:
            row, col = mailbox_to_coord(i)
            temple_dist = abs(row - (0 if not state.is_p1_turn else 4))
            evaluation += (4 - temple_dist) * 25

        # Reward student advancement
        if space in "sS" and is_mine:
            row, _ = mailbox_to_coord(i)
            forwardness = row if state.is_p1_turn else (4 - row)
            evaluation += forwardness * 5

    # Reward mobility
    if precomputed_moves is None:
        precomputed_moves = get_all_valid_moves(state)
    num_moves = len(precomputed_moves)
    evaluation += min(5, num_moves) * 6

    # Reward threats on opponent pieces
    for move in precomputed_moves:
        from_idx, to_idx, _ = move
        target_piece = state.mailbox_board[to_idx]
        if target_piece and target_piece != ".":
            if target_piece.islower() != state.is_p1_turn:
                evaluation += 30 if target_piece in "sS" else 80

    return evaluation


def evaluate_terminal(state: BoardState, depth: int, precomputed_moves=None) -> float:
    win, message = is_victory(state)
    if not win:
        return evaluate_heuristic(state, precomputed_moves)
    score = 100000 + depth
    # If the player whose turn it was just lost, this is bad for them
    if ("Player 1 wins" in message and state.is_p1_turn) or ("Player 2 wins" in message and not state.is_p1_turn):
        return score
    else:
        return -score


def is_test_end(state: BoardState, depth: int) -> bool:
    return is_victory(state)[0] or depth == 0


def max_value(state: BoardState, alpha: float, beta: float, depth: int) -> float:
    # Get and order legal moves for optimal a-b pruning
    legal_moves = get_all_valid_moves(state)
    # legal_moves.sort(key=lambda move: -evaluate_heuristic(apply_move(state, move)), reverse=True)
    if is_test_end(state, depth):
        return evaluate_terminal(state, depth, legal_moves)
    v = -math.inf
    for move in legal_moves:
        v = max(v, min_value(apply_move(state, move), alpha, beta, depth - 1))
        alpha = max(alpha, v)
        if v >= beta:
            break
    return v


def min_value(state: BoardState, alpha: float, beta: float, depth: int) -> float:
    # Get and order legal moves for optimal a-b pruning
    legal_moves = get_all_valid_moves(state)
    # legal_moves.sort(key=lambda move: -evaluate_heuristic(apply_move(state, move)), reverse=True)

    if is_test_end(state, depth):
        return evaluate_terminal(state, depth, legal_moves)
    v = math.inf
    for move in legal_moves:
        v = min(v, max_value(apply_move(state, move), alpha, beta, depth - 1))
        beta = min(beta, v)
        if v <= alpha:
            break
    return v


def depth_limited_alpha_beta_id_minimax(state: BoardState) -> tuple[int, int, str]:
    depth = 1
    target_depth = 4
    best_move = None
    # print("Starting minimax...")
    # Iterative deepening
    while depth <= target_depth:
        # print("Search depth:", depth)
        best_score = -math.inf
        best_moves = []
        # Find the move with the best score
        for move in get_all_valid_moves(state):
            score = min_value(apply_move(state, move), -math.inf, math.inf, depth - 1)
            # print("Move:", move, "Score:", score)
            if score > best_score:
                best_score = score
                best_moves = [move]
                # print("New best move at depth", depth, "is", move, "with score", score)
            elif score == best_score:
                best_moves.append(move)
        # print("Best moves at depth", depth, "are", best_moves)
        best_move = random.choice(best_moves)
        depth += 1
    return best_move
