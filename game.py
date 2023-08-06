import numpy as np


def checker_game(possible_moves, game_board):
    if(game_board is None):
        game_board = create_checkers_board(possible_moves)
        print("\n")
        print(game_board)
        print("\n")
    return game_board


def create_checkers_board(possible_moves):
    board = np.zeros((8, 8), dtype=int)
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 1:
                if row < 3:
                    board[row, col] = 2 # Black stones
                elif row > 4:
                    board[row, col] = 1 # White stones
            if(possible_moves[row, col] == 3):
                board[row, col] = 3 # Possible moves
    return board