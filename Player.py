import pygame
from Board import *

class Player:
    def __init__(self, red):
        self.connected = False
        self.red = red
        self.is_turn = True if self.red else False

        self.locked_piece = None
        self.locked_possible_moves = []

        self.moved_piece = None
        self.moved_kills = []
        self.moved_pos = None

        self.anim_move_ri = 0
        self.anim_move_ri_built = 0
        self.anim_move_r = [6, 7, 8, 9, 10, 11, 10, 9, 8, 7]

        self.rematch = False

    def get_pieces(self, board):
        return [piece for piece in board.pieces if piece.red is self.red]

    def get_clicked_piece(self, board, mouse_pos):
        x, y = mouse_pos
        r, c = y // board.cell_h, x // board.cell_w
        for piece in self.get_pieces(board):
            if piece.pos == (r, c) and not piece.cap:
                return piece
        return None

    def draw_possible_moves(self, win, board, r):
        xoff, yoff = board.rect[0]
        if self.locked_piece is None:
            return
        else:
            pos = self.locked_piece.pos
            for move in self.locked_possible_moves:
                for to_pos in move['to']:
                    w, h = r, r
                    tr, tc = to_pos
                    tx, ty = tc * board.cell_w + board.cell_w//2 - w//2, tr * board.cell_h + board.cell_h//2 - h//2
                    rect = pygame.rect.Rect(tx + xoff, ty + yoff, w, h)
                    pygame.draw.rect(win, (53, 150, 80), rect, 0)

    def is_legal_move(self, to_pos):
        for move in self.locked_possible_moves:
            if move['to'] and to_pos == move['to'][-1]:
                return True, move['kill']
        return False, None

    def handle_clicks(self, board, mouse_pos):
        if not self.is_turn:
            return
        piece = self.get_clicked_piece(board, mouse_pos)
        if piece is not None:
            self.lock_handler(board, piece)
        elif self.locked_piece is not None:
            self.move_handler(board, mouse_pos)

    def lock_handler(self, board, piece):
        self.locked_piece = piece
        self.locked_possible_moves = piece.possible_moves(board)

    def move_handler(self, board, mouse_pos):
        x, y = mouse_pos
        tr, tc = y // board.cell_h, x // board.cell_w
        legal, kills = self.is_legal_move((tr, tc))
        if legal:
            self.moved_kills = kills
            self.moved_piece = self.locked_piece
            self.moved_pos = (tr, tc)
            self.locked_piece = None
            self.locked_possible_moves = []

    def animate_lock(self, win, board, sp=0.15):
        r = int(self.anim_move_r[self.anim_move_ri])
        self.draw_possible_moves(win, board, r)
        self.anim_move_ri_built = (self.anim_move_ri_built + sp) % (1 + sp)
        self.anim_move_ri = (self.anim_move_ri + int(self.anim_move_ri_built)) % len(self.anim_move_r)

    def draw_lock(self, win, board):
        if self.locked_piece is not None:
            self.animate_lock(win, board)
