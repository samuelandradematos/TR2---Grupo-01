#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>

#define LORA_SCK 12
#define LORA_MISO 13
#define LORA_MOSI 11
#define LORA_CS 10
#define LORA_RST 9
#define LORA_DIO0 14

void setup() {
    Serial.begin(115200);
    while(!Serial);

    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI);
    LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);

    if (!LoRa.begin(433E6)) {
        while (true); 
    }
}

void loop() {
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
        while (LoRa.available()) {
            pacote += (char)LoRa.read();
        }
        Serial.println(pacote); 
    }
}