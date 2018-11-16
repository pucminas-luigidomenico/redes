# Externo
import json
import socket
import struct

def print_game(num_ships, show_board, enemy_board, player_board):
    """ Mostra na tela o estado atual do jogo. """
    column = 'A'

    print('\nTabuleiro Inimigo\t\t\tMeu Tabuleiro')

    # Imprime os tabuleiros do inimigo e do jogador
    rows = [i for i in range(1, num_ships)]
    print(' {}\t\t {}'.format(rows, rows))
    
    for (enemy_row, player_row) in zip(show_board, player_board):
        print(column + ' ' + '  '.join(enemy_row) + '\t\t' +
              column + ' ' + '  '.join(player_row))
        column = chr(ord(column) + 1)

    # Imprime a quantidade de navios afundados
    print('O inimigo tem {} afundado(s)'.format(sink_ships(enemy_board)))
    print('Você tem {} afundado(s)\n'.format(sink_ships(player_board)))
    

def sink_ships(board):
    """ Retorna a quantidade de navios afundados. """

    return 0


def start_game():
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
    data = json.loads(client.recv(length).decode())

    show_board = data['show_board']
    player_board = data['player_board']
    enemy_board = data['enemy_board']

    print_game(num_ships, show_board, enemy_board, player_board)
    
    client.close()


if __name__ == '__main__':
    start_game()
