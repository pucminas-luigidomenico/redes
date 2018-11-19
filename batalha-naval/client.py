# Externo
import json
import socket
import struct

# Local
import common

def print_game(ships, num_ships, boards, hits):
    """ Mostra na tela o estado atual do jogo. 
    
    @param ships tipos de navios.
    @param num_ships quantidade de navios.
    @param boards tabuleiros (inimigo e jogador).
    @param hits acertos (inimigo e jogador).
    """
    
    column = 'A'

    print('\nTabuleiro Inimigo\t\t\tMeu Tabuleiro')

    # Imprime os tabuleiros do inimigo e do jogador
    rows = '  '.join([str(i) for i in range(1, num_ships + 1)])
    print('  {}\t\t  {}'.format(rows, rows))
    
    for enemy_row, player_row in zip(boards['enemy'], boards['player']):
        print(column + ' ' + '  '.join(enemy_row) + '\t\t' +
              column + ' ' + '  '.join(player_row))
        column = chr(ord(column) + 1)

    # Imprime a quantidade de navios afundados
    print('O inimigo tem {} afundado(s)'.format(hits['player']))
    print('Você tem {} afundado(s)\n'.format(hits['enemy']))

    for _, ship in ships.items():
        print('-> {}: {}'.format(ship['symbol'], ship['name']))
    print('-> -: Posição válida')
    print('-> *: Falha')
    print('-> x: Acerto\n')


def get_row(board_size):
    """ Retorna uma linha válida do tabuleiro, de acordo
    com a posição informada pelo jogador. 

    @param board_size tamanho do tabuleiro.

    @return inteiro representando a linha.
    """
    
    row = 'A'
    valid_pos = False
    while not valid_pos:
        try:
            row = (input('Escolha uma linha (A-J): '))
            row = row.upper()

            if ord(row) < ord('A') or ord(row) >= ord('A') + board_size:
                raise Exception()

            valid_pos = True
        except Exception:
            print('Caractere Inválido')

    return ord(row) - ord('A')


def get_column(board_size):
    """ Retorna uma coluna válida do tabuleiro, de acordo
    com a posição informada pelo jogador. 
    
    @param board_size tamanho do tabuleiro.

    @param inteiro representando a coluna.
    """
    
    col = 0
    valid_pos = False
    while not valid_pos:
        try:
            col = int(input('Escolha uma coluna (1-10): '))

            if col < 1 or col >= 1 + board_size:
                raise Exception()
            
            valid_pos = True
        except ValueError:
            print('Valor Inválido.')
        except Exception:
            print('Valor fora do Limite.')

    return col - 1
    

def get_direction():
    """ Retorna a orientação em que será colocado o navio (horizontal
    ou vertical).

    @return inteiro representando a direção, sendo 1 para horizontal e
    0 para vertical.
    """
    
    valid_dir = False
    while not valid_dir:
        try:
            d = input('Insira a direção (Horizontal: H, Vertical: V): ')
            d = d.upper()

            if d not in ['H', 'V']:
                raise Exception()

            valid_dir = True
        except Exception:
            print('Direção inválida!')
            
    return 1 if d == 'H' else 0


def get_coord(board_size):
    """ Retorna a coordenada informada pelo jogador. 

    @param board_size tamanho do tabuleiro.

    @return tupla contendo dois elementos: linha e coluna.
    """
    
    i = get_row(board_size)
    j = get_column(board_size)

    return (i, j)


def place_ship(board, board_size, ship):
    """ Posiciona navio no tabuleiro, de acordo
    com posição informada pelo jogador. 

    @param board tabuleiro.
    @param ship tipo de navio.
    """

    fit = False
    positions = []
    
    while not fit:
        row, col = get_coord(board_size)
        direction = get_direction()
        
        for s in range(ship['size']):
            r = row + s * (1 - direction)
            c = col + s * direction

            if (r >= len(board) or c >= len(board[0]) or
                board[r][c] != '-'):
                
                break
            elif s == ship['size'] - 1:
                fit = True
                positions = [(row + (1 - direction) * i,
                              col + direction * i)
                             for i in range(ship['size'])]

        if not fit:
            print('Posição inválida!')

    for i, j in positions:
        board[i][j] = ship['symbol']
        
    
def new_board(ships, num_ships, board_size):
    """ Cria um novo tabuleiro, de acordo com as escolhas
    do jogador.

    @param ships tipos de navios.
    @param num_ships quantidade de navios.
    @param board_size tamanho do tabuleiro.
    
    @return matriz representando o tabuleiro.
    """

    enemy_board = [['-'] * board_size for i in range(board_size)]
    player_board = [['-'] * board_size for i in range(board_size)]

    # Posiciona Porta-Avião.
    print('\nPosicionando porta-avião')
    place_ship(player_board, board_size, ships['P'])
    print_game(
        ships, num_ships,
        {'player': player_board, 'enemy': enemy_board},
        {'player': 0, 'enemy': 0}
    )
    
    # Posiciona Navios-Tanque.
    for i in range(1, 3):
        print('\nPosicionando navio-tanque nº {}'.format(i))
        place_ship(player_board, board_size, ships['T'])
        print_game(
            ships, num_ships,
            {'player': player_board, 'enemy': enemy_board},
            {'player': 0, 'enemy': 0}
        )
        
    # Posiciona Contratorpedeiros.
    for i in range(1, 4):
        print('\nPosicionando contratorpedeiro nº {}'.format(i))
        place_ship(player_board, board_size, ships['C'])
        print_game(
            ships, num_ships,
            {'player': player_board, 'enemy': enemy_board},
            {'player': 0, 'enemy': 0}
        )

    # Posiciona Submarinos.
    for i in range(1, 5):
        print('\nPosicionando submarino nº {}'.format(i))
        place_ship(player_board, board_size, ships['S'])
        print_game(
            ships, num_ships,
            {'player': player_board, 'enemy': enemy_board},
            {'player': 0, 'enemy': 0}
        )
    
    return board


def prepare_game():
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
    hits = {'player': 0, 'enemy': 0}

    # Tabuleiro do jogador.
    player_board = new_board(ships, num_ships, board_size)

    # Dicionário contendo ambos os tabuleiros.
    boards = {'player': player_board, 'enemy': enemy_board}

    print('\n\nMarquinhos Gameplay: Comeeeeeeeeça o jogo!', end='')
    start_game(client, ships, num_ships, boards, board_size, hits)

    
def start_game(conn, ships, num_ships, boards, board_size, hits):
    # Rodada inicial: jogador.
    turn = common.Turn.PLAYER
    winner = None

    while not winner:
        while turn == common.Turn.PLAYER:
            # Rodada do jogador.
            print_game(ships, num_ships, boards, hits)
            row, col = get_coord(board_size)

            # Envia ao servidor a jogada.
            data = json.dumps({'row': row, 'col': col}).encode()
            conn.send(struct.pack('!I', len(data)))
            conn.send(data)
            
            # Recebe resultado da jogada.
            res, = struct.unpack('!I', conn.recv(4))
            res = common.MoveStatus(res)

            if res == common.MoveStatus.HIT:
                print('Acerto em ({}, {})'.format(
                    chr(ord('A') + row),
                    col + 1
                ))
                boards['enemy'][row][col] = 'x'
                hits['player'] += 1
            else:
                turn = common.Turn.SERVER

        # Turno do inimigo (servidor).
        while turn == common.Turn.SERVER:
            pass

        
if __name__ == '__main__':
    prepare_game()
