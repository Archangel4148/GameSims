import random
import socket
from Onitama.game_tools import parse_sen, to_sen, get_all_valid_moves, LOGICAL_TO_MAILBOX

HOST = 'localhost'
PORT = 65432

def choose_move(board_state, role):
    """
    Choose and return a move as a tuple: (from_idx, to_idx, card)
    This will be converted and sent to the server as: "<logical_from> <logical_to> <card>"
    """
    valid_moves = get_all_valid_moves(board_state)
    move = random.choice(valid_moves)
    return move

def logical_index(mailbox_index):
    try:
        return LOGICAL_TO_MAILBOX.index(mailbox_index)
    except ValueError:
        return -1

def main():
    role = None
    board = None
    buffer = b""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("[CONNECTED] Waiting for GAME_START...")

        while True:
            data = sock.recv(1024)
            if not data:
                break
            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                msg = line.decode().strip()
                print("[RECEIVED]", msg)

                if msg.startswith("GAME_START"):
                    _, role = msg.split(maxsplit=1)
                    print(f"[GAME STARTED] Role: {role}")

                elif msg.startswith("GAME_UPDATE"):
                    _, sen = msg.split(maxsplit=1)
                    board = parse_sen(sen)
                    if board.is_p1_turn == (role == "P1"):
                        from_idx, to_idx, card = choose_move(board, role)
                        send_move(sock, from_idx, to_idx, card)

                elif msg.startswith("INVALID_MOVE"):
                    print("[WARNING] Invalid move:", msg)

                elif msg.startswith("GAME_OVER"):
                    print("[GAME OVER]", msg)
                    return

def send_move(sock, from_idx, to_idx, card):
    logical_from = logical_index(from_idx)
    logical_to = logical_index(to_idx)
    assert logical_from != -1 and logical_to != -1, "Invalid mailbox indices"
    msg = f"{logical_from} {logical_to} {card}\n"
    print(f"[SENDING MOVE] {msg.strip()}")
    try:
        sock.sendall(msg.encode())
    except Exception as e:
        print(f"[SEND ERROR] {e}")

if __name__ == "__main__":
    main()
