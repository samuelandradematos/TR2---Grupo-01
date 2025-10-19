<<<<<<< HEAD
# TR2---Grupo-01
=======
# TR2---Grupo-01
>>>>>>> cca3018 (Adiciona pasta venv ao gitignore)
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
    <li>No servo: Lógica de rede e transporte, i.e. tamanho dos pacotes e sockets/portas, para ser enviado via LoRa os dados coletados pelos modulos para o mestre</li>
</ul>