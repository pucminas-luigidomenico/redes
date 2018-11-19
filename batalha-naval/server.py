# Externo
import json
import random
import socket
import struct
import threading

# Local
import common
import util
    
def random_orientation():
    """ Retorna a orientação do navio a ser inserido. 

    @return tupla informando a orientação (1, 0) ou (0, 1).
    """
    
    horizontal = random.randint(0, 1)
    return (horizontal, 1 - horizontal)


def place_random_ship(board, ship, orientation):
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
            board[r][c] = ship['symbol']
            
            
def random_board(ships, num_ships, board_size):
    """ Cria um novo tabuleiro, posicionando os navios
    de forma randômica.
    
    @param ships tipos de navios
    @param num_ships quantidade de navios
    @param board_size tamanho do tabuleiro

    @return matriz representando o tabuleiro.
    """
    
    board = [['-'] * board_size for i in range(board_size)]

    # Posiciona Porta-Avião.
    place_random_ship(board, ships['P'], random_orientation())

    # Posiciona Navios-Tanque.
    place_random_ship(board, ships['T'], random_orientation())
    place_random_ship(board, ships['T'], random_orientation())

    # Posiciona Contratorpedeiros.
    place_random_ship(board, ships['C'], random_orientation())
    place_random_ship(board, ships['C'], random_orientation())
    place_random_ship(board, ships['C'], random_orientation())

    # Posiciona submarinos.
    place_random_ship(board, ships['S'], random_orientation())
    place_random_ship(board, ships['S'], random_orientation())
    place_random_ship(board, ships['S'], random_orientation())
    place_random_ship(board, ships['S'], random_orientation())

    return board


def prepare_game(conn):
    """ Realiza todos os preparativos necessários para
    o início de um novo jogo.

    @param conn conexão.
    @param client endereço.
    """

    ships = {
        'P': {'symbol': 'p', 'name': 'Porta Aviões', 'size': 5},
        'T': {'symbol': 't', 'name': 'Navio Tanque', 'size': 4},
        'C': {'symbol': 'c', 'name': 'Contratorpedeiro', 'size': 3},
        'S': {'symbol': 's', 'name': 'Submarino', 'size': 2}
    }

    # Parâmetros do jogo.
    board_size = 10
    num_ships = 10

    # Tabuleiro de jogo referente ao servidor.
    server_board = random_board(ships, num_ships, board_size)

    # Enviando dados iniciais para cliente.
    data = json.dumps(ships).encode()

    conn.send(struct.pack('!I', board_size))
    conn.send(struct.pack('!I', num_ships))
    conn.send(struct.pack('!I', len(data)))
    conn.send(data)

    start_game(conn, server_board, board_size, ships, num_ships)

    
def start_game(conn, server_board, board_size, ships, num_ships):
    # Turno inicial: jogador.
    turn = common.Turn.PLAYER
    winner = None
    
    while not winner:
        while turn == common.Turn.PLAYER:
            length, = struct.unpack('!I', conn.recv(4))
            data = json.loads(conn.recv(length).decode())
            row, col = data.values()

            print('O BRODI ALI TENTOU: {} {}'.format(row, col))
            res = common.make_move(server_board, row, col)
            conn.send(struct.pack('!I', res.value))

            if res != common.MoveStatus.HIT:
                turn = common.Turn.SERVER

        print('AGORA EH O SERVER BEBE')
    
    
def start_server():
    """ Inicializa o servidor e espera por conexões. Quando
    uma conexão é feita, cria uma nova thread específica
    para a nova conexão, dando início a uma nova partida.
    """
    
    host = util.get_address()
    port = int(input('Insira a porta de conexão: '))

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
