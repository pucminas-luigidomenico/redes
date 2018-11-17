# Externo
import json
import socket
import struct

def print_game(ships, num_ships, boards, player_hits, enemy_hits):
    """ Mostra na tela o estado atual do jogo. """
    column = 'A'

    print('\nTabuleiro Inimigo\t\t\tMeu Tabuleiro')

    # Imprime os tabuleiros do inimigo e do jogador
    rows = '  '.join([str(i) for i in range(1, num_ships + 1)])
    print('  {}\t\t  {}'.format(rows, rows))
    
    for (enemy_row, player_row) in zip(boards['enemy'], boards['player']):
        print(column + ' ' + '  '.join(enemy_row) + '\t\t' +
              column + ' ' + '  '.join(player_row))
        column = chr(ord(column) + 1)

    # Imprime a quantidade de navios afundados
    print('O inimigo tem {} afundado(s)'.format(player_hits))
    print('Você tem {} afundado(s)\n'.format(enemy_hits))

    for _, ship in ships.items():
        print('-> {}: {}'.format(ship['symbol'], ship['name']))
    print('-> -: Posição válida')
    print('-> *: Falha')
    print('-> x: Acerto\n')


def place_ship(board, board_size, ship):
    """ Posiciona navio no tabuleiro, de acordo
    com posição informada pelo jogador. 

    @param board tabuleiro
    @param ship tipo de navio
    """

    fit = False
    positions = []
    
    while not fit:
        try:
            pos = input('Insira a posição separando com espaço (e.g.: A 3): ')
            row, col = pos.split(' ')
            row = ord(row.upper()) - ord('A')
            col = int(col) - 1

            direction = input('Insira a direção (Horizontal: H, Vertical: V): ').upper()

            if not direction:
                raise Exception
        except:
            print('Opção inválida!')
            continue
    
        horizontal, vertical = (direction == 'H', direction == 'V')
        for s in range(ship['size']):
            r = row + s * vertical
            c = col + s * horizontal

            if (r >= len(board) or c >= len(board[0]) or
                board[r][c] != '-'):
                
                break
            elif s == ship['size'] - 1:
                fit = True
                positions = [(row + vertical * i, col + horizontal * i)
                             for i in range(ship['size'])]

        if not fit:
            print('Posição inválida!')

    for i, j in positions:
        board[i][j] = ship['symbol']
        
    
def new_board(ships, num_ships, board_size):
    """ Cria um novo tabuleiro, de acordo com as escolhas
    do jogador.

    @param ships tipos de navios
    @param num_ships quantidade de navios
    @param board_size tamanho do tabuleiro
    
    @return matriz representando o tabuleiro.
    """
    
    board = [['-'] * board_size for i in range(board_size)]

    # Posiciona Porta-Avião.
    print('\nPosicionando porta-avião')
    place_ship(board, board_size, ships['P'])

    # Posiciona Navios-Tanque.
    for i in range(1, 3):
        print('\nPosicionando navio-tanque nº {}'.format(i))
        place_ship(board, board_size, ships['T'])

    # Posiciona Contratorpedeiros.
    for i in range(1, 4):
        print('\nPosicionando contratorpedeiro nº {}'.format(i))
        place_ship(board, board_size, ships['C'])

    # Posiciona Submarinos.
    for i in range(1, 5):
        print('\nPosicionando submarino nº {}'.format(i))
        place_ship(board, board_size, ships['S'])
    
    return board


def start_game():
    """ Inicializa conexão com o servidor, para novo jogo. """
    
    print('{} Batalha Naval {}\n'.format('=' * 30, '=' * 30))
    host = input('Insira o IP do servidor: ')
    port = int(input('Insira a porta para conexão: '))

    # Cria o socket do servnameor, declarando a família do protocolo
    # através do parâmetro AF_INET, bem como o protocolo TCP,
    # através do parâmetro SOCKET_STREAM.
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Recebe dados iniciais do jogo.
    # A função <struct.unpack> retorna uma tupla que, nesse caso,
    # contém apenas um elemento.
    board_size, = struct.unpack('!I', client.recv(4))
    num_ships, = struct.unpack('!I', client.recv(4))
    
    length, = struct.unpack('!I', client.recv(4))
    ships = json.loads(client.recv(length).decode())

    # Tabuleiro inimigo.
    enemy_board = [['-'] * board_size] * board_size
    player_hits = 0
    enemy_hits = 0

    # Tabuleiro do jogador.
    player_board = new_board(ships, num_ships, board_size)
    print_game(
        ships,
        num_ships,
        {'player': player_board, 'enemy': enemy_board},
        player_hits, enemy_hits
    )
    
    winner = None
    while not winner:
        pass
    
    client.close()


if __name__ == '__main__':
    start_game()
