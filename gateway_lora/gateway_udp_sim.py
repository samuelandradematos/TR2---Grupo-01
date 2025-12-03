# (gera dados simulados e envia por UDP)

import socket, random, time
from config import UDP_HOST, UDP_PORT, PERIODO_S, SALA
from payload import build_payload
import serial

def amostra():
    ser = serial.Serial('COM6', 9600)  # Substitua 'COM3' pela porta correta
    linha = ser.readline().decode('utf-8')
    temp, umid = map(float, linha.strip().split(','))
    return (
        temp,
        umid
    )

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    try:
        while True:
            temp, umid = amostra()
            pkt = build_payload(SALA, seq, temp, umid)
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
