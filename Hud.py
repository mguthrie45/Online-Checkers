import pygame

class Hud:
    XOFF, YOFF = 0, 0
    def __init__(self, sw, sh, bw, bh, player):
        self.sw, self.sh, self.bw, self.bh = sw, sh, bw, bh
        self.red = player.red

    def draw_panel(self):
        pass

    def draw_captured_pieces(self, win, board):
        red_img = pygame.image.load('red.png')
        blue_img = pygame.image.load('blue.png')
        bxoff, byoff = board.rect[0]
        x1, x2, y_init = bxoff // 2 - 31, int(bxoff * (3/2)) + self.bw - 31, byoff
        y_inc = self.bh // 16
        for i in range(max(board.red_cap, board.blue_cap)):
            if i <= board.red_cap:
                win.blit(red_img, (x1, y_init))
            if i <= board.blue_cap:
                win.blit(blue_img, (x2, y_init))
            y_init += y_inc

    def draw_player_turn(self):
        pass

    def draw_players(self, win, board):
        font = pygame.font.SysFont(None, 32)
        btopleft = board.rect[0]
        bbotleft = board.rect[2]
        p2x, p2y = self.sw // 2, btopleft[1] // 2
        p1x, p1y = self.sw // 2, btopleft[1] + self.bh + btopleft[1] // 2
        p2txt = font.render('Player 2', True, (0, 0, 0))
        p1txt = font.render('Player 1', True, (0, 0, 0))
        p2w, p2h = p2txt.get_width(), p2txt.get_height()
        p1w, p1h = p1txt.get_width(), p1txt.get_height()

        p2x -= p2w // 2
        p2y -= p2h // 2
        p1x -= p1w // 2
        p1y -= p1h // 2

        win.blit(p2txt, (p2x, p2y))
        print(p1x, p1y)
        win.blit(p1txt, (p1x, p1y))

    def draw(self, win, board):
        self.draw_players(win, board)
        self.draw_captured_pieces(win, board)