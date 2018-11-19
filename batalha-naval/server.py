# Externo
import json
import random
import socket
import struct
import threading

# Local
import util
    
def random_orientation():
    """ Retorna a orientação do navio a ser inserido. 

    @return tupla informando a orientação (1, 0) ou (0, 1).
    """
    
    horizontal = random.randint(0, 1)
    return (horizontal, 1 - horizontal)


def place_random_ship(board, ship, ship_number, orientation):
    """ Posiciona um navio randomicamente no tabuleiro. """

    horizontal, vertical = orientation
    fit = False
    
    while not fit:
        row = random.randint(0, len(board) - 1)
        col = random.randint(0, len(board[0]) - 1)

        for s in range(ship['size']):
            r = row + s * vertical
            c = col + s * horizontal

            if (r >= len(board) or c >= len(board[0]) or
                board[r][c] != '-'):

                break
            elif s == ship['size']-1:
                fit = True

    # Se o navio couber na posição dada, ele é posicionado.
    if fit:
        for s in range(ship['size']):
            r = row + s * vertical
            c = col + s * horizontal
            board[r][c] = ship['symbol'] + str(ship_number)
            
            
def random_board(ships, num_ships, board_size):
    """ Cria um novo tabuleiro, posicionando os navios
    de forma randômica.
    
    @param ships tipos de navios
    @param num_ships quantidade de navios
    @param board_size tamanho do tabuleiro

    @return matriz representando o tabuleiro.
    """
    
    board = [['-' for _ in range(board_size)]
             for _ in range(board_size)]

    for key, ship in ships.items():
        # Posiciona navio de acordo com tipo.
        for i in range(ship['quantity']):
            place_random_ship(
                board, ships[key],
                (i + 1), random_orientation()
            )

    return board


def prepare_game(conn):
    """ Realiza todos os preparativos necessários para
    o início de um novo jogo.

    @param conn conexão.
    @param client endereço.
    """

    ships = {
        'P': {'symbol': 'p', 'name': 'Porta Aviões',
              'size': 5, 'quantity': 1},
        'T': {'symbol': 't', 'name': 'Navio Tanque',
              'size': 4, 'quantity': 2},
        'C': {'symbol': 'c', 'name': 'Contratorpedeiro',
              'size': 3, 'quantity': 3},
        'S': {'symbol': 's', 'name': 'Submarino',
              'size': 2, 'quantity': 4}
    }

    # Parâmetros do jogo.
    board_size = 10
    num_ships = 10

    # Tabuleiro de jogo referente ao servidor.
    enemy_board = random_board(ships, num_ships, board_size)

    # Enviando dados iniciais para cliente.
    data = json.dumps(ships).encode()

    conn.send(struct.pack('!I', board_size))
    conn.send(struct.pack('!I', num_ships))
    conn.send(struct.pack('!I', len(data)))
    conn.send(data)

    length, = struct.unpack('!I', conn.recv(4))
    player_board = json.loads(conn.recv(length).decode())
    print(enemy_board)

    boards = {'player': player_board, 'enemy': enemy_board}
    start_game(conn, boards, board_size, ships, num_ships)

    
def random_coord(board_size):
    i = random.randint(0, board_size - 1)
    j = random.randint(0, board_size - 1)

    return (i, j)


def make_move(board, row, col):
    """ Faz a jogada no tabuleiro e retorna o resultado. """
    
    res = util.MoveStatus.HIT
    if board[row][col] == '-':
        res = util.MoveStatus.MISS
    elif board[row][col] == '*' or board[row][col] == 'x':
        res = util.MoveStatus.INVALID

    return res

    
def start_game(conn, boards, board_size, ships, num_ships):
    # Turno inicial: jogador.
    turn = util.Turn.PLAYER
    winner = util.Winner.NONE
    hits = {'player': 0, 'enemy': 0}

    hits_needed = 0
    for _, ship in ships.items():
        hits_needed += ship['quantity'] * ship['size']

    while winner == util.Winner.NONE:
        while turn == util.Turn.PLAYER:
            length, = struct.unpack('!I', conn.recv(4))
            i, j = json.loads(conn.recv(length).decode()).values()
            res = make_move(boards['enemy'], i, j)

            conn.send(struct.pack('!I', res.value))
            if res == util.MoveStatus.HIT:
                hits['player'] += 1
            else:
                turn = util.Turn.ENEMY

            data = json.dumps(hits).encode()
            conn.send(struct.pack('!I', len(data)))
            conn.send(data)

            if hits['player'] == hits_needed:
                winner = util.Winner.PLAYER
                conn.send(struct.pack('!I', winner.value))
                break
            else:
                conn.send(struct.pack('!I', winner.value))

            conn.send(struct.pack('!I', turn.value))
        
        while turn == util.Turn.ENEMY:
            i, j = random_coord(board_size)
            res = make_move(boards['player'], i, j)
            
            data = json.dumps({'row': i, 'col': j}).encode()
            conn.send(struct.pack('!I', len(data)))
            conn.send(data)
            
            print(res)
            print(res.value)
            conn.send(struct.pack('!I', res.value))
            if res == util.MoveStatus.HIT:
                hits['enemy'] += 1
                # TODO: Continuar da posição
            else:
                turn = util.Turn.PLAYER
                
            data = json.dumps(hits).encode()
            conn.send(struct.pack('!I', len(data)))
            conn.send(data)

            if hits['enemy'] == hits_needed:
                winner = util.Winner.ENEMY
                conn.send(struct.pack('!I', winner.value))
                break
            else:
                conn.send(struct.pack('!I', winner.value))

            conn.send(struct.pack('!I', turn.value))

    conn.close()

    
def start_server():
    """ Inicializa o servidor e espera por conexões. Quando
    uma conexão é feita, cria uma nova thread específica
    para a nova conexão, dando início a uma nova partida.
    """
    
    host = util.get_address()
    port = int(input('Porta: '))

    # Cria o socket do servnameor, declarando a família do protocolo
    # através do parâmetro AF_INET, bem como o protocolo TCP,
    # através do parâmetro SOCKET_STREAM.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))

    # Define um limite de 5 conexões simultâneas esperando
    # na fila.
    server.listen(5)

    print('Servidor iniciado. Aguardando conexões...')
    print('Host: {}\t Porta: {}'.format(host, port))

    # Inicia a escuta por possíveis conexões
    while True:
        conn, client = server.accept()
        print('{} conectado. Preparando novo jogo...'.format(client[0]))
        threading.Thread(target=prepare_game, args=(conn, )).start()


if __name__ == '__main__':
    start_server()
