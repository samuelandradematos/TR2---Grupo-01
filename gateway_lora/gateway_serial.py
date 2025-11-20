import socket
import sys
import time

# Requer: pip install pyserial
import serial

try:
    from gateway_lora.config import SALA, UDP_HOST, UDP_PORT
    from gateway_lora.payload import build_payload
except ImportError:
    from config import SALA, UDP_HOST, UDP_PORT
    from payload import build_payload

SERIAL_PORT = "COM3"
BAUD_RATE = 115200


def dht11_hex_to_float(hex_str):
    """Lógica de conversão do DHT11 (Ex: '2D05' -> 45.5)"""
    if len(hex_str) != 4: return 0.0
    try:
        inteiro = int(hex_str[0:2], 16)
        decimal = int(hex_str[2:4], 16)
        return inteiro + (decimal / 10.0)
    except:
        return 0.0

def poeira_hex_to_int(hex_str):
    """Converte Hex da Poeira para Int (Ex: '14' -> 20)"""
    try:
        return int(hex_str, 16)
    except:
        return 0


def main():
    print(f"--- Iniciando Gateway Serial REAL na porta {SERIAL_PORT} ---")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) 
    except Exception as e:
        print(f"Erro ao abrir serial: {e}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq_local = 0

    try:
        while True:
            if 'ser' in locals() and ser.in_waiting > 0:
                try:
                    linha = ser.readline().decode('utf-8', errors='ignore').strip()
                except:
                    continue
                
                if not linha: continue

                print(f"[RX Hardware]: {linha}")

                try:
                    dados = linha.split(',')
                    if len(dados) >= 4:
                        sala_lida = dados[0]
                        
                        # 1. Temp (Hex 16-bit)
                        val_t = int(dados[1], 16)
                        if val_t & 0x8000: val_t -= 0x10000
                        temp = val_t * 0.0625
                        
                        # 2. Umidade (Hex DHT11)
                        umid = dht11_hex_to_float(dados[2])
                        
                        # 3. Poeira (Hex 8-bit)
                        poeira = poeira_hex_to_int(dados[3])

                        pkt = build_payload(sala_lida, seq_local, temp, umid, poeira)
                        sock.sendto(pkt, (UDP_HOST, UDP_PORT))
                        print(f" -> Dados enviados. Seq: {seq_local}")
                        
                        seq_local = (seq_local + 1) & 0x7fffffff
                except Exception as e:
                    print(f" -> Erro parse: {e}")

    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        if 'ser' in locals(): ser.close()
        sock.close()

if __name__ == "__main__":
    main()