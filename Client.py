#TODO: Hud system: score/num captures, draw captures on sides, show who's turn it is, countdown timer for turn?
#TODO: Make a better terminal state. Detect wins before all pieces captured if opponent cant move.
#TODO: Add graphics
#TODO: Add some serverside locking functionality. Maybe if player joins, automatically refresh. Make sure player cant play before both loaded in. Make sure players cant play after game ends
#TODO: Game restart/rematch system? If both players agree and are still connected, restart the game.



import pygame
from Board import *
from Player import *
from Server import ServerInstance
from Network import *
from Hud import *

ADDR, PORT = ServerInstance.ADDR, ServerInstance.PORT

def send_self_to_server(network, player):
    try:
        reply = network.send_player_state(player)
        return reply
    except socket.error as e:
        print(e)

def get_board_mouse_pos(board_rect, mouse_pos):
    xoff, yoff = board_rect[0]
    mx, my = mouse_pos
    actx, acty = mx - xoff, my - yoff
    return actx, acty

def main():
    WIDTH, HEIGHT = 720, 640
    BOARDWIDTH, BOARDHEIGHT = 496, 496
    BACKGROUND_COLOR = (53, 145, 77)
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    net = ServerConnection()
    start_info = net.get_start_info()
    player_self, board = start_info['self'], start_info['board']
    hud = Hud(WIDTH, HEIGHT, BOARDWIDTH, BOARDHEIGHT, player_self)
    board_rect = board.get_board_rect()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                act_pos = get_board_mouse_pos(board_rect, mouse_pos)
                player_self.handle_clicks(board, act_pos)

        game_state = send_self_to_server(net, player_self)
        player_self, board = game_state['self'], game_state['board']

        win.fill(BACKGROUND_COLOR)
        board.draw(win)
        player_self.draw_lock(win, board)
        hud.draw(win, board)

        pygame.display.update()
        clock.tick(40)

if __name__ == "__main__":
    main()