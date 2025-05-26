import dataclasses

# Create a mapping from nice indices to mailbox indices
MAILBOX_WIDTH = 9
MAILBOX_SIZE = MAILBOX_WIDTH * MAILBOX_WIDTH
LOGICAL_TO_MAILBOX = [(r + 2) * MAILBOX_WIDTH + (c + 2) for r in range(5) for c in range(5)]


@dataclasses.dataclass
class BoardState:
    mailbox_board: list[str | None]
    turn: int
    p1_cards: list[str]
    p2_cards: list[str]
    center_card: str

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
        output.append(f"Turn: Player {self.turn}")

        return "\n".join(output)


def parse_sen(sen: str) -> BoardState:
    # Parse the SEN string
    sections = sen.split("/")
    board = sections[:-1]
    card_section = sections[-1][:-1]
    cards = [card_section[i] + card_section[i + 1] for i in range(0, len(card_section), 2)]
    turn = sections[-1][-1]

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
    return BoardState(mailbox, int(turn), cards[0:2], cards[2:4], cards[4])


if __name__ == '__main__':
    starting_sen = "SMSMS/5/5/5/smsms/TIDRCRBORO1"
    # test_sen = starting_sen
    test_sen = "SMSMS/5/2s2/5/smsms/TIDRCRBORO1"

    board = parse_sen(test_sen)

    print(board)