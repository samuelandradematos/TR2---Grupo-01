# servidor_backend/app_run.py
import os, sys, threading
BASE = os.path.dirname(__file__)
if BASE not in sys.path:
    sys.path.append(BASE)

from storage import init_db
from udp_server import servidor_udp, worker_persistencia
from http_dashboard import start_http

def main():
    init_db()
    threading.Thread(target=worker_persistencia, daemon=True).start()
    threading.Thread(target=servidor_udp, daemon=True).start()
    start_http()

if __name__ == "__main__":
    main()
