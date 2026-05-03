#!/usr/bin/env python3
"""Демонстрация работы функционального каскадного алгоритма."""

from process_cascade import (
    Board,
    BoardState,
    Element,
    initialize_game,
    find_matches,
    remove_matches,
    fill_empty_spaces,
)


def print_board(board: Board, title: str = "Board") -> None:
    """Вывести игровую доску в читаемом формате."""
    print(f"\n{title} (size={board.size}):")
    for row in board.cells:
        print("  ", " ".join(cell.Symbol for cell in row))


def main():
    print("=== Демонстрация работы каскадного алгоритма ===\n")
    
    # 1. Создаем доску с готовыми совпадениями
    print("1. Создаем доску с горизонтальным совпадением из 3 'A':")
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
    print_board(state.Board, "Исходная доска")
    
    # 2. Находим совпадения
    print("\n2. Находим совпадения:")
    matches = find_matches(state.Board)
    print(f"   Найдено {len(matches)} совпадение(ий)")
    for match in matches:
        print(f"   - {match.Direction.name} совпадение длиной {match.Length} на ({match.Row}, {match.Col})")
    
    # 3. Удаляем совпадения
    print("\n3. Удаляем совпадения:")
    state_after_removal = remove_matches(state, matches)
    print_board(state_after_removal.Board, "После удаления")
    print(f"   Очки: {state_after_removal.Score}")
    
    # 4. Заполняем пустые клетки
    print("\n4. Заполняем пустые клетки случайными символами:")
    state_after_filling = fill_empty_spaces(state_after_removal)
    print_board(state_after_filling.Board, "После заполнения")
    print(f"   Очки: {state_after_filling.Score}")
    
    # 5. Инициализируем новую игру
    print("\n5. Инициализация новой игры (размер 5x5):")
    initial_state = initialize_game(5)
    print_board(initial_state.Board, "Инициализированная доска")
    print(f"   Очки: {initial_state.Score}")
    print(f"   Доска не содержит пустых клеток: {all(cell.Symbol != 'EMPTY' for row in initial_state.Board.cells for cell in row)}")
    
    print("\n=== Демонстрация завершена ===")


if __name__ == "__main__":
    main()
