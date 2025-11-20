import random
import socket
import sys
import time


class MockSerial:
    def __init__(self, port, baudrate, timeout=1):
        print(f"[MOCK] Simulando Hardware Conectado na porta {port}...")
        self.in_waiting = 0
        self.last_data_time = 0

    def update(self):
        if time.time() - self.last_data_time > 3.0: 
            self.in_waiting = 1
            self.last_data_time = time.time()
        else:
            self.in_waiting = 0

    def readline(self):
        salas = ["Sala_Servidor", "Sala_Bateria"]
        sala = random.choice(salas)
        
        # 1. Temp (20% chance de Crítico)
        if random.random() < 0.2: temp_real = random.uniform(28.0, 35.0)
        else: temp_real = random.uniform(20.0, 24.0)
        temp_hex = float_para_hex_temp_sensor(temp_real)
        
        # 2. Umidade (20% chance de Atenção)
        rng = random.random()
        if rng < 0.1: umid_real = random.uniform(10.0, 25.0)
        elif rng > 0.9: umid_real = random.uniform(75.0, 90.0)
        else: umid_real = random.uniform(40.0, 60.0)
        umid_hex = float_para_hex_dht11(umid_real) 
        
        # 3. Poeira (20% chance de Alta > 35)
        if random.random() < 0.2:
            poeira_int = random.randint(40, 80) # Alta (Sujo)
        else:
            poeira_int = random.randint(5, 25)  # Normal (Limpo)
            
        poeira_hex = int_para_hex_poeira(poeira_int)
        
        linha = f"{sala},{temp_hex},{umid_hex},{poeira_hex}\n"
        return linha.encode('utf-8')

try:
    from gateway_lora.config import UDP_HOST, UDP_PORT
    from gateway_lora.payload import build_payload
except ImportError:
    from config import UDP_HOST, UDP_PORT
    from payload import build_payload


def float_para_hex_temp_sensor(temp_celsius):
    """Simula sensor de Temperatura (Resolução 0.0625) -> Ex: 25.5 -> '0198'"""
    raw_val = int(temp_celsius / 0.0625)
    hex_val = raw_val & 0xFFFF
    return f"{hex_val:04X}"

def float_para_hex_dht11(umidade_perc):
    """Simula sensor DHT11 (Byte Inteiro + Byte Decimal) -> Ex: 45.5 -> '2D05'"""
    inteiro = int(umidade_perc)
    decimal = int((umidade_perc - inteiro) * 10)
    return f"{inteiro:02X}{decimal:02X}"

def int_para_hex_poeira(poeira_qtd):
    """Simula sensor DSM501A (Int -> Hex) -> Ex: 20 -> '14'"""
    return f"{poeira_qtd:02X}"


class MockSerial:
    def __init__(self, port, baudrate, timeout=1):
        print(f"[MOCK] Simulando Hardware Conectado na porta {port}...")
        self.in_waiting = 0
        self.last_data_time = 0

    def update(self):
        # Simula chegada de dados a cada 3 segundos
        if time.time() - self.last_data_time > 3.0: 
            self.in_waiting = 1
            self.last_data_time = time.time()
        else:
            self.in_waiting = 0

    def readline(self):
        salas = ["Sala_Servidor", "Sala_Bateria"]
        sala = random.choice(salas)
        
        if random.random() < 0.2: 
            temp_real = random.uniform(28.0, 35.0) # Crítico
        else:
            temp_real = random.uniform(20.0, 24.0) # Normal
        temp_hex = float_para_hex_temp_sensor(temp_real)
        
        rng_umid = random.random()
        if rng_umid < 0.1: umid_real = random.uniform(10.0, 25.0) # Baixa
        elif rng_umid > 0.9: umid_real = random.uniform(75.0, 90.0) # Alta
        else: umid_real = random.uniform(40.0, 60.0) # Normal
        umid_hex = float_para_hex_dht11(umid_real) 
        
        poeira_int = random.randint(5, 30)
        poeira_hex = int_para_hex_poeira(poeira_int)
        
        # Monta a linha CSV simulada: NOME,HEX_TEMP,HEX_UMID,HEX_POEIRA
        linha = f"{sala},{temp_hex},{umid_hex},{poeira_hex}\n"
        return linha.encode('utf-8')

    def close(self):
        print("[MOCK] Fechado.")

def dht11_hex_to_float(hex_str):
    """Decodifica o Hex do DHT11 (Ex: '2D05' -> 45.5)"""
    if len(hex_str) != 4: return 0.0
    try:
        inteiro = int(hex_str[0:2], 16)
        decimal = int(hex_str[2:4], 16)
        return inteiro + (decimal / 10.0)
    except:
        return 0.0

def poeira_hex_to_int(hex_str):
    """Decodifica Hex da Poeira (Ex: '14' -> 20)"""
    try:
        return int(hex_str, 16)
    except:
        return 0


def main():
    try:
        ser = MockSerial("COM_MOCK", 115200)
    except Exception:
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    
    print("--- Gateway Rodando (Simulação de Protocolo Hex) ---")

    try:
        while True:
            ser.update()
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8').strip()
                if not linha: continue

                print(f"[RX Serial]: {linha}")

                try:
                    dados = linha.split(',')
                    if len(dados) >= 4:
                        sala = dados[0]
                        
                        # 1. Decodifica Temperatura (Hex 16-bit)
                        val_t = int(dados[1], 16)
                        if val_t & 0x8000: val_t -= 0x10000
                        temp = val_t * 0.0625
                        
                        # 2. Decodifica Umidade (Hex DHT11)
                        umid = dht11_hex_to_float(dados[2])
                        
                        # 3. Decodifica Poeira (Hex 8-bit)
                        poeira = poeira_hex_to_int(dados[3])

                        print(f"   -> Decodificado: {temp:.2f}C | {umid:.1f}% | Poeira: {poeira}")

                        pkt = build_payload(sala, seq, temp, umid, poeira)
                        sock.sendto(pkt, (UDP_HOST, UDP_PORT))
                        seq += 1
                except Exception as e:
                    print(f"Erro de Parsing: {e}")
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        sock.close()

if __name__ == "__main__":
    main()