import dataclasses

# Map all possible cards to their move offsets
CARD_MOVES = {
    "MO": ((-1, -1), (1, 1), (1, -1), (-1, 1)),
    "RO": ((-1, 0), (-1, -1), (1, 0), (1, 1)),
    "HO": ((-1, 0), (0, 1), (0, -1)),
    "OX": ((0, 1), (1, 0), (0, -1)),
    "BO": ((-1, 0), (0, 1), (1, 0)),
    "TI": ((0, -1), (0, 2)),
    "FR": ((-2, 0), (-1, 1), (1, -1)),
    "RA": ((-1, -1), (1, 1), (2, 0)),
    "DR": ((-2, 1), (-1, -1), (1, -1), (2, 1)),
    "CR": ((-1, -1), (1, -1), (0, 1)),
    "MA": ((-1, 1), (1, 1), (0, -1)),
    "CB": ((-2, 0), (0, 1), (2, 0)),
    "GO": ((-1, 0), (-1, 1), (1, 0), (1, -1)),
    "CO": ((-1, 0), (1, 1), (1, -1)),
    "EL": ((-1, 0), (-1, 1), (1, 0), (1, 1)),
    "EE": ((-1, 1), (-1, -1), (1, 0)),
}

# Create a mapping from nice indices to mailbox indices
MAILBOX_WIDTH = 9  # Using a wide mailbox to catch long jumps (tiger, crab, etc.)
MAILBOX_SIZE = MAILBOX_WIDTH * MAILBOX_WIDTH
LOGICAL_TO_MAILBOX = [(r + 2) * MAILBOX_WIDTH + (c + 2) for r in range(5) for c in range(5)]


@dataclasses.dataclass
class BoardState:
    mailbox_board: list[str | None]
    is_p1_turn: bool
    p1_cards: list[str]
    p2_cards: list[str]
    center_card: str

    def __str__(self) -> str:
        output = []

        # Display the 5x5 board extracted from the mailbox
        for row in reversed(range(5)):
            line = []
            for col in range(5):
                mailbox_index = LOGICAL_TO_MAILBOX[row * 5 + col]
                piece = self.mailbox_board[mailbox_index]
                line.append(piece if piece else '.')
            output.append(" ".join(line))

        # Cards
        output.append(f"\nP1 Cards: {self.p1_cards[0]} {self.p1_cards[1]}")
        output.append(f"P2 Cards: {self.p2_cards[0]} {self.p2_cards[1]}")
        output.append(f"Center: {self.center_card}")
        output.append(f"Is P1's Turn?: {self.is_p1_turn}")

        return "\n".join(output)


def parse_sen(sen: str) -> BoardState:
    # Parse the SEN string
    sections = sen.split("/")
    board = sections[:-1]
    card_section = sections[-1][:-1]
    cards = [card_section[i] + card_section[i + 1] for i in range(0, len(card_section), 2)]
    is_p1_move = sections[-1][-1] == "0"

    # Parse the board
    board_list = []
    for row in board:
        row_string = ""
        for space in row:
            if space.isdigit():
                row_string += "." * int(space)
            else:
                row_string += space
        board_list += row_string

    # Build the board mailbox
    mailbox = [None] * MAILBOX_SIZE
    for i, space in enumerate(board_list):
        mailbox[LOGICAL_TO_MAILBOX[i]] = space

    # Build the board state
    return BoardState(mailbox, is_p1_move, cards[0:2], cards[2:4], cards[4])


def apply_move(board_state: BoardState, move: tuple[int, int, str]) -> BoardState:
    from_idx, to_idx, card = move
    moving_piece = board_state.mailbox_board[from_idx]
    target_space = board_state.mailbox_board[to_idx]

    # Validate move
    assert moving_piece and moving_piece != ".", f"Cannot make move; No piece at index {from_idx}"
    assert board_state.is_p1_turn == moving_piece.islower(), "Cannot make move; Out of turn"
    assert target_space == "." or target_space.islower() != board_state.is_p1_turn, "Cannot make move; Invalid target"
    playing_hand = board_state.p1_cards if board_state.is_p1_turn else board_state.p2_cards
    assert card in playing_hand, f"Cannot make move; No such card, \'{card}\' in hand"

    print(f"{from_idx}, {to_idx} is a valid move!")

    # Update card positions
    turn_player_cards = board_state.p1_cards if board_state.is_p1_turn else board_state.p2_cards

    new_cards = turn_player_cards.copy()
    new_cards.append(board_state.center_card)
    new_cards.remove(card)
    new_center_card = card

    # Apply move and create new board
    new_board = board_state.mailbox_board.copy()
    new_board[from_idx] = "."
    new_board[to_idx] = moving_piece

    if board_state.is_p1_turn:
        return BoardState(new_board, False, new_cards, board_state.p2_cards.copy(), new_center_card)
    else:
        return BoardState(new_board, True, board_state.p1_cards.copy(), new_cards, new_center_card)


def get_valid_targets_by_card(board_state: BoardState, start_idx: int, card: str) -> list[int]:
    is_p1 = board_state.is_p1_turn
    offsets = CARD_MOVES[card]
    mailbox = board_state.mailbox_board
    destinations = []

    for dx, dy in offsets:
        # Flip for P2 (rotated board)
        if not is_p1:
            dx, dy = -dx, -dy

        to_idx = start_idx + dx + dy * MAILBOX_WIDTH

        # Check if resulting index is on the board
        if 0 < to_idx < MAILBOX_SIZE:
            target = mailbox[to_idx]
            if target is None or target.islower() == is_p1:
                # Move is outside board, or targets an ally
                continue
            else:
                # Valid move
                destinations.append(to_idx)
    return destinations


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

if __name__ == '__main__':
    # starting_sen = "SSMSS/5/5/5/ssmss/TIMOCRBORO0"
    starting_sen = "5/5/2s2/5/5/TIMOCRBORO0"

    # Create the starting board
    board = parse_sen(starting_sen)

    print(board)

    # Demonstrate all valid moves
    for move in get_all_valid_moves(board):
        print("===", move[2], "===")
        print(apply_move(board, move))
