#Externo
import socket
import struct
import json

# Local
import util

def prepare_system(server, arquivo):
    msg, _ = server.recvfrom(1024)
    j_msg = json.loads(msg.decode())
    
    if j_msg['tipo'] == 'D':
        
        data = json.dumps({
            'comb': j_msg['comb'], 
            'preco': j_msg['preco'], 
            'coord': j_msg['coord']
        })

        arquivo.write(data)
        arquivo.write('\n')
        arquivo.flush()
    
    else:
        #data = arquivo.read()
        print('Teste')

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
    
    arquivo = open('sistema_preco.txt','a+') 

    # Inicia a escuta por possíveis conexões
    _, client = server.recvfrom(1024)
    print('{} conectado. Preparando novo sistema...'.format(client[0]))

    while True:
        prepare_system(server, arquivo)

    arquivo.close()
    server.close()

if __name__ == '__main__':
    start_server()