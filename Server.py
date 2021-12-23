import sys
import socket
import pickle
import _thread
from Player import *
from Board import *

SWIDTH, SHEIGHT = 720, 640
WIDTH, HEIGHT = 496, 496

def update_player_locks(player, uplayer):
    player.locked_piece = uplayer.locked_piece
    player.locked_possible_moves = uplayer.locked_possible_moves

class ServerInstance:
    NUM_PLAYERS = 2
    ADDR = "192.168.56.1"
    PORT = 5555
    def __init__(self):
        self.board = Board(SWIDTH, SHEIGHT, WIDTH, HEIGHT)
        self.players = [Player(True), Player(False)]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((self.ADDR, self.PORT))
        except socket.error as e:
            print(e)

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
        print(f'thread {id} connected.')
        start_info = {
            'self': self.players[id],
            'board': self.board if id == 0 else self.board.reverse()
        }
        self.share_game_state(conn, start_info)
        while True:
            try:
                player_self = self.recv_game_state(conn)
                if player_self:
                    update_player_locks(self.players[id], player_self)
                    if isinstance(player_self.moved_piece, Piece) and player_self.is_turn:
                        print(f"Player {id} moving")
                        if id == 0:
                            self.board.move_piece(player_self.moved_piece.pos, player_self.moved_pos)
                            for piece in player_self.moved_kills:
                                print(piece)
                                self.board.capture_piece(piece.pos)
                            #self.players[0].is_turn = False
                            #self.players[1].is_turn = True
                            self.players[0].moved_piece = None
                            self.players[0].moved_kills = []
                            self.players[0].moved_pos = None

                        elif id == 1:
                            self.board.move_piece(player_self.moved_piece.pos, player_self.moved_pos, comp=True)
                            print('here')
                            for piece in player_self.moved_kills: #TODO: FIX CAPTURE PIECES FOR BLUE (COMP) NOT WORKING AND CRASHING GAME
                                print(piece)
                                self.board.capture_piece(piece.pos, comp=True)
                            #self.players[0].is_turn = True
                            #self.players[1].is_turn = False
                            self.players[1].moved_piece = None
                            self.players[1].moved_kills = []
                            self.players[1].moved_pos = None

                    update_kings_by_position(self.board)

                    game_state = {
                        'self': self.players[id],
                        'board': self.board if id == 0 else self.board.reverse()
                    }
                    self.share_game_state(conn, game_state)

                else:
                    print(f"Connection with tid = {id} broken.")
                    break
            except:
                break

    def listen(self):
        self.sock.listen(self.NUM_PLAYERS)
        id = 0
        while True:
            conn, addr = self.sock.accept()
            self.players[id].connected = True
            _thread.start_new_thread(self.client_thread, (conn, id))
            id += 1

if __name__ == "__main__":
    server = ServerInstance()
    server.listen()

