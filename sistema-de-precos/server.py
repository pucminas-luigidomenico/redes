#Externo
import json
import socket
import struct
import sys

# Local
import util

def prepare_system(server, arquivo):
    msg, client = server.recvfrom(1024)
    j_msg = json.loads(msg.decode())

    server.sendto(str(j_msg['id']).encode(), client)

    print('Mensagem {} recebida'.format(str(j_msg['id'])))

    if j_msg['type'] == 'D':

        json.dump({
            'fuel': j_msg['fuel'], 
            'price': j_msg['price'], 
            'coord': j_msg['coord']
        }, arquivo)
        arquivo.write('\n')
        arquivo.flush()
    
    else:
        arquivo.seek(0)
        data = arquivo.readlines() #json.load(arquivo)
        
        menor = sys.maxsize

        for i in range(len(data)):
            station = json.loads(data[i])
            
            if util.haversine(station['coord'], j_msg['center'], j_msg['radius']) \
            and station['fuel'] == j_msg['fuel'] \
            and station['price'] < menor:
                menor = station ['price']

        server.sendto(str(menor).encode(), client)

def start_server():
    """ Inicializa o servidor e espera por conexões. Quando
    uma conexão é feita, cria uma nova thread específica
    para a nova conexão, dando início a uma nova partida.
    """

    host = util.get_address()
    port = int(input('Insira a porta para conexão: '))

    # Cria o socket do servnameor, declarando a família do protocolo
    # através do parâmetro AF_INET, bem como o protocolo UDP,
    # através do parâmetro SOCKET_DGRAM.
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print('Servidor iniciado. Aguardando conexões...')
    print('Host: {}\t Porta: {}'.format(host, port))
    
    arquivo = open('sistema_preco.json','a+') 

    # Inicia a escuta por possíveis conexões
    _, client = server.recvfrom(1024)
    print('{} conectado. Preparando novo sistema...'.format(client[0]))

    while True:
        prepare_system(server, arquivo)

    arquivo.close()
    server.close()

if __name__ == '__main__':
    start_server()