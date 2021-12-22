import pygame

class Piece:
    def __init__(self, red, is_king, pos, cap=False):
        self.red = red
        self.is_king = is_king
        self.cap = cap
        self.pos = pos

    def get_diag_positions(self, board):
        r, c = self.pos
        pos = []
        if r > 0:
            if c > 0:
                pos.append((r - 1, c - 1))
            if c < 7:
                pos.append((r - 1, c + 1))
        return pos

    def get_elim_path(self, board, from_pos, to_pos):
        piece = board.board[to_pos]
        if isinstance(piece, Piece) and piece.red is not self.red:
            skip_pos = (to_pos[0] - 1, to_pos[1] + (to_pos[1] - from_pos[1]))
            print(skip_pos)
            if skip_pos not in board.board:
                return [], []
            if board.board[skip_pos] is None:
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
            if b[to_pos] is None:
                moves.append({'to': [to_pos], 'kill': []})
            elif isinstance(b[to_pos], Piece) and b[(r, c)].red is not b[to_pos].red:
                path, kills = self.get_elim_path(board, self.pos, to_pos)
                move = {'to': path, 'kill': kills}
                moves.append(move)
        return moves

    def draw(self, win, cell_w, cell_h):
        if not self.cap:
            color = (255, 0, 0) if self.red else (0, 0, 255)
            r, c = self.pos
            x, y = c * cell_w + 1, r * cell_h + 1
            w, h = cell_w - 2, cell_h - 2
            pygame.draw.rect(win, color, pygame.rect.Rect(x, y, w, h), 0)


class Board:
    def __init__(self, w, h, board=None, pieces=None):
        self.w, self.h = w, h
        self.cell_w, self.cell_h = w // 8, h // 8
        self.pieces = set() if pieces is None else pieces
        self.board = self.init_board() if board is None else board

    def init_board(self):
        if self.pieces:
            raise("Board ERROR: Given pieces but no board configuration")
        board = {}
        for r in range(8):
            for c in range(8):
                if r <= 1:
                    piece = Piece(False, False, (r, c))
                    board[(r, c)] = piece
                    self.pieces.add(piece)
                elif r >= 6:
                    piece = Piece(True, False, (r, c))
                    board[(r, c)] = piece
                    self.pieces.add(piece)
                else:
                    board[(r, c)] = None
        board[(5,3)] = Piece(False, False, (5, 3))
        self.pieces.add(board[(5,3)])
        board[(3, 5)] = Piece(False, False, (3, 5))
        self.pieces.add(board[(3,5)])
        return board

    def get_comp_pos(self, pos):
        return (7 - pos[0], 7 - pos[1])

    def reverse(self):
        board = {}
        pieces = set()
        for r, c in self.board:
            comp_pos = (7-r, 7-c)
            board[comp_pos] = self.board[(r, c)]
            if isinstance(board[comp_pos], Piece):
                comp_piece = Piece(board[comp_pos].red, board[comp_pos].is_king, comp_pos, board[comp_pos].cap)
                pieces.add(comp_piece)
        return Board(self.w, self.h, board, pieces)


    def move_piece(self, from_pos, to_pos, comp=False):
        if comp:
            actual_from = self.get_comp_pos(from_pos)
            actual_to = self.get_comp_pos(to_pos)
            piece = self.board[actual_from]
            self.board[actual_from] = None
            piece.pos = actual_to
            self.board[actual_to] = piece
            print(f'move from {actual_from} to {actual_to}')
        else:
            piece = self.board[from_pos]
            self.board[from_pos] = None
            piece.pos = to_pos
            self.board[to_pos] = piece
            print(f'move from {from_pos} to {to_pos}')

    def draw(self, win):
        for r, c in self.board:
            x, y = c * self.cell_w + 1, r * self.cell_h + 1
            w, h = self.cell_w - 2, self.cell_h - 2
            pygame.draw.rect(win, (0, 0, 0), pygame.rect.Rect(x, y, w, h), 0)

        for piece in self.pieces:
            piece.draw(win, self.cell_w, self.cell_h)

    def capture_piece(self, pos, comp=False):
        if comp:
            actual_pos = self.get_comp_pos(pos)
            print(actual_pos, self.board[pos])
            piece = self.board[actual_pos]
            self.board[pos] = None
            piece.cap = True
        else:
            print(pos, self.board[pos])
            piece = self.board[pos]
            self.board[pos] = None
            piece.cap = True
