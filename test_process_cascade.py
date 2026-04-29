from process_cascade import (
    Board,
    BoardState,
    Element,
    Match,
    MatchDirection,
    process_cascade,
    find_matches,
)


def test_process_cascade_no_matches():
    board = Board(
        size=3,
        cells=[
            [Element("A"), Element("B"), Element("C")],
            [Element("D"), Element("E"), Element("F")],
            [Element("G"), Element("H"), Element("I")],
        ],
    )
    state = BoardState(Board=board, Score=0)
    result = process_cascade(state)
    assert result == state


def test_process_cascade_with_matches():
    board = Board(
        size=3,
        cells=[
            [Element("A"), Element("A"), Element("A")],
            [Element("B"), Element("C"), Element("D")],
            [Element("E"), Element("F"), Element("G")],
        ],
    )
    state = BoardState(Board=board, Score=0)
    result = process_cascade(state)

    # After removing horizontal match of 3 "A"s, gravity should pull "B", "C", "D" down
    # and fill empty spaces with new random symbols
    assert result.Score == 30  # 3 elements * 10 points each
    # Check that the board has no empty cells after filling
    for row in result.Board.cells:
        for cell in row:
            assert cell.Symbol != "EMPTY"


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
            [Element("A"), Element("B"), Element("C")],
            [Element("A"), Element("E"), Element("F")],
        ],
    )
    matches = find_matches(board)
    assert len(matches) == 2
    assert matches[0].Direction == MatchDirection.HORIZONTAL
    assert matches[0].Row == 0
    assert matches[0].Col == 0
    assert matches[0].Length == 3
    assert matches[1].Direction == MatchDirection.VERTICAL
    assert matches[1].Row == 0
    assert matches[1].Col == 0
    assert matches[1].Length == 3


def test_process_cascade_recursive():
    # Create a board with matches that will cascade
    board = Board(
        size=4,
        cells=[
            [Element("A"), Element("A"), Element("A"), Element("B")],
            [Element("C"), Element("D"), Element("E"), Element("F")],
            [Element("G"), Element("H"), Element("I"), Element("J")],
            [Element("K"), Element("L"), Element("M"), Element("N")],
        ],
    )
    state = BoardState(Board=board, Score=0)
    result = process_cascade(state)

    # After removing horizontal match of 3 "A"s, gravity should pull down the column
    # This may create new matches depending on the symbols that fall into place
    assert result.Score >= 30  # At least 30 points from the first match