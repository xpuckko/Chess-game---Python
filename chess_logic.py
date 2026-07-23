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
        self._has_moved = False

    @property
    def color(self):
        return self._color

    @property
    def piece_type(self):
        return self._piece_type

    @property
    def has_moved(self):
        return self._has_moved

    @has_moved.setter
    def has_moved(self, value: bool):
        self._has_moved = value

    def get_opposite_color(self):
        return Color.BLACK if self.color == Color.WHITE else Color.WHITE

class Position:
    def __init__(self, x: int, y: str):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Position({self.x}, {self.y!r})"

class Board:
    def __init__(self):
        self._board = self.create_board()
        self._en_passant_target: Position | None = None
        self._pieces_cache_dirty = True
        self._pieces_by_color_cache = {Color.WHITE: {}, Color.BLACK: {}}
        self._load_board(self._get_initial_pieces())

    @property
    def board(self):
        return self._board

    @property
    def en_passant_target(self):
        return self._en_passant_target

    @en_passant_target.setter
    def en_passant_target(self, value: Position | None):
        self._en_passant_target = value

    @property
    def pieces_by_color(self):
        if self._pieces_cache_dirty:
            self._rebuild_pieces_by_color()
            self._pieces_cache_dirty = False
        return self._pieces_by_color_cache

    def _rebuild_pieces_by_color(self):
        self._pieces_by_color_cache = {Color.WHITE: {}, Color.BLACK: {}}
        for x in range(1, 9):
            for y in "ABCDEFGH":
                pos = Position(x, y)
                piece = self.get_piece(pos)
                if piece is not None:
                    self._pieces_by_color_cache[piece.color][pos] = piece

    def create_board(self):
        return [[None for _ in range(8)] for _ in range(8)]

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

    def _to_index(self, position: Position) -> tuple[int, int]:
        return position.x - 1, ord(position.y) - ord('A')

    def set_piece(self, piece: Piece | None, position: Position):
        row_idx, col_idx = self._to_index(position)
        existing = self.board[row_idx][col_idx]

        if existing is not None and piece is not None and existing.color == piece.color:
            raise ValueError("Position already occupied")

        self.board[row_idx][col_idx] = piece
        self._pieces_cache_dirty = True

    def get_piece(self, position: Position) -> Piece | None:
        row_idx, col_idx = self._to_index(position)
        return self.board[row_idx][col_idx]

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
        new_x = position.x + direction

        if not (1 <= new_x <= 8):
            return candidates

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

        return candidates

    def _get_stepping_moves(self, position, piece, deltas):
        moves = []
        for dx, dy in deltas:
            new_x = position.x + dx
            new_y = chr(ord(position.y) + dy)
            if 1 <= new_x <= 8 and 'A' <= new_y <= 'H':
                new_position = Position(new_x, new_y)
                if self.is_empty(new_position) or self.get_piece(new_position).color != piece.color:
                    moves.append(new_position)
        return moves

    def _get_pawn_moves(self, position: Position, piece: Piece) -> List[Position]:
        direction = 1 if piece.color == Color.WHITE else -1
        moves: List[Position] = []

        middle = Position(position.x + direction, position.y)
        if self.is_empty(middle):
            moves.append(middle)

            start_rank = 2 if piece.color == Color.WHITE else 7
            if position.x == start_rank:
                end = Position(position.x + 2 * direction, position.y)
                if self.is_empty(end):
                    moves.append(end)

        moves.extend(self.can_take_pawn(position))

        if self.en_passant_target is not None:
            target = self.en_passant_target
            if target.x == position.x + direction and abs(ord(target.y) - ord(position.y)) == 1:
                moves.append(target)

        return moves

    def _get_knight_moves(self, position, piece):
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        return self._get_stepping_moves(position, piece, knight_moves)

    def _get_king_moves(self, position, piece):
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._get_stepping_moves(position, piece, king_moves)

    def pseudo_legal_moves(self, position: Position) -> List[Position]:
        piece = self.get_piece(position)
        if piece is None:
            return []

        moves: list[Position] = []

        match piece.piece_type:
            case PieceType.PAWN:
                return self._get_pawn_moves(position, piece)
            case PieceType.ROOK:
                return self._get_sliding_moves(position, piece, [(1,0),(-1,0),(0,1),(0,-1)])
            case PieceType.KNIGHT:
                return self._get_knight_moves(position, piece)
            case PieceType.BISHOP:
                return self._get_sliding_moves(position, piece, [(1,1),(1,-1),(-1,1),(-1,-1)])
            case PieceType.QUEEN:
                return self._get_sliding_moves(position, piece, [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)])
            case PieceType.KING:
                return self._get_king_moves(position, piece)

    def make_move(self, from_position: Position, to_position: Position,
                promotion_piece: PieceType | None = None) -> Piece | None:
        piece = self.get_piece(from_position)
        if piece is None:
            raise ValueError("No piece at the source position")
        if to_position not in self.pseudo_legal_moves(from_position):
            raise ValueError("Move is not pseudo-legal")

        is_promotion = self._is_promotion(piece, to_position)
        if is_promotion:
            self._validate_promotion_piece(promotion_piece)

        captured_piece = self._resolve_capture(piece, from_position, to_position)
        self._update_en_passant_target(piece, from_position, to_position)

        if is_promotion:
            piece = Piece(piece.color, promotion_piece)

        piece.has_moved = True
        self.set_piece(piece, to_position)
        self.set_piece(None, from_position)

        return captured_piece  # Game си append-ва в своя история


    def _is_promotion(self, piece: Piece, to_position: Position) -> bool:
        return piece.piece_type == PieceType.PAWN and (
            (to_position.x == 8 and piece.color == Color.WHITE) or
            (to_position.x == 1 and piece.color == Color.BLACK)
        )


    def _validate_promotion_piece(self, promotion_piece: PieceType | None):
        if promotion_piece is None or promotion_piece in (PieceType.PAWN, PieceType.KING):
            raise ValueError("Invalid promotion piece")


    def _resolve_capture(self, piece: Piece, from_position: Position, to_position: Position) -> Piece | None:
        is_en_passant = (
            piece.piece_type == PieceType.PAWN and
            self.en_passant_target is not None and
            to_position == self.en_passant_target and
            self.is_empty(to_position)
        )
        if is_en_passant:
            captured_position = Position(from_position.x, to_position.y)
            captured_piece = self.get_piece(captured_position)
            self.set_piece(None, captured_position)
            return captured_piece
        return self.get_piece(to_position)


    def _update_en_passant_target(self, piece: Piece, from_position: Position, to_position: Position):
        if piece.piece_type == PieceType.PAWN and abs(to_position.x - from_position.x) == 2:
            self.en_passant_target = Position((from_position.x + to_position.x) // 2, from_position.y)
        else:
            self.en_passant_target = None



   

    