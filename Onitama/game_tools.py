import dataclasses
import random

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

STARTING_BOARD = "SSMSS...............ssmss"

# Create a mapping from nice indices to mailbox indices
MAILBOX_WIDTH = 9  # Using a wide mailbox to catch long jumps (tiger, crab, etc.)
MAILBOX_SIZE = MAILBOX_WIDTH * MAILBOX_WIDTH
LOGICAL_TO_MAILBOX = [(r + 2) * MAILBOX_WIDTH + (c + 2) for r in range(5) for c in range(5)]


@dataclasses.dataclass
class BoardState:
    mailbox_board: list[str | None] = None
    is_p1_turn: bool = None
    p1_cards: list[str] = None
    p2_cards: list[str] = None
    center_card: str = None

    def __post_init__(self):
        # Generate a standard starting board
        if self.mailbox_board is None:
            self.mailbox_board = [None] * MAILBOX_SIZE
            flat_board = list(STARTING_BOARD)
            for i, char in enumerate(flat_board):
                self.mailbox_board[LOGICAL_TO_MAILBOX[i]] = char

        # Deal cards randomly
        if self.p1_cards is None or self.p2_cards is None or self.center_card is None:
            game_deck = random.sample(list(CARD_MOVES.keys()), 5)
            self.p1_cards = game_deck[:2]
            self.p2_cards = game_deck[2:4]
            self.center_card = game_deck[4]

            # Select a random starting player
            self.is_p1_turn = random.choice((True, False))

    def __str__(self) -> str:
        output = []

        # Display the 5x5 board extracted from the mailbox
        for row in range(5):
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


def to_sen(board_state: BoardState) -> str:
    # Extract 5x5 board portion from mailbox
    board_rows = []

    for row in range(5):
        row_data = ""
        for col in range(5):
            mailbox_index = LOGICAL_TO_MAILBOX[row * 5 + col]
            val = board_state.mailbox_board[mailbox_index]
            row_data += val if val and val != "." else "1"

        # Compress empty spaces ("111" → "3")
        compressed = ""
        count = 0
        for char in row_data:
            if char == "1":
                count += 1
            else:
                if count > 0:
                    compressed += str(count)
                    count = 0
                compressed += char
        if count > 0:
            compressed += str(count)
        board_rows.append(compressed)

    # Combine all card data
    card_string = "".join(board_state.p1_cards + board_state.p2_cards + [board_state.center_card])
    turn = "0" if board_state.is_p1_turn else "1"

    return "/".join(board_rows) + "/" + card_string + turn


def apply_move(board_state: BoardState, move: tuple[int, int, str]) -> BoardState:
    from_idx, to_idx, card = move
    moving_piece = board_state.mailbox_board[from_idx]
    target_space = board_state.mailbox_board[to_idx]
    dx = (to_idx % MAILBOX_WIDTH) - (from_idx % MAILBOX_WIDTH)
    dy = -((to_idx // MAILBOX_WIDTH) - (from_idx // MAILBOX_WIDTH))

    # Validate move
    assert moving_piece and moving_piece != ".", f"Cannot make move; No piece at index {from_idx}"
    assert board_state.is_p1_turn == moving_piece.islower(), "Cannot make move; Out of turn"
    assert target_space == "." or target_space.islower() != board_state.is_p1_turn, "Cannot make move; Invalid target"
    assert card in CARD_MOVES, f"Card '{card}' is not a recognized card."
    playing_hand = board_state.p1_cards if board_state.is_p1_turn else board_state.p2_cards
    assert card in playing_hand, f"Cannot make move; No such card, \'{card}\' in hand"

    # Flip card direction for Player 2
    if not board_state.is_p1_turn:
        dx, dy = -dx, -dy

    assert (dx, dy) in CARD_MOVES[card], f"Cannot make move; ({dx},{dy}) not valid for card '{card}'"

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


def is_victory(board_state: BoardState) -> tuple[bool, str]:
    # Capture wins
    if "m" not in board_state.mailbox_board:
        return True, "Player 2 wins by capture!"
    if "M" not in board_state.mailbox_board:
        return True, "Player 1 wins by capture!"
    # Temple wins
    p1_temple = LOGICAL_TO_MAILBOX[22]
    p2_temple = LOGICAL_TO_MAILBOX[2]
    if board_state.mailbox_board[p1_temple] == "M":
        return True, "Player 2 wins by occupation!"
    if board_state.mailbox_board[p2_temple] == "m":
        return True, "Player 1 wins by occupation!"
    # No win
    return False, ""


def get_valid_targets_by_card(board_state: BoardState, start_idx: int, card: str) -> list[int]:
    is_p1 = board_state.is_p1_turn
    offsets = CARD_MOVES[card]
    mailbox = board_state.mailbox_board
    destinations = []

    for dx, dy in offsets:
        # Flip for P2 (rotated board)
        if not is_p1:
            dx, dy = -dx, -dy

        to_idx = start_idx + dx + (-dy) * MAILBOX_WIDTH

        # Check if resulting index is on the board
        if 0 < to_idx < MAILBOX_SIZE:
            target = mailbox[to_idx]
            if target is None or (target != "." and target.islower() == is_p1):
                # Move is outside board, or targets an ally
                continue
            else:
                # Valid move
                destinations.append(to_idx)
    return destinations


if __name__ == '__main__':
    board = BoardState()
    print(board)
