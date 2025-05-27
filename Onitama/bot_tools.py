from Onitama.game_tools import BoardState, MAILBOX_SIZE, get_valid_targets_by_card


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
    for i in range(MAILBOX_SIZE):
        valid_moves += get_valid_moves_for_piece(board_state, i)
    return valid_moves
