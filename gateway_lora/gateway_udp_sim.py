# (gera dados simulados e envia por UDP)

import socket, random, time
from config import UDP_HOST, UDP_PORT, PERIODO_S, SALA
from payload import build_payload

def amostra_fake():
    return (
        random.uniform(20, 30),   # temperatura
        random.uniform(40, 70),   # umidade
        random.randint(5, 30)     # poeira
    )

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    try:
        while True:
            temp, umid, poeira = amostra_fake()
            pkt = build_payload(SALA, seq, temp, umid, poeira)
            sock.sendto(pkt, (UDP_HOST, UDP_PORT))
            print(f"Enviado seq={seq} bytes={len(pkt)} para {UDP_HOST}:{UDP_PORT}")
            seq = (seq + 1) & 0x7fffffff
            time.sleep(PERIODO_S)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    main()
