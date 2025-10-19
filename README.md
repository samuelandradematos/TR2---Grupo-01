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
        </ul>
    </li>
</ul>