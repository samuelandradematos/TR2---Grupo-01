import socket

import serial  # pip install pyserial

from gateway_lora.config import UDP_HOST, UDP_PORT
from gateway_lora.payload import build_payload

PORTA = "COM3" 
BAUD = 115200

def main():
    ser = serial.Serial(PORTA, BAUD)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    print("Gateway Rodando (dados reais)...")

    while True:
        if ser.in_waiting:
            try:
                linha = ser.readline().decode().strip()
                print(f"Lido: {linha}")
                partes = linha.split(',')             
                if len(partes) >= 2:
                    temp = float(partes[0])
                    umid = float(partes[1])

                    pkt = build_payload("Sala_Servidor", seq, temp, umid, 0)
                    sock.sendto(pkt, (UDP_HOST, UDP_PORT))
                    print(f"Enviado UDP (Seq: {seq})")
                    seq += 1
            except Exception:
                pass

if __name__ == "__main__":
    main()