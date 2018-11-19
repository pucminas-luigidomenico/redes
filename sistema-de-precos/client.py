# Externo
import json
import socket
import struct

def input_tipo():
    """ Retorna o tipo de mensagem a ser enviada para os servidor (dados
    ou pesquisa).

    @return inteiro representando o tipo, sendo 1 para dados e
    0 para pesquisa.
    """
    
    valid_tip = False
    while not valid_tip:
        try:
            t = input('Insira o tipo de mensagem (Dados: D, Pesquisa: P): ')
            t = t.upper()

            if t not in ['D', 'P']:
                raise Exception()

            valid_tip = True
        except Exception:
            print('Tipo de mensagem inválido!')
            
    return 1 if t == 'D' else 0

def id_menssagem():
    return 0

def input_comb():
    """ Retorna o tipo de combustível(díesel, álcool ou gasolina).

    @return inteiro representando o tipo, sendo 0 para diesel,
    1 para álcool e 2 para gasolina.
    """
    
    valid_comb = False
    while not valid_comb:
        try:
            c = int(input('Insira o tipo de combustível (Díesel: 0, Álcool: 1, Gasolina: 2): '))

            if c not in [0, 1, 2]:
                raise Exception()

            valid_comb = True
        except Exception:
            print('Tipo de combustível inválido!')
            
    return c

def input_preco():
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

def input_raio():
    """ Retorna o raio da pesquisa
    """

    valid_rai = False
    while not valid_rai:
        try:
            r = int(input('Insira o raio da pesquisa: '))
            valid_rai = True
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
    # através do parâmetro AF_INET, bem como o protocolo TCP,
    # através do parâmetro SOCKET_STREAM.
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, port)

    client.sendto(''.encode(), addr)

    # Recebe dados iniciais do sistema.
    # A função <struct.unpack> retorna uma tupla que, nesse caso,
    # contém apenas um elemento.
    while True:
        start_system(client, addr)

    client.close()

def start_system(client, addr):
    tipo = input_tipo()
    id_msg = id_menssagem()
    id_comb = input_comb()

    if tipo == 1:
        preco = input_preco()
        coord = input_coord()

        data = json.dumps({
            'tipo': 'D', 
            'id': id_msg, 
            'comb': id_comb, 
            'preco': preco, 
            'coord': coord 
        }).encode()

        client.sendto(data, addr)
    else:
        raio = input_raio()
        center = input_center()

        data = json.dumps({
            'tipo': 'P', 
            'id': id_msg, 
            'comb': id_comb,
            'raio': raio,
            'center': center 
        }).encode()

        client.sendto(data, addr)

if __name__ == '__main__':
    prepare_system()