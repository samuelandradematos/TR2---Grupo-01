# Monitoramento de Condições Ambientais com LoRa (Grupo 1)

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

## 🔧 Funcionalidades Adicionadas

* **Monitoramento em Tempo Real:** Atualização a cada 2 segundos.
* **Sistema de Alertas Visuais com Critérios:**
  * 🔴 Temperatura > 26.0°C
  * 🟡 Umidade < 30% ou > 70%
  * 🔘 Poeira > 35 partículas
* **Protocolo em Hexadecimal:** Conversão de valores float em hex para reduzir airtime LoRa e consumo.
* **Modo Dual:** Suporte a hardware real (Serial/USB) ou modo Mock com simulação.

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

## 📂 Estrutura Atualizada do Projeto

```
TR2---GRUPO-01/
├── dashboard_web/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── firmwareReciever/
├── firmwareSender/
│
├── gateway_lora/
│   ├── config.py
│   ├── gateway_serial.py
│   ├── gateway_serial_mock.py
│   └── payload.py
│
├── servidor_backend/
│   ├── app_run.py
│   ├── udp_server.py
│   ├── http_dashboard.py
│   ├── storage.py
│   └── state.py
│
├── diagrama_monitoramento.png
├── README.md
└── requirements.txt
```

## 5. Como Executar (Versão Atualizada)

### Pré-requisitos

```bash
Python 3.7+
pip install pyserial
```

### Iniciar o Backend

```bash
python3 -m servidor_backend.app_run
```

### Executar o Gateway

#### Modo Simulado

```bash
python3 gateway_lora/gateway_serial_mock.py
```

#### Modo Real

```bash
python3 gateway_lora/gateway_serial.py
```

###Acessar o Dashboard

```
http://localhost:8000
```

## 7. Autores

- Adriele Evellen Alves de Abreu — 20/2042785
- Fernando Nunes de Freitas — 22/2014661
- Samuel Andrade de Matos — 17/0155943

Hardware/Firmware:
<br>
Hardware:
<ul>
    <li>2x ESP32-S3R8  </li>
    <li>2x LoRa SX1278 </li>
    <li>1x SHT40/41 - Sensor de temperatura e Umidade - </li>
    <li>1x DSM501A - Sensor de Poeira - </li>
</ul>
Firmware:
<ul>
    <li>SPI (Comunicação do ESP com o LoRa, presente tanto no servo como no mestre)</li>
    <li>I2C (Comunicação do modulo SHT40/41 com o servo)</li>
    <li>PWM (Comunicação do modulo DSM501A com o servo)</li>
    <li>No servo: 
        <ul>
            <li>Separaçao dos dados de cada sensor, e do nivel da bateria, em pacotes para ser enviados pelo LoRa</li>
            <li>Logica de gerenciamento de energia e frequencia de envio</li>
            <li>Monitoramento da bateria</li>
        </ul>
    </li>
    <li>No mestre:
        <ul>
            <li>Logica de categorizaçao para envio ao servidor</li>
            <li>AComunicaçao TCP com o servidor, com uma certa frequencia</li>
            <li>Verificaçao da situaçao do servo a cada <b>delta t</b>, UDP</li>
        </ul>
    </li>
    <li>Comum a ambos(servo e mestre):
        <ul>
            <li>Logica de rede</li>
            <li>Roda Servidor: python3 -m servidor_backend.app_run</li>
            <li>Ennvia dados: python3 gateway_lora/gateway_udp_sim.py</li>
        </ul>
    </li>
</ul>


