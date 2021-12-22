import pygame
from Board import *
from Player import *
from Server import ServerInstance
from Network import *

ADDR, PORT = ServerInstance.ADDR, ServerInstance.PORT

def send_self_to_server(network, player):
    try:
        reply = network.send_player_state(player)
        return reply
    except socket.error as e:
        print(e)

def main():
    WIDTH, HEIGHT = 500, 500
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    net = ServerConnection()
    start_info = net.get_start_info()
    player_self, board = start_info['self'], start_info['board']

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                player_self.handle_clicks(board, mouse_pos)

        send_state = player_self
        game_state = send_self_to_server(net, player_self)
        player_self, board = game_state['self'], game_state['board']

        win.fill((255,255,255))
        board.draw(win)
        player_self.draw_lock(win, board)

        pygame.display.update()
        clock.tick(40)

if __name__ == "__main__":
    main()