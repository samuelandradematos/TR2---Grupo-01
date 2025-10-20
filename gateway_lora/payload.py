# (serialização/validação do JSON)

import json, time

def build_payload(sala: str, seq: int, temperatura: float, umidade: float, poeira: int) -> bytes:
    doc = {
        "sala": sala,
        "timestamp": int(time.time()),
        "temperatura": round(float(temperatura), 2),
        "umidade": round(float(umidade), 2),
        "poeira": int(poeira),
        "seq": int(seq),
    }
    return json.dumps(doc, separators=(",", ":")).encode("utf-8")
