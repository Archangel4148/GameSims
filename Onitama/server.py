import socket
import threading
from Onitama.game_tools import BoardState, to_sen, parse_sen, apply_move, is_victory, LOGICAL_TO_MAILBOX

HOST = 'localhost'
PORT = 65432

clients = {}       # 'P1' -> socket, 'P2' -> socket
roles = {}         # socket -> 'P1' or 'P2'
current_board = None
lock = threading.Lock()

def handle_client(conn, role):
    global current_board

    # Wait until both players are connected
    while True:
        with lock:
            if len(clients) == 2:
                break

    buffer = b""
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                msg = line.decode().strip()
                process_bot_move(conn, role, msg)
        except Exception as e:
            print(f"[ERROR] {role} - {e}")
            break

    print(f"[DISCONNECT] {role}")
    with lock:
        del clients[role]
        del roles[conn]
    conn.close()

def process_bot_move(conn, role, msg):
    global current_board
    try:
        current_turn = "P1" if current_board.is_p1_turn else "P2"
        if role != current_turn:
            conn.sendall(b"INVALID_MOVE Not your turn.\n")
            return

        parts = msg.strip().split()
        assert len(parts) == 3, f"Bad move format: '{msg}'"

        logical_from = int(parts[0])
        logical_to = int(parts[1])
        card = parts[2]

        from_idx = LOGICAL_TO_MAILBOX[logical_from]
        to_idx = LOGICAL_TO_MAILBOX[logical_to]

        with lock:
            current_board = apply_move(current_board, (from_idx, to_idx, card))
            sen = to_sen(current_board)

            print(current_board)

            # Check win condition
            won, reason = is_victory(current_board)
            if won:
                for sock in clients.values():
                    try:
                        sock.sendall(f"GAME_OVER {reason}\n".encode())
                    except:
                        pass  # One of them might have already disconnected
                print(f"[GAME OVER] {reason}")
                return

            # Notify the next player to move
            next_turn = "P1" if current_board.is_p1_turn else "P2"
            next_sock = clients[next_turn]
            next_sock.sendall(f"GAME_UPDATE {sen}\n".encode())

    except Exception as e:
        conn.sendall(f"INVALID_MOVE {str(e)}\n".encode())
        print(f"[INVALID] {role} sent: {msg} — {e}")

def start_server():
    global current_board
    current_board = BoardState()

    print(f"[SERVER] Starting on {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)

        while len(clients) < 2:
            conn, addr = s.accept()
            with lock:
                if 'P1' not in clients:
                    role = 'P1'
                elif 'P2' not in clients:
                    role = 'P2'
                else:
                    print(f"[REJECTED] Extra connection from {addr}")
                    conn.close()
                    continue

                clients[role] = conn
                roles[conn] = role
                print(f"[CONNECTED] {role} from {addr}")
                threading.Thread(target=handle_client, args=(conn, role)).start()

        # Once both are connected, broadcast start
        sen = to_sen(current_board)
        for role, conn in clients.items():
            conn.sendall(f"GAME_START {role}\n".encode())

        print(current_board)

        # Send GAME_UPDATE to the bot whose turn it is
        turn_player = "P1" if current_board.is_p1_turn else "P2"
        clients[turn_player].sendall(f"GAME_UPDATE {sen}\n".encode())

if __name__ == "__main__":
    start_server()
