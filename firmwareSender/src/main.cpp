#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <DHTesp.h>

#define LORA_SCK 12
#define LORA_MISO 13
#define LORA_MOSI 11
#define LORA_CS 10
#define LORA_RST 9
#define LORA_DIO0 46
#define DHT_PIN 47
#define DHT_TYPE DHT11

DHTesp dht;

// Variáveis RTC para armazenar a última leitura
RTC_DATA_ATTR int rtcBootCount = 0;
RTC_DATA_ATTR float rtcLastTemp = NAN;
RTC_DATA_ATTR float rtcLastHum = NAN;
RTC_DATA_ATTR int sequenceNumber = 0;
RTC_DATA_ATTR float rtcLastTransmissionTime = 0;

const long int SHORT_WAKE_SECS = 3;    // checagem rápida (ex: 10 min)
const long int LONG_SLEEP_SECS = 10;  // sono longo (ex: 3 horas)
const float TEMP_THRESHOLD = 5.0;        // graus Celsius
const float HUM_THRESHOLD = 10.0;        // porcentagem

void goToDeepSleep(long int sleepSeconds) {
    Serial.println("Indo para o modo de sono profundo...");
    Serial.flush();

    LoRa.end();
    SPI.end();

    esp_sleep_enable_timer_wakeup(sleepSeconds * 1000000LL);
    esp_deep_sleep_start();
}

void sendMeasurement(float temperature, float humidity) {
    String msg = "";
    msg = String(temperature, 2) + "," + String(humidity, 2) + "," + String(sequenceNumber++) + "," + String(rtcLastTransmissionTime, 2);
    Serial.println("Enviando mensagem LoRa: " + msg);
    float startTime = millis() / 1000.0;
    LoRa.beginPacket();
    LoRa.print(msg);
    LoRa.endPacket();
    float endTime = millis() / 1000.0;

    rtcLastTransmissionTime = endTime - startTime;
}

void setup() {
    Serial.begin(115200);

    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI);
    LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);

    if (!LoRa.begin(433E6)) {
        Serial.println("Erro ao iniciar LoRa!");
        while (true);
    }
    dht.setup(46, DHTesp::DHT11);
    Serial.println("Transmissor LoRa pronto!");
}

void loop() {
    delay(dht.getMinimumSamplingPeriod()); // Espera o tempo minimo entre leituras
    float humidity = dht.getHumidity();
    float temperature = dht.getTemperature();

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Falha ao ler do sensor DHT!");
        goToDeepSleep(SHORT_WAKE_SECS);
        return;
    }
    
    // Primeira leitura ou valores inválidos armazenados
    if (isnan(rtcLastHum) || isnan(rtcLastTemp)){
        Serial.println("Primeira leitura, enviando dados...");
        rtcLastHum = humidity;
        rtcLastTemp = temperature;
        
        sendMeasurement(temperature, humidity);
        goToDeepSleep(SHORT_WAKE_SECS);
        return;
    }

    float tempDiff = fabs(temperature - rtcLastTemp);
    float humDiff = fabs(humidity - rtcLastHum);


    // Mudança significativa detectada
    if (tempDiff >= TEMP_THRESHOLD || humDiff >= HUM_THRESHOLD) {
        Serial.println("Mudança significativa detectada, enviando dados...");
        rtcLastTemp = temperature;
        rtcLastHum = humidity;
        rtcBootCount = 0;

        sendMeasurement(temperature, humidity);
        goToDeepSleep(LONG_SLEEP_SECS);
        return;
    }

    // Incrementa o contador de boots curtos e envia se atingir o limite
    rtcBootCount++;
    Serial.println("BootCount atual: " + String(rtcBootCount));
    int maxBoots = (int)(LONG_SLEEP_SECS / SHORT_WAKE_SECS);
    if (rtcBootCount >= maxBoots) {
        Serial.println("Limite de boots curtos atingido, enviando dados...");
        rtcLastTemp = temperature;
        rtcLastHum = humidity;
        rtcBootCount = 0;

        sendMeasurement(temperature, humidity);
        goToDeepSleep(LONG_SLEEP_SECS);
        return;
    }

    // Nenhuma mudança significativa, voltar ao sono curto
    goToDeepSleep(SHORT_WAKE_SECS);
    
    
}