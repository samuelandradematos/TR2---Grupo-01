# (estado em memória: último valor, fila)

from queue import Queue
from threading import Lock

fila = Queue(maxsize=1000)      # para persistência assíncrona
ultimo = {}                     # último por sala
lock_ultimo = Lock()
