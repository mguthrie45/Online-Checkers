#TODO: Hud system: countdown timer for turn?
#TODO: Make a better terminal state. Detect wins before all pieces captured if opponent cant move.
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
    BACKGROUND_COLOR = (53, 150, 80)
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    net = ServerConnection()
    start_info = net.get_start_info()
    player_self, player_other, board = start_info['self'], start_info['other'], start_info['board']
    hud = Hud(WIDTH, HEIGHT, BOARDWIDTH, BOARDHEIGHT, player_self)
    board_rect = board.get_board_rect()

    while True:
        game_state = send_self_to_server(net, player_self)
        player_self, player_other, board, game_winner = game_state['self'], game_state['other'], game_state['board'], game_state['game_winner']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                act_pos = get_board_mouse_pos(board_rect, mouse_pos)
                player_self.handle_clicks(board, act_pos)
            if game_winner is not None and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_self.rematch = True

        if player_self.connected and player_other.connected and game_winner is None:
            print(player_self.rematch)
            win.fill(BACKGROUND_COLOR)
            hud.draw(win, board)
            board.draw(win)
            player_self.draw_lock(win, board)
        elif game_winner is not None:
            win.fill(BACKGROUND_COLOR)
            board.draw(win)
            win_font = pygame.font.SysFont(None, 36)
            text = win_font.render(f'{game_winner} wins', True, (255, 0, 0))
            text_rematch = win_font.render('press [Enter] to rematch', True, (255, 0, 0))
            text_wait = win_font.render('waiting for other player', True, (255, 0, 0))
            fw, fh = text.get_width(), text.get_height()

            rw, rh = 400, fh * 2 + 30
            rx, ry = WIDTH//2 - rw//2, HEIGHT//2 - rh//2
            pygame.draw.rect(win, BACKGROUND_COLOR, pygame.rect.Rect(rx, ry, rw, rh), 0)
            pygame.draw.rect(win, (0, 0, 0), pygame.rect.Rect(rx - 1, ry - 1, rw + 2, rh + 2), 1)

            tx, ty = WIDTH // 2 - fw // 2, HEIGHT // 2 - fh // 2 - 15

            win.blit(text, (tx, ty))
            if not player_self.rematch:
                win.blit(text_rematch, (WIDTH//2 - text_rematch.get_width()//2, ty + fh + 2))
            else:
                win.blit(text_wait, (WIDTH//2 - text_wait.get_width()//2, ty + fh + 2))
        else:
            win.fill(BACKGROUND_COLOR)
            board.draw(win)
            wait_font = pygame.font.SysFont(None, 36)

            text = wait_font.render('waiting for player...', True, (255, 0, 0))
            fw, fh = text.get_width(), text.get_height()

            rw, rh = 350, fh + 30
            rx, ry = WIDTH//2 - rw//2, HEIGHT//2 - rh//2
            pygame.draw.rect(win, BACKGROUND_COLOR, pygame.rect.Rect(rx, ry, rw, rh), 0)
            pygame.draw.rect(win, (0, 0, 0), pygame.rect.Rect(rx - 1, ry - 1, rw + 2, rh + 2), 1)
            win.blit(text, (WIDTH//2 - fw//2, HEIGHT//2 - fh//2))

        pygame.display.update()
        clock.tick(40)

if __name__ == "__main__":
    main()