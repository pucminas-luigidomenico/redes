# Externo
import json
import socket
import struct
import select

def input_type():
    """ Retorna o tipo de mensagem a ser enviada para os servidor (dados
    ou pesquisa).

    @return inteiro representando o tipo, sendo 1 para dados e
    0 para pesquisa.
    """
    
    valid_type = False
    while not valid_type:
        try:
            t = input('\nInsira o tipo de mensagem (Dados: D, Pesquisa: P): ')
            t = t.upper()

            if t not in ['D', 'P']:
                raise Exception()

            valid_type = True
        except Exception:
            print('Tipo de mensagem inválido!')
            
    return t

def input_fuel():
    """ Retorna o tipo de combustível(díesel, álcool ou gasolina).

    @return inteiro representando o tipo, sendo 0 para diesel,
    1 para álcool e 2 para gasolina.
    """
    
    valid_fuel = False
    while not valid_fuel:
        try:
            c = int(input('Insira o tipo de combustível (Díesel: 0, Álcool: 1, Gasolina: 2): '))

            if c not in [0, 1, 2]:
                raise Exception()

            valid_fuel = True
        except Exception:
            print('Tipo de combustível inválido!')
            
    return c

def input_price():
    """ Retorna o preço do combustível
    """

    valid_prc = False
    while not valid_prc:
        try:
            p = int(input('Insira o preço do combustível: '))
            valid_prc = True
        except Exception:
            print('Preço inválido!')

    return p

def input_radius():
    """ Retorna o raio da pesquisa
    """

    valid_radius = False
    while not valid_radius:
        try:
            r = int(input('Insira o raio da pesquisa: '))
            valid_radius = True
        except Exception:
            print('Raio inválido!')

    return r

def input_center():
    """ Retorna a coordenada do centro da pesquisa
    """

    valid_cen = False
    while not valid_cen:
        try:
            lat = int(input('Insira a latitude do centro da pesquisa: '))
            lng = int(input('Insira a longtude do centro da pesquisa: '))
            valid_cen = True
        except Exception:
            print('Coordenada inválida!')

    return lat, lng

def input_coord():
    """ Retorna a coordenada do posto de gasolina
    """

    valid_cen = False
    while not valid_cen:
        try:
            lat = int(input('Insira a latitude do posto de gasolina: '))
            lng = int(input('Insira a longtude do posto de gasolina: '))
            valid_cen = True
        except Exception:
            print('Coordenada inválida!')

    return lat, lng

def prepare_system():
    """ Inicializa conexão com o servidor, para o sistema. """
    
    print('{} Sistema de Preços {}\n'.format('=' * 30, '=' * 30))
    host = input('Insira o IP do servidor: ')
    port = int(input('Insira a porta para conexão: '))

    # Cria o socket do servnameor, declarando a família do protocolo
    # através do parâmetro AF_INET, bem como o protocolo UDP,
    # através do parâmetro SOCKET_STREAM.
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, port)

    client.sendto(''.encode(), addr)

    # Recebe dados iniciais do sistema.
    # A função <struct.unpack> retorna uma tupla que, nesse caso,
    # contém apenas um elemento.
    id_msg = 0
    while True:
        start_system(id_msg, client, addr)
        id_msg += 1

    client.close()

def start_system(id_msg, client, addr):
    data = ''
    type_msg = input_type()
    id_fuel = input_fuel()

    if type_msg == 'D':
        price = input_price()
        coord = input_coord()

        data = json.dumps({
            'type': 'D', 
            'id': id_msg, 
            'fuel': id_fuel, 
            'price': price, 
            'coord': coord 
        }).encode()
    
        client.sendto(data, addr)

        try:
            client.settimeout(5.0)
            msg, _ = client.recvfrom(1024)
            print('Confirmado: {}'.format(msg.decode()))

        except Exception as ex:
            print('Retransmissão...')
            client.sendto(data, addr)

    else:
        radius = input_radius()
        center = input_center()

        data = json.dumps({
            'type': 'P', 
            'id': id_msg, 
            'fuel': id_fuel,
            'radius': radius,
            'center': center 
        }).encode()

        client.sendto(data, addr)

        try:
            client.settimeout(5.0)
            msg, _ = client.recvfrom(1024)
            print('\nConfirmado: {}'.format(msg.decode()))

        except Exception as ex:
            print('\nRetransmissão...')
            client.sendto(data, addr)

        msg, _ = client.recvfrom(1024)
        print('\nMenor Valor: {}'.format(msg.decode()))

if __name__ == '__main__':
    prepare_system()