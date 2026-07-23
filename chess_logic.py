from enum import Enum
from turtle import position
from typing import List
from webbrowser import get

class Color(Enum):
    WHITE = 1
    BLACK = 2

class PieceType(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6



class Piece:
    def __init__(self, color: Color, piece_type: PieceType):
        self._color = color
        self._piece_type = piece_type

    @property
    def color(self):
        return self._color

    @property
    def piece_type(self):
        return self._piece_type

    def get_opposite_color(self):
        return Color.BLACK if self.color == Color.WHITE else Color.WHITE

class Position:
    def __init__(self, x: int, y: str):
        if not (1 <= x <= 8):
            raise ValueError("Row must be between 1 and 8")

        if y not in "ABCDEFGH":
            raise ValueError("Column must be between A and H")

        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

class Board:
    def __init__(self):
        self._board=self.create_board()
        self._load_board(self._get_initial_pieces())

    @property
    def board(self):
        return self._board

    def create_board(self):
        board=[]
        for i in range(8):
            row=[]
            for j in range(8):
                row.append(None)
            board.append(row)
        return board


    def _get_initial_pieces(self) -> List[tuple[Piece, Position]]:
        pieces = []

        # White pieces
        pieces.append((Piece(Color.WHITE, PieceType.ROOK), Position(1, "A")))
        pieces.append((Piece(Color.WHITE, PieceType.KNIGHT), Position(1, "B")))
        pieces.append((Piece(Color.WHITE, PieceType.BISHOP), Position(1, "C")))
        pieces.append((Piece(Color.WHITE, PieceType.QUEEN), Position(1, "D")))
        pieces.append((Piece(Color.WHITE, PieceType.KING), Position(1, "E")))
        pieces.append((Piece(Color.WHITE, PieceType.BISHOP), Position(1, "F")))
        pieces.append((Piece(Color.WHITE, PieceType.KNIGHT), Position(1, "G")))
        pieces.append((Piece(Color.WHITE, PieceType.ROOK), Position(1, "H")))

        for column in "ABCDEFGH":
            pieces.append((Piece(Color.WHITE, PieceType.PAWN), Position(2, column)))

        # Black pieces
        pieces.append((Piece(Color.BLACK, PieceType.ROOK), Position(8, "A")))
        pieces.append((Piece(Color.BLACK, PieceType.KNIGHT), Position(8, "B")))
        pieces.append((Piece(Color.BLACK, PieceType.BISHOP), Position(8, "C")))
        pieces.append((Piece(Color.BLACK, PieceType.QUEEN), Position(8, "D")))
        pieces.append((Piece(Color.BLACK, PieceType.KING), Position(8, "E")))
        pieces.append((Piece(Color.BLACK, PieceType.BISHOP), Position(8, "F")))
        pieces.append((Piece(Color.BLACK, PieceType.KNIGHT), Position(8, "G")))
        pieces.append((Piece(Color.BLACK, PieceType.ROOK), Position(8, "H")))

        for column in "ABCDEFGH":
            pieces.append((Piece(Color.BLACK, PieceType.PAWN), Position(7, column)))

        return pieces

    def _load_board(self, pieces: List[tuple[Piece, Position]]):
        for piece, position in pieces:
            self.set_piece(piece, position)

    def set_piece(self, piece: Piece, position: Position):
        x, y = position.x, position.y

        if(self.board[x][y] is not None and self.board[x][y].color == piece.color):
            raise ValueError("Position already occupied")

        self.board[x][y]= piece

    def get_piece(self, position: Position)-> Piece:
        x, y = position.x, position.y
        return self.board[x][y]  

    def is_empty(self, position: Position) -> bool:
        return self.get_piece(position) is None

    def can_take_pawn(self, position: Position) -> List[Position]:
        piece: Piece = self.get_piece(position)
        candidates: list[Position] = []

        if piece is None:
            return candidates
        if piece.piece_type != PieceType.PAWN:
                return candidates

        direction = 1 if piece.color == Color.WHITE else -1

        if position.y == 'A':
            target= Position(position.x + direction, 'B')
            candidate = self.get_piece(target)
            if candidate is not None and candidate.color == piece.get_opposite_color():
                candidates.append(target)
        elif position.y == 'H':
            target= Position(position.x + direction, 'G')
            candidate = self.get_piece(target)
            if candidate is not None and candidate.color == piece.get_opposite_color():
                candidates.append(target)
        else:
            target1= Position(position.x + direction, chr(ord(position.y) - 1))
            target2= Position(position.x + direction, chr(ord(position.y) + 1))
            candidate1= self.get_piece(target1)
            candidate2= self.get_piece(target2)
            if candidate1 is not None and candidate1.color == piece.get_opposite_color():
                candidates.append(target1)
            if candidate2 is not None and candidate2.color == piece.get_opposite_color():
                candidates.append(target2)

         # TODO: en passant ще изисква self.en_passant_target,
         # ще го добавя след като имам make_move() и история на ходовете

        return candidates

    def _get_sliding_moves(self, position, piece, directions):
        moves = []

        for dx, dy in directions:
            x, y = position.x, ord(position.y)

            while True:
                x += dx
                y += dy

                if not (1 <= x <= 8 and ord('A') <= y <= ord('H')):
                    break

                new_position = Position(x, chr(y))

                if self.is_empty(new_position):
                    moves.append(new_position)
                else:
                    if self.get_piece(new_position).color != piece.color:
                        moves.append(new_position)
                    break

        return moves

    def pseudo_legal_moves(self, position: Position):
        piece = self.get_piece(position)
        if piece is None:
            return []

        moves: list[Position] = []

        match piece.piece_type:
            case PieceType.PAWN:
                direction = 1 if piece.color == Color.WHITE else -1

                middle = Position(position.x + direction, position.y)
                end = Position(position.x + 2 * direction, position.y)

                if self.is_empty(middle):
                    moves.append(middle)


                if position.x == 2 and piece.color == Color.WHITE and self.is_empty(middle) and self.is_empty(end):
                    moves.append(end)
                elif position.x == 7 and piece.color == Color.BLACK and self.is_empty(middle) and self.is_empty(end):
                    moves.append(end)

                candidates: list[Position] = self.can_take_pawn(position)
                moves.extend(candidates)

                return moves

            case PieceType.ROOK:
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                return self._get_sliding_moves(position, piece, directions)

            case PieceType.KNIGHT:
                knight_moves = [
                    (2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

                for dx,dy in knight_moves:
                    new_x = position.x + dx
                    new_y = chr(ord(position.y) + dy)

                    if 1 <= new_x <= 8 and ord('A') <= new_y <= ord('H'):
                        new_position = Position(new_x, new_y)
                        if self.is_empty(new_position) or self.get_piece(new_position).color != piece.color:
                            moves.append(new_position)
                return moves

            case PieceType.BISHOP:
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                return self._get_sliding_moves(position, piece, directions)

            case PieceType.QUEEN:
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
                return self._get_sliding_moves(position, piece, directions)

            case PieceType.KING:
                king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

                for dx, dy in king_moves:
                    x,y = position.x, ord(position.y)
                    
                    new_x=x+dx
                    new_y=chr(y+dy)

                    if 1 <= new_x <= 8 and ord('A') <= new_y <= ord('H'):
                        new_position = Position(new_x, new_y)
                        if self.is_empty(new_position) or self.get_piece(new_position).color != piece.color:
                            moves.append(new_position)
                    
                return moves

    def make_move(self, from_position:Position, to_position: Position) -> Piece | None:
        piece = self.get_piece(from_position)
        if piece is None:
            raise ValueError("No piece at the source position")

        if to_position not in self.pseudo_legal_moves(from_position):
            raise ValueError("Move is not pseudo-legal")

        captured_piece = self.get_piece(to_position)
        self.set_piece(piece, to_position)
        self.set_piece(None, from_position)

        return captured_piece

   

    