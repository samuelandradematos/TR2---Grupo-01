# (receptor UDP, decodifica e enfileira)

import socket, json, threading, logging
from state import fila, ultimo, lock_ultimo
from storage import init_db, salvar

UDP_PORT = 9001
BUF = 4096

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def worker_persistencia():
    while True:
        doc = fila.get()
        try:
            salvar(doc)
        except Exception as e:
            logging.exception("Erro ao salvar: %s", e)
        finally:
            fila.task_done()

def servidor_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    logging.info(f"UDP ouvindo em 0.0.0.0:{UDP_PORT}")
    while True:
        data, addr = sock.recvfrom(BUF)
        try:
            doc = json.loads(data.decode("utf-8"))
            with lock_ultimo:
                ultimo[doc["sala"]] = doc
            try:
                fila.put_nowait(doc)
            except:
                logging.warning("Fila cheia, descartando medida seq=%s", doc.get("seq"))
            logging.info("Rx %s seq=%s de %s", doc.get("sala"), doc.get("seq"), addr)
        except Exception as e:
            logging.warning("Pacote inválido de %s: %s", addr, e)

def main():
    init_db()
    t = threading.Thread(target=worker_persistencia, daemon=True)
    t.start()
    servidor_udp()

if __name__ == "__main__":
    main()
