#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>

#define LORA_SCK 12
#define LORA_MISO 13
#define LORA_MOSI 11
#define LORA_CS 10
#define LORA_RST 9
#define LORA_DIO0 14

#define BAND 433E6 
String NOME_SALA = "Sala_Servidor";

void setup() {
    Serial.begin(115200);
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI);
    LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);

    if (!LoRa.begin(BAND)) {
        Serial.println("Erro LoRa!");
        while (true);
    }
    Serial.println("Sender Iniciado!");
}

// Funções auxiliares para gerar o Hexadecimal
String floatToHex16(float val) {
    int raw = (int)(val / 0.0625);
    char buf[5];
    sprintf(buf, "%04X", raw & 0xFFFF);
    return String(buf);
}

String floatToHexDHT(float val) {
    int i = (int)val;
    int d = (int)((val - i) * 10);
    char buf[5];
    sprintf(buf, "%02X%02X", i & 0xFF, d & 0xFF);
    return String(buf);
}

void loop() {
    float temp = 22.0 + (random(0, 500) / 100.0);
    float umid = 40.0 + (random(0, 400) / 10.0);
    int poeira = random(5, 30);

    // Formata: NOME,TEMP_HEX,UMID_HEX,POEIRA_HEX
    String pacote = NOME_SALA + "," + 
                    floatToHex16(temp) + "," + 
                    floatToHexDHT(umid) + "," + 
                    String(poeira, HEX);
    
    LoRa.beginPacket();
    LoRa.print(pacote);
    LoRa.endPacket();

    Serial.println("Enviado: " + pacote);
    delay(5000);
}