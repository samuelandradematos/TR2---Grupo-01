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
    def readline(self):
        temp = random.uniform(20.0, 32.0)
        umid = random.uniform(30.0, 80.0)
        return f"{temp:.2f}, {umid:.2f}".encode('utf-8')

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ser = MockSerial()
    
    seq = 0
    sala = "Sala_Servidor"
    
    print(f"Gateway Simulado")
    print(f"Enviando 'Temperatura, Umiddade' a cada 5s")

    try:
        while True:
            linha = ser.readline().decode('utf-8')
            print(f"[RX Serial]: {linha}")
            try:
                partes = linha.split(',')
                
                if len(partes) >= 2:
                    temp = float(partes[0])
                    umid = float(partes[1])
                    poeira = 40 if random.random() < 0.2 else 15 # valor simulado da poeira
                    pkt = build_payload(sala, seq, temp, umid, poeira)
                    sock.sendto(pkt, (UDP_HOST, UDP_PORT))
                    print(f"UDP Enviado (Seq: {seq})")
                    seq += 1
                    
            except ValueError:
                print("[Falha ao converter números")
                
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()