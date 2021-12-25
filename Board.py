import pygame

class Piece:
    def __init__(self, red, is_king, pos, cap=False):
        self.red = red
        self.is_king = is_king
        self.cap = cap
        self.pos = pos
        self.im_path = self.get_img_path()

    def get_img_path(self):
        if self.red:
            if self.is_king:
                return 'regking.png'
            else:
                return 'red.png'
        else:
            if self.is_king:
                return 'blueking.png'
            else:
                return 'blue.png'

    def get_diag_positions(self, board):
        r, c = self.pos
        pos = []
        if r > 0:
            if c > 0:
                pos.append((r - 1, c - 1))
            if c < 7:
                pos.append((r - 1, c + 1))
        if self.is_king and r < 7:
            if c > 0:
                pos.append((r + 1, c - 1))
            if c < 7:
                pos.append((r + 1, c + 1))
        return pos

    def get_elim_path(self, board, from_pos, to_pos):
        piece = board.board[to_pos]
        if isinstance(piece, Piece) and piece.red is not self.red:
            skip_pos = (to_pos[0] - 1, to_pos[1] + (to_pos[1] - from_pos[1]))
            if skip_pos not in board.board:
                return [], []
            if board.board[skip_pos] is None or board.board[skip_pos].cap:
                piece_copy = Piece(self.red, self.is_king, skip_pos)
                diag_moves = piece_copy.get_diag_positions(board)
                possible_paths = []
                possible_kills = []
                for tpos in diag_moves:
                    path, kills = piece_copy.get_elim_path(board, skip_pos, tpos)
                    possible_paths.append(path)
                    possible_kills.append(kills)
                trace = [skip_pos] + max(possible_paths, key=lambda x: len(x))
                kills = [piece] + max(possible_kills, key=lambda x: len(x))
                return trace, kills
            else:
                return [], []
        else:
            return [], []

    def possible_moves(self, board):
        b = board.board
        moves = []
        r, c = self.pos
        for to_pos in self.get_diag_positions(board):
            if b[to_pos] is None or b[to_pos].cap:
                moves.append({'to': [to_pos], 'kill': []})
            elif isinstance(b[to_pos], Piece) and b[(r, c)].red is not b[to_pos].red:
                path, kills = self.get_elim_path(board, self.pos, to_pos)
                move = {'to': path, 'kill': kills}
                moves.append(move)
        return moves

    def draw(self, win, cell_w, cell_h, xoff, yoff):
        if not self.cap:
            img = pygame.image.load(self.im_path)
            r, c = self.pos
            x, y = c * cell_w + 1, r * cell_h + 1
            w, h = cell_w - 2, cell_h - 2
            win.blit(img, (x + xoff, y + yoff))


class Board:
    IMG_PATH = "board.png"
    NUM_PLAYER_PIECES = 1
    def __init__(self, sw, sh, w, h, board=None, pieces=None, red_cap=0, blue_cap=0):
        self.sw, self.sh = sw, sh
        self.w, self.h = w, h
        self.cell_w, self.cell_h = w // 8, h // 8
        self.pieces = set() if pieces is None else pieces
        self.board = self.init_board() if board is None else board
        self.red_cap, self.blue_cap = red_cap, blue_cap
        self.rect = self.get_board_rect()

    def set_num_captured(self):
        rct, bct = 0, 0
        for piece in self.pieces:
            if piece.red and piece.cap:
                rct += 1
            if not piece.red and piece.cap:
                bct += 1

    def get_board_rect(self):
        topleft = ((self.sw - self.w) // 2, (self.sh - self.h) // 2)
        topright = (topleft[0] + self.w, (self.sh - self.h) // 2)
        botleft = (topleft[0], topright[0] + self.h)
        botright = (topright[0], botleft[1])
        return (topleft, topright, botleft, botright)

    def init_board(self):
        if self.pieces:
            raise("Board ERROR: Given pieces but no board configuration")
        board = {}
        for r in range(8):
            for c in range(8):
                '''if r == 0 and c % 2 == 0 or r == 1 and c % 2 == 1:
                    piece = Piece(False, False, (r, c))
                    board[(r, c)] = piece
                    self.pieces.add(piece)
                if r == 6 and c % 2 == 1 or r == 7 and c % 2 == 0:
                    piece = Piece(True, False, (r, c))
                    board[(r, c)] = piece
                    self.pieces.add(piece)
                else:'''
                board[(r, c)] = None
        board[(5,3)] = Piece(True, False, (5, 3))
        self.pieces.add(board[(5,3)])
        board[(4, 2)] = Piece(False, False, (4, 2))
        self.pieces.add(board[(4,2)])
        return board

    def get_comp_pos(self, pos):
        return (7 - pos[0], 7 - pos[1])

    def reverse(self):
        board = {}
        pieces = set()
        for r, c in self.board:
            comp_pos = (7-r, 7-c)
            piece = self.board[(r, c)]
            if isinstance(piece, Piece):
                comp_piece = Piece(piece.red, piece.is_king, comp_pos, piece.cap)
                board[comp_pos] = comp_piece
                pieces.add(comp_piece)
            else:
                board[comp_pos] = None
        return Board(self.sw, self.sh, self.w, self.h, board, pieces, self.red_cap, self.blue_cap)


    def move_piece(self, from_pos, to_pos, comp=False):
        if comp:
            actual_from = self.get_comp_pos(from_pos)
            actual_to = self.get_comp_pos(to_pos)
            piece = self.board[actual_from]
            self.board[actual_from] = None
            piece.pos = actual_to
            self.board[actual_to] = piece
        else:
            piece = self.board[from_pos]
            self.board[from_pos] = None
            piece.pos = to_pos
            self.board[to_pos] = piece

    def draw_panel(self, win):
        frame_img = pygame.image.load('frame.png')
        fw = 12
        bxoff, byoff = self.rect[0]
        win.blit(frame_img, (bxoff - fw, byoff - fw))

    def draw(self, win):
        self.draw_panel(win)

        img = pygame.image.load(self.IMG_PATH)
        topleft = self.rect[0]
        xoff, yoff = topleft
        win.blit(img, (xoff, yoff))

        for piece in self.pieces:
            piece.draw(win, self.cell_w, self.cell_h, xoff, yoff)

    def capture_piece(self, pos, comp=False):
        if comp:
            actual_pos = self.get_comp_pos(pos)
            piece = self.board[actual_pos]
            if piece.red:
                self.red_cap += 1
            else:
                self.blue_cap += 1
            self.board[actual_pos] = None
            piece.cap = True
        else:
            piece = self.board[pos]
            if piece.red:
                self.red_cap += 1
            else:
                self.blue_cap += 1
            self.board[pos] = None
            piece.cap = True

    def is_terminal(self):
        print(self.red_cap, self.blue_cap)
        return self.red_cap >= self.NUM_PLAYER_PIECES or self.blue_cap >= self.NUM_PLAYER_PIECES

    def get_winner(self):
        return 'red' if self.blue_cap >= self.NUM_PLAYER_PIECES else 'blue'

def update_kings_by_position(board):
    for pos in board.board:
        piece = board.board[pos]
        if isinstance(piece, Piece):
            if piece.red and piece.pos[0] == 0 and board.red_cap > 0:
                piece.is_king = True
                board.red_cap -= 1
            elif not piece.red and piece.pos[0] == 7 and board.blue_cap > 0:
                piece.is_king = True
                board.blue_cap -= 1

def check_for_win(board):
    if board.is_terminal():
        print('terminal')
        return board.get_winner()
