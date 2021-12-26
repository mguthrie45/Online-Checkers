import sys
import socket
import pickle
import _thread
from Player import *
from Board import *

SWIDTH, SHEIGHT = 720, 640
WIDTH, HEIGHT = 496, 496

def update_player_info(server, player, uplayer):
    player.locked_piece = uplayer.locked_piece
    player.locked_possible_moves = uplayer.locked_possible_moves
    player.anim_move_ri = uplayer.anim_move_ri
    player.anim_move_ri_built = uplayer.anim_move_ri_built
    if server.game_winner is not None:
        player.rematch = uplayer.rematch

class ServerInstance:
    NUM_PLAYERS = 2
    ADDR = "192.168.1.224"
    PORT = 5555
    def __init__(self):
        self.board = self.make_new_board()
        self.game_winner = None
        self.players = self.make_players()

        self.id_locked = [False, False]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((self.ADDR, self.PORT))
        except socket.error as e:
            print(e)

    def make_new_board(self):
        return Board(SWIDTH, SHEIGHT, WIDTH, HEIGHT)

    def make_players(self):
        return [Player(True), Player(False)]

    def recv_game_state(self, conn):
        data = conn.recv(4096)
        if not data:
            return None
        state = pickle.loads(data)
        return state

    def share_game_state(self, conn, state):
        encoded = pickle.dumps(state)
        conn.sendall(encoded)

    def client_thread(self, conn, id):
        start_info = {
            'self': self.players[id],
            'other': self.players[0] if id == 1 else self.players[1],
            'board': self.board if id == 0 else self.board.reverse()
        }
        self.share_game_state(conn, start_info)
        while True:
            try:
                player_self = self.recv_game_state(conn)
                if player_self:
                    update_player_info(self, self.players[id], player_self)
                    if isinstance(player_self.moved_piece, Piece) and player_self.is_turn:
                        if id == 0:
                            self.board.move_piece(player_self.moved_piece.pos, player_self.moved_pos)
                            for piece in player_self.moved_kills:
                                self.board.capture_piece(piece.pos)
                            self.players[0].is_turn = False
                            self.players[1].is_turn = True
                            self.players[0].moved_piece = None
                            self.players[0].moved_kills = []
                            self.players[0].moved_pos = None

                        elif id == 1:
                            self.board.move_piece(player_self.moved_piece.pos, player_self.moved_pos, comp=True)
                            for piece in player_self.moved_kills:
                                self.board.capture_piece(piece.pos, comp=True)
                            self.players[0].is_turn = True
                            self.players[1].is_turn = False
                            self.players[1].moved_piece = None
                            self.players[1].moved_kills = []
                            self.players[1].moved_pos = None

                    update_kings_by_position(self.board)

                    self.game_winner = check_for_win(self.board)

                    if self.game_winner is not None and self.players[0].rematch and self.players[1].rematch:
                        self.players = self.make_players()
                        self.players[0].connected = True
                        self.players[1].connected = True
                        self.board = self.make_new_board()
                        self.game_winner = None

                    game_state = {
                        'self': self.players[id],
                        'other': self.players[0] if id == 1 else self.players[1],
                        'board': self.board if id == 0 else self.board.reverse(),
                        'game_winner': self.game_winner
                    }
                    self.share_game_state(conn, game_state)

                else:
                    print(f"Connection with tid = {id} broken.")
                    self.players[id].connected = False
                    self.id_locked[id] = False
                    break
            except:
                break

    def listen(self):
        self.sock.listen(self.NUM_PLAYERS)
        id = None
        while True:
            conn, addr = self.sock.accept()
            if not self.id_locked[0]:
                self.id_locked[0] = True
                id = 0
            elif not self.id_locked[1]:
                self.id_locked[1] = True
                id = 1
            self.players[id].connected = True
            _thread.start_new_thread(self.client_thread, (conn, id))

if __name__ == "__main__":
    server = ServerInstance()
    server.listen()

