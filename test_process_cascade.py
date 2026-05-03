from process_cascade import (
    Board,
    BoardState,
    Element,
    Match,
    MatchDirection,
    find_matches,
    initialize_game,
    GameInitializer,
)


def test_find_matches_horizontal():
    board = Board(
        size=3,
        cells=[
            [Element("A"), Element("A"), Element("A")],
            [Element("B"), Element("C"), Element("D")],
            [Element("E"), Element("F"), Element("G")],
        ],
    )
    matches = find_matches(board)
    assert len(matches) == 1
    assert matches[0].Direction == MatchDirection.HORIZONTAL
    assert matches[0].Row == 0
    assert matches[0].Col == 0
    assert matches[0].Length == 3


def test_find_matches_vertical():
    board = Board(
        size=3,
        cells=[
            [Element("A"), Element("B"), Element("C")],
            [Element("A"), Element("C"), Element("D")],
            [Element("A"), Element("F"), Element("G")],
        ],
    )
    matches = find_matches(board)
    assert len(matches) == 1
    assert matches[0].Direction == MatchDirection.VERTICAL
    assert matches[0].Row == 0
    assert matches[0].Col == 0
    assert matches[0].Length == 3


def test_find_matches_multiple():
    board = Board(
        size=3,
        cells=[
            [Element("A"), Element("A"), Element("A")],
            [Element("A"), Element("A"), Element("A")],
            [Element("D"), Element("E"), Element("F")],
        ],
    )
    matches = find_matches(board)
    assert len(matches) == 2
    assert matches[0].Direction == MatchDirection.HORIZONTAL
    assert matches[0].Row == 0
    assert matches[0].Col == 0
    assert matches[0].Length == 3
    assert matches[1].Direction == MatchDirection.HORIZONTAL
    assert matches[1].Row == 1
    assert matches[1].Col == 0
    assert matches[1].Length == 3


def test_initialize_game():
    # Test that initialize_game creates a valid board
    state = initialize_game(3)
    
    # Board should be created
    assert state.Board.size == 3
    assert state.Board.cells is not None
    assert len(state.Board.cells) == 3
    
    # All cells should be filled (no EMPTY symbols)
    for row in state.Board.cells:
        for cell in row:
            assert cell.Symbol != "EMPTY"
    
    # Score should be 0 (no matches removed during initialization)
    assert state.Score == 0


def test_game_initializer_builder():
    # Test the Builder pattern
    state = (
        GameInitializer(3)
        .fill_empty()
        .process_cascade()
        .build()
    )
    
    # Board should be created
    assert state.Board.size == 3
    assert state.Board.cells is not None
    assert len(state.Board.cells) == 3
    
    # All cells should be filled (no EMPTY symbols)
    for row in state.Board.cells:
        for cell in row:
            assert cell.Symbol != "EMPTY"