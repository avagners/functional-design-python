from dataclasses import dataclass
from enum import Enum
import random
from typing import List, Optional, Callable, TypeVar


T = TypeVar('T')


def pipe(value: T, func: Callable[[T], any]) -> any:
    """
    Pipe function for pipeline-style processing.
    
    Allows chaining function calls in a readable left-to-right manner.
    This is a standalone function that enables the pipe pattern.
    
    Example:
        result = pipe(data, transform).pipe(filter).pipe(collect)
    """
    return func(value)


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


# Extension method for BoardState to enable pipe pattern with dot notation
BoardState.pipe = lambda self, func: func(self)


def draw(board_state: BoardState, ask: bool = False) -> BoardState:
    """
    Draw the board state to console for debugging.
    
    This function prints the board in a readable format, similar to the C# example
    in materials 21) and 22).
    
    Args:
        board_state: The board state to draw
        ask: If True, waits for user input after drawing (for debugging)
    
    Returns:
        The same board state (for pipeline chaining)
    """
    board = board_state.Board
    print(f"  {' '.join(str(i) for i in range(board.size))}")
    for i in range(board.size):
        print(f"{i} {' '.join(cell.Symbol for cell in board.cells[i])}")
    print()
    if ask:
        input("Press Enter to continue...")
    return board_state


class GameInitializer:
    """Builder pattern for initializing game state with fluent interface."""
    
    def __init__(self, board_size: int = 8):
        self.board_size = board_size
        # Create empty board with empty cells
        empty_cells = [[Element() for _ in range(board_size)] for _ in range(board_size)]
        self.current_state = BoardState(Board(size=board_size, cells=empty_cells), 0)
    
    def fill_empty(self) -> 'GameInitializer':
        """Fill empty spaces with random symbols."""
        self.current_state = fill_empty_spaces(self.current_state)
        return self
    
    def process_cascade(self) -> 'GameInitializer':
        """Process the board to remove any matches."""
        self.current_state = process_cascade_recursive(self.current_state)
        return self
    
    def build(self) -> BoardState:
        """Return the final initialized game state."""
        return self.current_state


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


def build_game_pipeline(debug: bool = False) -> Callable[[BoardState], BoardState]:
    """
    Build the game processing pipeline as a function.
    
    This function creates a pipeline that chains the main processing steps
    (fill_empty_spaces, process_cascade_recursive) for use in the main algorithm.
    Corresponds to BuildGamePipeline() from material 24).
    
    Args:
        debug: If True, includes draw() calls in the pipeline for debugging
    
    Returns:
        A function that takes BoardState and returns processed BoardState
    
    Example:
        pipeline = build_game_pipeline(debug=True)
        state.pipe(pipeline)
    """
    def pipeline(bs: BoardState) -> BoardState:
        result = bs.pipe(fill_empty_spaces)
        if debug:
            result.pipe(draw)
        return result.pipe(lambda state: process_cascade_recursive(state, debug))
    
    return pipeline


def initialize_game(board_size: int = 8, debug: bool = False) -> BoardState:
    """
    Initialize game board with random elements and ensure no initial matches.
    
    Uses pipe pattern for pipeline-style processing, making the code readable
    from left to right, exactly as shown in the materials 24).
    
    Args:
        board_size: Size of the board (default 8)
        debug: If True, draws intermediate board states for debugging
    
    Returns:
        BoardState: Initialized game board with no matches
    
    Example:
        state = initialize_game(8)
        state = initialize_game(8, debug=True)
    """
    # Create empty board state and apply the pipeline
    return (
        BoardState(
            Board(size=board_size, cells=[[Element() for _ in range(board_size)] for _ in range(board_size)]),
            0
        )
        .pipe(build_game_pipeline(debug))
    )


def process_cascade_pipeline(current_state: BoardState, matches: List[Match], debug: bool = False) -> BoardState:
    """
    Pipeline function that chains the main processing steps.
    
    This function encapsulates the pipeline as a separate function,
    as suggested in material 23) "Конвейер как функция".
    
    Args:
        current_state: Current board state
        matches: List of matches to remove
        debug: If True, draws intermediate board states for debugging
    
    Returns:
        Processed board state
    
    Example:
        state.pipe(lambda bs: process_cascade_pipeline(bs, find_matches(bs.Board)))
    """
    intermediate = (
        current_state
        .pipe(lambda bs: remove_matches(bs, matches))
    )
    
    if debug:
        intermediate.pipe(draw)
    
    return intermediate.pipe(fill_empty_spaces)


def process_cascade_recursive(current_state: BoardState, debug: bool = False) -> BoardState:
    """
    Recursively process the board to remove all matches using pipeline style.
    
    This function uses the pipe pattern to chain operations in a readable way,
    exactly as shown in the materials 20), 21), and 22).
    
    Args:
        current_state: Current board state
        debug: If True, draws intermediate board states for debugging
    
    Returns:
        Processed board state
    
    Example:
        state.pipe(process_cascade_recursive)
    """
    matches = find_matches(current_state.Board)
    if not matches:
        return current_state
    
    # Chain operations using pipe pattern with dot notation
    return (
        current_state
        .pipe(lambda bs: process_cascade_pipeline(bs, matches, debug))
        .pipe(lambda bs: process_cascade_recursive(bs, debug))
    )
