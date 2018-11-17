# Externo
import enum

Turn = enum.Enum('Turn', 'SERVER PLAYER')
MoveStatus = enum.Enum('MoveStatus', 'HIT MISS INVALID')

def make_move(board, row, col):
    """ Faz a jogada no tabuleiro e retorna o resultado. """
    
    res = MoveStatus.HIT
    if board[row][col] == '-':
        res = MoveStatus.MISS
    elif board[row][col] == '*' or board[row][col] == 'x':
        res = MoveStatus.INVALID

    return res
