import socket
from math import radians, cos, sin, asin, sqrt

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

def haversine(coord, center, radius):
    """
    Calula se uma latitude/longitude está dentro de uma área circular
    com latitude/longitude conhecidos (especificado em graus decimais)
    """
    lat1 = coord[0]
    lon1 = coord[1]
    lat2 = center[0]
    lon2 = center[1]

    # Converte graus decimais em radianos
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Fórmula haversine 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # 6371 Raio da terra em kilometros. Use 3956 para milhas
    return True if (c * r) > radius else False