import random
import socket
import time

try:
    from gateway_lora.config import UDP_HOST, UDP_PORT
    from gateway_lora.payload import build_payload
except ImportError:
    from config import UDP_HOST, UDP_PORT
    from payload import build_payload

class MockSerial:
    def __init__(self, port='COM6', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        print(f"Mock Serial initialized on {self.port} at {self.baudrate} bps")
        self.seq = 0 # Simulação de sequência

    def readline(self):
        temp = random.uniform(20.0, 32.0)
        umid = random.uniform(30.0, 80.0)
        self.seq += 1
        seq = self.seq
        return f"{temp:.2f}, {umid:.2f}, {seq}".encode('utf-8')

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ser = MockSerial()
    
    sala = "Sala_Servidor"
    
    print(f"Gateway Simulado")
    print(f"Enviando 'Temperatura, Umiddade' a cada 5s")

    try:
        while True:
            linha = ser.readline().decode('utf-8')
            print(f"[RX Serial]: {linha}")
            try:
                temp, umid, seq = linha.split(',')
                pkt = build_payload(sala,float(temp), float(umid), int(seq))
                sock.sendto(pkt, (UDP_HOST, UDP_PORT))
                print(f"Enviado seq={seq} bytes={len(pkt)} para {UDP_HOST}:{UDP_PORT}")
                    
            except ValueError:
                print("[Falha ao converter números")
                
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()