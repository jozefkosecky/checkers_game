import numpy as np


def checker_game(possible_moves, game_board,was_move_made):
    if(game_board is None):
        game_board = create_checkers_board(possible_moves)
        print("\n")
        print(possible_moves)
        print("\n")

        print("\n")
        print(game_board)
        print("\n")

    if(was_move_made):
        game_board = update_checkers_board(possible_moves, game_board)
        print("\n")
        print(possible_moves)
        print("\n")

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

def update_checkers_board(possible_moves, game_board):
    board = np.zeros((8, 8), dtype=int)
    new_stone_position = None
    stone = None
    for row in range(8):
        for col in range(8):
            if(game_board[row, col] == 3 and possible_moves[row, col] != 3):
                new_stone_position = [row, col]
            if(possible_moves[row, col] == 3 and (game_board[row, col] == 1 or game_board[row, col] == 2)):
                stone = game_board[row, col]

    if(new_stone_position != None and stone != None):
        for row in range(8):
            for col in range(8):
                if(new_stone_position == [row, col]):
                    board[row, col] = stone
                elif(possible_moves[row, col] == 3):
                    board[row, col] = 3
                else:
                    board[row, col] =  game_board[row, col]
    else:
        board = game_board
    return board