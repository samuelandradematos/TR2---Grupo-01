# Monitoramento de Condições Ambientais com LoRa

Parte 1 do Projeto Final da disciplina **CIC0236 - Teleinformática e Redes 2 (2025.2)**.

## 1. Descrição Geral

Este projeto implementa um sistema distribuído para **monitorar condições ambientais** (temperatura, umidade e poeira) em salas de equipamentos da universidade.

O sistema emprega a tecnologia **LoRa** para comunicação de baixo consumo e longo alcance entre os nós sensores e um gateway central. O gateway, por sua vez, atua como uma ponte, encaminhando os dados recebidos para um servidor backend através da rede IP (via **UDP**).

O servidor, desenvolvido inteiramente em **Python com bibliotecas padrão** (`socket`, `http.server`, `threading`, `sqlite3`, `queue`), armazena, processa e disponibiliza os dados para um dashboard web que exibe as informações em tempo real e permite a consulta de históricos.

## 2. Funcionalidades

* **Coleta de Dados:** Os nós sensores (hardware) coletam dados de temperatura, umidade e poeira.
* **Comunicação em Camadas:**
    * **Física/Enlace:** Nós Sensores → Gateway via **LoRa**.
    * **Rede/Transporte:** Gateway → Servidor via **UDP/IP**.
    * **Aplicação:** Servidor ↔ Dashboard via **HTTP** e **JSON**.
* **Backend Robusto:** O servidor utiliza *threading* para lidar com recepção UDP, persistência em banco de dados e serviço web simultaneamente.
* **Persistência:** Os dados são armazenados de forma assíncrona em um banco de dados **SQLite**.
* **Dashboard Interativo:** Uma interface web simples (HTML/CSS/JS) que exibe:
    * Dados em tempo real (com atualização automática).
    * Histórico dos últimos 200 registros (carregados sob demanda).

## 3. Arquitetura do Sistema

A arquitetura do sistema é dividida em três camadas lógicas principais, conforme o diagrama

### Fluxo de Dados

1.  **Nós Sensores (Hardware):** Um microcontrolador (ESP32) lê os dados dos sensores (SHT40, DSM501A).
2.  **Transmissão LoRa (Enlace):** O ESP32 envia os dados brutos usando um módulo LoRa (SX1278).
3.  **Gateway (Rede/Transporte):** Um segundo ESP32 (atuando como Gateway) recebe o pacote LoRa. Ele se conecta à rede Wi-Fi/IP da universidade e encaminha os dados.
4.  **Encapsulamento UDP:** O Gateway formata os dados em um payload **JSON** e os envia como um datagrama **UDP** para o IP e porta do Servidor Backend.
5.  **Servidor Backend (Aplicação):**
    * **Thread 1 (Receptor UDP):** O script `udp_server.py`, rodando em uma thread, escuta na porta 9001 usando um `socket`. Ao receber um pacote, ele decodifica o JSON.
    * **Desacoplamento (Fila):** O dado recebido é colocado em uma `queue.Queue` (`state.py`) para processamento assíncrono. Isso evita que o receptor UDP bloqueie.
    * **Thread 2 (Persistência):** O `worker_persistencia` (outra thread) consome da fila e salva os dados no banco de dados `sqlite3` (`storage.py`).
    * **Thread 3 (Servidor Web):** O `http_dashboard.py` (rodando na thread principal) usa `http.server` para servir a interface web e os endpoints de API.
6.  **Dashboard (Aplicação/Usuário):**
    * O navegador do usuário acessa `http://localhost:8000`.
    * O `script.js` faz chamadas `fetch` periódicas para `/last` (que lê o último estado da memória) para atualizar a tabela de tempo real.
    * Ao clicar no botão, o `script.js` faz um `fetch` para `/all` (que consulta o banco de dados) para preencher o histórico.

## 4. Tecnologias Utilizadas

### Hardware (Implementação Real)

* **Microcontrolador:** 2x ESP32-S3R8
* **Comunicação LoRa:** 2x LoRa SX1278
* **Sensores:**
    * SHT40/41 (Temperatura e Umidade) - via I2C
    * DSM501A (Poeira) - via PWM

### Software e Protocolos

* **Backend:** Python 3 (sem frameworks externos)
* **Bibliotecas Padrão (Python):**
    * `socket`: Para o servidor UDP.
    * `http.server`: Para o servidor web e API.
    * `sqlite3`: Para o banco de dados.
    * `threading`: Para concorrência (UDP, Web, DB worker).
    * `queue`: Para desacoplamento entre threads.
    * `json`, `logging`, `time`, `os`
* **Frontend:** HTML5, CSS3, JavaScript (ES6+ com `fetch` e `async/await`)
* **Protocolos:** LoRa, UDP, IP, HTTP
* **Formato de Dados:** JSON

## 5. Como Executar o Protótipo (Simulado)

Este repositório contém o **Servidor Backend** e um **Simulador de Gateway** em Python, permitindo testar toda a camada de Aplicação e Transporte sem o hardware real.

### Pré-requisitos

* Python 3.7 ou superior.

### 1. Iniciar o Servidor Backend

Em um terminal, execute o módulo `app_run` de dentro da pasta `servidor_backend`. Isso iniciará todos os serviços:

```bash
# A partir da raiz do projeto
python3 -m servidor_backend.app_run
```

### 2. Iniciar o Simulador do Gateway

Em um outro terminal, execute o script do gateway simulado:

```bash
# A partir da raiz do projeto
python3 gateway_lora/gateway_udp_sim.py
```

Este script começará a enviar pacotes UDP (dados falsos de "Sala: Servidor") para o seu servidor a cada 5 segundos. Você verá os logs de "Enviado" no terminal do gateway e "Rx" no terminal do servidor.

### 3. Acessar o Dashboard

Abra seu navegador e acesse:

[http://localhost:8000](http://localhost:8000)

A tabela "Dados em Tempo Real" deve exibir os dados da "Sala: Servidor" e atualizar automaticamente.

Clique em "Mostrar Histórico" para ver os dados sendo persistidos no banco de dados.

## 6. Estrutura de Pastas
```
.
├── gateway_lora/
│   ├── gateway_udp_sim.py   # (SIMULADOR) Envia pacotes UDP falsos
│   ├── payload.py           # Helper para formatar o JSON
│   └── config.py            # Configurações (IP, porta, nome da sala)
│
├── servidor_backend/
│   ├── app_run.py           # Ponto de entrada (inicia as 3 threads)
│   ├── udp_server.py        # Thread 1: Servidor UDP (socket) + Thread 2: Worker (queue)
│   ├── http_dashboard.py    # Thread 3: Servidor HTTP (http.server) e API
│   ├── storage.py           # Lógica de banco de dados (sqlite3)
│   ├── state.py             # Estado em memória (queue, lock, ultimo_valor)
│   ├── schema.sql           # (Referência) DDL da tabela
│   └── database.db          # (Gerado) Arquivo do banco de dados
│
├── dashboard_web/
│   ├── index.html           # Estrutura do dashboard
│   ├── script.js            # Lógica do frontend (fetch, DOM)
│   └── style.css            # Estilização da página
│
└── README.md                # Este arquivo
```

## 7. Autores
- Adriele Evellen Alves de Abreu — 20/2042785
- Fernando Nunes de Freitas — 22/2014661
- Samuel Andrade de Matos — 17/0155943
