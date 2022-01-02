import socket
import json
import pickle

class ServerConnection:
    ADDR = "192.168.1.189"
    PORT = 5555
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.info = self.connect()

    def get_start_info(self):
        return self.info

    def connect(self):
        try:
            self.socket.connect((self.ADDR, self.PORT))
            return self.recv_game_state()
        except:
            print('Connection Error...')

    def recv_game_state(self):
        data = self.socket.recv(4096)
        return pickle.loads(data)

    def send_player_state(self, state):
        encoded = pickle.dumps(state)
        try:
            self.socket.send(encoded)
            return self.recv_game_state()
        except socket.error as e:
            print(e)