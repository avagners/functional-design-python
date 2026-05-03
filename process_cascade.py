from dataclasses import dataclass
from enum import Enum
import random
from typing import List, Optional


class MatchDirection(Enum):
    HORIZONTAL = "Horizontal"
    VERTICAL = "Vertical"


@dataclass(frozen=True)
class Element:
    Symbol: str = "EMPTY"


@dataclass
class Match:
    Direction: MatchDirection
    Row: int
    Col: int
    Length: int


@dataclass
class Board:
    size: int
    cells: List[List[Element]]


@dataclass
class BoardState:
    Board: Board
    Score: int


SYMBOLS = ["A", "B", "C", "D", "E"]


def find_matches(board: Board) -> List[Match]:
    """Find all matches of 3 or more matching elements on the board."""
    matches: List[Match] = []

    # Horizontal matches
    for row in range(board.size):
        start_col = 0
        for col in range(1, board.size):
            # Skip empty cells at the start of the row
            if board.cells[row][start_col].Symbol == "EMPTY":
                start_col = col
                continue

            # If current cell is empty, break current sequence
            if board.cells[row][col].Symbol == "EMPTY":
                add_match_if_valid(matches, row, start_col, col - start_col, MatchDirection.HORIZONTAL)
                start_col = col + 1
                continue

            # Check symbol match for non-empty cells
            if board.cells[row][col].Symbol != board.cells[row][start_col].Symbol:
                add_match_if_valid(matches, row, start_col, col - start_col, MatchDirection.HORIZONTAL)
                start_col = col
            elif col == board.size - 1:
                add_match_if_valid(matches, row, start_col, col - start_col + 1, MatchDirection.HORIZONTAL)

    # Vertical matches
    for col in range(board.size):
        start_row = 0
        for row in range(1, board.size):
            # Skip empty cells at the start of the column
            if board.cells[start_row][col].Symbol == "EMPTY":
                start_row = row
                continue

            # If current cell is empty, break current sequence
            if board.cells[row][col].Symbol == "EMPTY":
                add_match_if_valid(matches, start_row, col, row - start_row, MatchDirection.VERTICAL)
                start_row = row + 1
                continue

            # Check symbol match for non-empty cells
            if board.cells[row][col].Symbol != board.cells[start_row][col].Symbol:
                add_match_if_valid(matches, start_row, col, row - start_row, MatchDirection.VERTICAL)
                start_row = row
            elif row == board.size - 1:
                add_match_if_valid(matches, start_row, col, row - start_row + 1, MatchDirection.VERTICAL)

    return matches


def add_match_if_valid(matches: List[Match], row: int, col: int, length: int, direction: MatchDirection) -> None:
    # Consider only matches of 3 or more elements
    if length >= 3:
        matches.append(Match(direction, row, col, length))


def mark_cells_for_removal(board: Board, matches: List[Match]) -> List[List[Element]]:
    new_cells = [row[:] for row in board.cells]

    for match in matches:
        for i in range(match.Length):
            row = match.Row if match.Direction == MatchDirection.HORIZONTAL else match.Row + i
            col = match.Col + i if match.Direction == MatchDirection.HORIZONTAL else match.Col
            new_cells[row][col] = Element()

    return new_cells


def apply_gravity(cells: List[List[Element]], size: int) -> List[List[Element]]:
    new_cells = [[Element() for _ in range(size)] for _ in range(size)]

    for col in range(size):
        new_row = size - 1
        for row in range(size - 1, -1, -1):
            if cells[row][col].Symbol != "EMPTY":
                new_cells[new_row][col] = cells[row][col]
                new_row -= 1

    return new_cells


def calculate_score(removed_count: int) -> int:
    # Base scoring system: 10 points per element
    return removed_count * 10


def remove_matches(current_state: BoardState, matches: List[Match]) -> BoardState:
    """Remove matched cells, apply gravity, and update score."""
    if not matches:
        return current_state

    # Step 1: Mark cells for removal
    marked_cells = mark_cells_for_removal(current_state.Board, matches)

    # Step 2: Apply gravity
    gravity_applied_cells = apply_gravity(marked_cells, current_state.Board.size)

    # Step 3: Calculate score
    removed_count = sum(match.Length for match in matches)
    new_score = current_state.Score + calculate_score(removed_count)

    # Return NEW state
    return BoardState(
        Board(size=current_state.Board.size, cells=gravity_applied_cells),
        new_score
    )


def fill_empty_spaces(current_state: BoardState) -> BoardState:
    """Fill empty cells with random symbols."""
    if not current_state.Board.cells:
        return current_state

    new_cells = [row[:] for row in current_state.Board.cells]

    for row in range(current_state.Board.size):
        for col in range(current_state.Board.size):
            if new_cells[row][col].Symbol == "EMPTY":
                new_cells[row][col] = Element(random.choice(SYMBOLS))

    return BoardState(
        Board(size=current_state.Board.size, cells=new_cells),
        current_state.Score
    )


def initialize_game(board_size: int = 8) -> BoardState:
    """
    Initialize game board with random elements and ensure no initial matches.
    
    This function creates a new board with random elements, then processes it
    through the cascade algorithm to eliminate any initial matches.
    
    Returns:
        BoardState: Initialized game board with no matches
    """
    # 1. Create empty board state
    empty_state = BoardState(Board(size=board_size), 0)
    
    # 2. Fill empty spaces with random symbols
    filled_state = fill_empty_spaces(empty_state)
    
    # 3. Process cascade to remove any initial matches
    return process_cascade(filled_state)
