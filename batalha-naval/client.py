# Externo
import json
import socket
import struct

# Local
import util

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
    enemy_rows = '  '.join([str(i) for i in range(1, num_ships + 1)])
    player_rows = '   '.join([str(i) for i in range(1, num_ships + 1)])
    print('  {}\t\t  {}'.format(enemy_rows, player_rows))
    
    for enemy_row, player_row in zip(boards['enemy'], boards['player']):
        player_row = list(map(
            lambda x: '- ' if x == '-' else x,
            player_row
        ))
        print(column + ' ' + '  '.join(enemy_row) + '\t\t' +
              column + ' ' + '  '.join(player_row))
        column = chr(ord(column) + 1)

    # Imprime a quantidade de navios afundados
    print('O inimigo tem {} acerto(s)'.format(hits['enemy']))
    print('Você tem {} acerto(s)\n'.format(hits['player']))

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


def place_ship(board, board_size, ship, ship_number):
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
        board[i][j] = ship['symbol'] + str(ship_number)
        
    
def new_board(ships, num_ships, board_size):
    """ Cria um novo tabuleiro, de acordo com as escolhas
    do jogador.

    @param ships tipos de navios.
    @param num_ships quantidade de navios.
    @param board_size tamanho do tabuleiro.
    
    @return matriz representando o tabuleiro.
    """

    enemy_board = [['-' for _ in range(board_size)]
                   for _ in range(board_size)]
    player_board = [['-' for _ in range(board_size)]
                    for _ in range(board_size)]

    for key, ship in ships.items():
        # Posiciona navio de acordo com tipo.
        for i in range(ship['quantity']):
            place_ship(player_board, board_size, ships[key], (i + 1))
            print_game(
                ships, num_ships,
                {'player': player_board, 'enemy': enemy_board},
                {'player': 0, 'enemy': 0}
            )
    
    return player_board


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
    enemy_board = [['-' for _ in range(board_size)]
                   for _ in range(board_size)]

    # Tabuleiro do jogador.
    player_board = new_board(ships, num_ships, board_size)

    # Dicionário contendo ambos os tabuleiros.
    boards = {'player': player_board, 'enemy': enemy_board}

    # Enviando tabuleiro do jogador para o servidor.
    data = json.dumps(boards['player']).encode()
    client.send(struct.pack('!I', len(data)))
    client.send(data)
    
    print('\n\nMarquinhos Gameplay: Comeeeeeeeeça o jogo!')
    start_game(client, ships, num_ships, boards, board_size)


def start_game(conn, ships, num_ships, boards, board_size):
    # Rodada inicial: jogador.
    turn = util.Turn.PLAYER
    winner = util.Winner.NONE
        
    while winner == util.Winner.NONE:
        if turn == util.Turn.PLAYER:
            i, j = get_coord(board_size)
            data = json.dumps({'row': i, 'col': j}).encode()
            conn.send(struct.pack('!I', len(data)))
            conn.send(data)

            # Lê o resultado do movimento.
            data, = struct.unpack('!I', conn.recv(4))
            res = util.MoveStatus(data)

            print('Resultado da sua jogada: {}'.format(
                util.MoveResult[res]
            ))

            if res == util.MoveStatus.HIT:
                boards['enemy'][i][j] = 'x'
            else:
                boards['enemy'][i][j] = '*'
        else:
            # Lê o resultado do movimento.
            length, = struct.unpack('!I', conn.recv(4))
            i, j = json.loads(conn.recv(length).decode()).values()
            
            data, = struct.unpack('!I', conn.recv(4))
            res = util.MoveStatus(data)

            print('Resultado da jogada inimiga: {}'.format(
                util.MoveResult[res]
            ))
            
            if res == util.MoveStatus.HIT:
                boards['player'][i][j] = 'x '
            else:
                boards['player'][i][j] = '* '
        
        length, = struct.unpack('!I', conn.recv(4))
        hits = json.loads(conn.recv(length).decode())
        print_game(ships, num_ships, boards, hits)

        data, = struct.unpack('!I', conn.recv(4))
        winner = util.Winner(data)

        data, = struct.unpack('!I', conn.recv(4))
        turn = util.Turn(data)
        
if __name__ == '__main__':
    prepare_game()
