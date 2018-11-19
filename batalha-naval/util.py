import socket
import enum

Turn = enum.Enum('Turn', 'ENEMY PLAYER')
MoveStatus = enum.Enum('MoveStatus', 'HIT MISS')

MoveResult = {
    MoveStatus.HIT: 'Acerto',
    MoveStatus.MISS: 'Erro',
}

Winner = enum.Enum('Winner', 'NONE SERVER PLAYER')

def get_address():
    """ Retorna o endereço IP local da máquina . """

    try:
        address = socket.gethostbyname(socket.gethostname())
    except:
        address = None
    finally:
        # Caso ocorra uma exceção, ou o endereço retornado seja
        # seja o endereço de loopback (127.x.x.x), conectar a
        # uma rede externa para que se utilize a interface correta.
        if not address or address.startswith("127."):
            host = "8.8.8.8"
            port = 80
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((host, port))

            address = sock.getsockname()[0]

            sock.close()

        return address
