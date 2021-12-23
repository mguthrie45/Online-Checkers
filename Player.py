import pygame
from Board import *

class Player:
    def __init__(self, red):
        self.connected = False
        self.red = red
        #self.is_turn = True if self.red else False
        self.is_turn = True

        self.locked_piece = None
        self.locked_possible_moves = []

        self.moved_piece = None
        self.moved_kills = []
        self.moved_pos = None

    def get_pieces(self, board):
        return [piece for piece in board.pieces if piece.red is self.red]

    def get_clicked_piece(self, board, mouse_pos):
        print(self.is_turn)
        x, y = mouse_pos
        r, c = y // board.cell_h, x // board.cell_w
        print(r, c)
        for piece in self.get_pieces(board):
            if piece.pos == (r, c):
                return piece
        return None

    def draw_possible_moves(self, win, board):
        xoff, yoff = board.rect[0]
        if self.locked_piece is None:
            return
        else:
            pos = self.locked_piece.pos
            for move in self.locked_possible_moves:
                for to_pos in move['to']:
                    w, h = 8, 8
                    tr, tc = to_pos
                    tx, ty = tc * board.cell_w + board.cell_w//2 - w//2, tr * board.cell_h + board.cell_h//2 - h//2
                    rect = pygame.rect.Rect(tx + xoff, ty + yoff, w, h)
                    pygame.draw.rect(win, (0, 255, 0), rect, 0)

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
        print('here')

    def move_handler(self, board, mouse_pos):
        x, y = mouse_pos
        tr, tc = y // board.cell_h, x // board.cell_w
        legal, kills = self.is_legal_move((tr, tc))
        print(kills)
        if legal:
            self.moved_kills = kills
            self.moved_piece = self.locked_piece
            self.moved_pos = (tr, tc)
            self.locked_piece = None
            self.locked_possible_moves = []

    def draw_lock(self, win, board):
        if self.locked_piece is not None:
            self.draw_possible_moves(win, board)
