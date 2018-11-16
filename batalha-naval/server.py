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


def place_ship(board, ship, orientation):
    """ Posiciona um navio randomicamente no tabuleiro. """

    horizontal, vertical = orientation
    fit = False
    
    while not fit:
        row = random.randint(0, len(board) - 1)
        col = random.randint(0, len(board[0]) - 1)

        for s in range(ship['size']):
            r = row + s * horizontal
            c = col + s * vertical

            # Se já existe algum navio posicionado, ou
            # o navio não cabe.
            fail = (r >= len(board) or
                    c >= len(board[0]) or
                    board[r][c] != '-')

            if fail:
                break
            elif s == ship['size']-1:
                fit = True

    # Se o navio couber na posição dada, ele é posicionado.
    if fit:
        for s in range(ship['size']):
            r = row + s * horizontal
            c = col + s * vertical
            board[r][c] = ship['symbol']
            
            
def random_board(ships, num_ships, board_size):
    """ Cria um novo tabuleiro, posicionando os navios

    de forma randômica.
    @return matriz representando o tabuleiro.
    """
    
    board = [['-'] * board_size for i in range(board_size)]

    # Posiciona Porta-Aviões
    place_ship(board, ships['P'], random_orientation())

    # Posiciona Navios-Tanque
    place_ship(board, ships['T'], random_orientation())
    place_ship(board, ships['T'], random_orientation())

    # Posiciona Contratorpedeiros
    place_ship(board, ships['C'], random_orientation())
    place_ship(board, ships['C'], random_orientation())
    place_ship(board, ships['C'], random_orientation())

    # Posiciona submarinos
    place_ship(board, ships['S'], random_orientation())
    place_ship(board, ships['S'], random_orientation())
    place_ship(board, ships['S'], random_orientation())
    place_ship(board, ships['S'], random_orientation())

    return board


def prepare_game(conn, client):
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

    board_size = 10
    num_ships = 10
    
    show_board = random_board(ships, num_ships, board_size)
    player_board = random_board(ships, num_ships, board_size)
    server_board = random_board(ships, num_ships, board_size)

    data = json.dumps({
        'show_board': show_board,
        'player_board': player_board,
        'enemy_board': server_board
    }).encode()

    # Enviando dados iniciais para cliente.
    conn.send(struct.pack('!I', board_size))
    conn.send(struct.pack('!I', num_ships))
    conn.send(struct.pack('!I', len(data)))
    conn.send(data)
    conn.close()
    

def start_server():
    """ Inicializa o servidor e espera por conexões. Quando
    uma conexão é feita, cria uma nova thread específica
    para a nova conexão, dando início a uma nova partida.
    """
    
    host = util.get_address()
    port = 5000

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
        threading.Thread(target=prepare_game, args=(conn, client)).start()


if __name__ == '__main__':
    start_server()
