#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <DHTesp.h>

#define LORA_SCK 12
#define LORA_MISO 13
#define LORA_MOSI 11
#define LORA_CS 10
#define LORA_RST 9
#define LORA_DIO0 14
#define DHT_PIN 46
#define DHT_TYPE DHT11

DHTesp dht;

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
    dht.setup(46, DHTesp::DHT11);
    Serial.println("Transmissor LoRa pronto!");
}

int timeESP = 0;
void loop() {
    String msg = "";
    delay(dht.getMinimumSamplingPeriod()); // Espera o tempo minimo entre leituras
    timeESP++;
    float humidity = dht.getHumidity();
    float temperature = dht.getTemperature();
    if (String(humidity) != "nan" && String(temperature) != "nan") {
        Serial.println(timeESP);
        if (timeESP >= 2){ // 10800 para eficiencia energetica (3 horas)
            msg = String(temperature) + "," + String(humidity);
            LoRa.beginPacket();
            LoRa.print(msg);
            LoRa.endPacket();
            timeESP = 0;
        }
    }
    Serial.println(msg);
}