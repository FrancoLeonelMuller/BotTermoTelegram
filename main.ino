/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/telegram-control-esp32-esp8266-nodemcu-outputs/

  Project created using Brian Lough's Universal Telegram Bot Library: https://github.com/witnessmenow/Universal-Arduino-Telegram-Bot
  Example based on the Universal Arduino Telegram Bot Library: https://github.com/witnessmenow/Universal-Arduino-Telegram-Bot/blob/master/examples/ESP8266/FlashLED/FlashLED.ino
*/

#ifdef ESP32
#include <WiFi.h>
#else
#include <ESP8266WiFi.h>
#endif
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>   // Universal Telegram Bot Library written by Brian Lough: https://github.com/witnessmenow/Universal-Arduino-Telegram-Bot
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <EEPROM.h>

// Replace with your network credentials
const char* ssid = "****";
const char* password = "****";

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// Initialize Telegram BOT
#define BOTtoken "*****"  // your Bot Token (Get from Botfather)

// Use @myidbot to find out the chat ID of an individual or a group
// Also note that you need to click "start" on a bot before it can
// message you
#define CHAT_ID1 "*****" //User1
#define CHAT_ID2 "*****" //User2

#ifdef ESP8266
X509List cert(TELEGRAM_CERTIFICATE_ROOT);
#endif

WiFiClientSecure client;
UniversalTelegramBot bot(BOTtoken, client);

// Checks for new messages every 1 second.
int botRequestDelay = 1000;
unsigned long lastTimeBotRan;


const int ledPin = D0;
bool ledState = HIGH;
int horaPrende = 0;
int horaApaga = 0;
bool ledStateEEPROM = false;

// Handle what happens when you receive new messages
void handleNewMessages(int numNewMessages, String hourBot) {
  Serial.println("handleNewMessages");
  Serial.println(String(numNewMessages));

  for (int i = 0; i < numNewMessages; i++) {
    // Chat id of the requester
    String chat_id = String(bot.messages[i].chat_id);
    if (chat_id != CHAT_ID1 && chat_id != CHAT_ID2) {
      bot.sendMessage(chat_id, "y vo' quien so'? Toca de aca", "");
      continue;
    }
    Serial.println(chat_id);
    // Print the received message
    String text = bot.messages[i].text;
    Serial.println(text);

    String from_name = bot.messages[i].from_name;

    if (text == "/hola") {
      String welcome = "Hola wachin en que te puedo ayudar, " + from_name + ".\n";
      welcome += "Te voy a pasar una lista de comandos que podes usar.\n\n";
      welcome += "/ON Prende el termotanque \n";
      welcome += "/OFF Apaga el termotanque xd\n";
      welcome += "/status Te digo como esta el termotanque \n";
      welcome += "/hora te digo la hora que tengo\n";
      welcome += "/setHoraON *hora* pasame una hora para prender el termo (en formato 24hs sin :, ej /setHoraON 1506)\n";
      welcome += "/setHoraOFF *hora* pasame una hora para apagar el termo (en formato 24hs sin :, ej /setHoraOFF 2236)\n";
      bot.sendMessage(chat_id, welcome, "");
    }

    if (text == "/ON") {
      bot.sendMessage(chat_id, "El termo se prendio", "");
      ledState = LOW;
      digitalWrite(ledPin, ledState);
      EEPROM.put(10, ledState);
      EEPROM.commit();
      ledStateEEPROM = ledState;
    }

    if (text == "/OFF") {
      bot.sendMessage(chat_id, "El termo se apago", "");
      ledState = HIGH;
      digitalWrite(ledPin, ledState);
      EEPROM.put(10, ledState);
      EEPROM.commit();
      ledStateEEPROM = ledState;
    }

    if (text == "/hora") {
      bot.sendMessage(chat_id, hourBot, "");
    }

    if (text == "/status") {
      


      String statusmsg = "El termo esta ";
      if (digitalRead(ledPin)) {
        statusmsg += "apagado. \n";
      } else {
         statusmsg += "prendido. \n";
      }

      

      statusmsg += "Se prende a las " + (String(horaPrende)).substring(0,2) + ":" + (String(horaPrende)).substring(2,4) + "\n";
      statusmsg += "Se apaga a las " + (String(horaApaga)).substring(0,2) + ":" + (String(horaApaga)).substring(2,4) + "\n";

      bot.sendMessage(chat_id, statusmsg, "");
    }

    if (text.indexOf("/setHoraON") != -1) {
      String horaTomada = text.substring(11);
      String mnjhoraTomada = "Joya pa, prendo el termo a las " + horaTomada.substring(0,2) + ":" + horaTomada.substring(2,4);
      int horaTomadaint = horaTomada.toInt();
      Serial.println(horaTomadaint);

      if (horaTomadaint > 2359 || horaTomadaint < 0) {
        bot.sendMessage(chat_id, "Vo' so' boludo que queres meter cualquier hora o que?", "");
        continue;
      }
      bot.sendMessage(chat_id, mnjhoraTomada, "");
      EEPROM.put(0, horaTomadaint);
      EEPROM.commit();
      horaPrende = horaTomadaint;
    }

    if (text.indexOf("/setHoraOFF") != -1) {
      String horaTomada = text.substring(12);
      String mnjhoraTomada = "Joya pa, apago el termo a las " + horaTomada.substring(0,2) + ":" + horaTomada.substring(2,4);
      int horaTomadaint = horaTomada.toInt();
      Serial.println(horaTomadaint);

      if (horaTomadaint > 2359 || horaTomadaint < 0) {
        bot.sendMessage(chat_id, "Vo' so' boludo que queres meter cualquier hora o que?", "");
        continue;
      }
      bot.sendMessage(chat_id, mnjhoraTomada, "");
      EEPROM.put(5, horaTomadaint);
      EEPROM.commit();
      horaApaga = horaTomadaint;
    }

  }
}

void setup() {
  Serial.begin(115200);
  EEPROM.begin(30);
#ifdef ESP8266
  configTime(0, 0, "pool.ntp.org");      // get UTC time via NTP
  client.setTrustAnchors(&cert); // Add root certificate for api.telegram.org
#endif

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, ledState);

  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
#ifdef ESP32
  client.setCACert(TELEGRAM_CERTIFICATE_ROOT); // Add root certificate for api.telegram.org
#endif
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  // Print ESP32 Local IP Address
  Serial.println(WiFi.localIP());
  

  // Initialize a NTPClient to get time
  timeClient.begin();
  // Set offset time in seconds to adjust for your timezone, for example:
  timeClient.setTimeOffset(-10800);

  EEPROM.get(0, horaPrende);
  EEPROM.get(5, horaApaga);
  EEPROM.get(10, ledStateEEPROM);
  bot.sendMessage("5002341467", "OwO Padre eh despertado", "");
  digitalWrite(ledPin, ledStateEEPROM);
  
}

void loop() {
  timeClient.update();
  int currentHour = timeClient.getHours();
  int currentMinute = timeClient.getMinutes();
  String currentHourBot = "";
  int comparaHoraInt = 0;


  if(currentHour < 10){
    currentHourBot = "0" + String(currentHour);
  }else currentHourBot = String(currentHour);
  if(currentMinute < 10){
    currentHourBot += ":0" + String(currentMinute);
  }else currentHourBot += ":" + String(currentMinute); 

  
  String aux1 = currentHourBot;
  aux1.remove(2,1);
  comparaHoraInt = aux1.toInt();

  Serial.println(currentHourBot);
  Serial.println(comparaHoraInt);
  Serial.println(horaPrende);
  Serial.println(horaApaga);
  
  if(comparaHoraInt == horaPrende){
    digitalWrite(ledPin, LOW);
    Serial.println("entro low");
  }
  if(comparaHoraInt == horaApaga){
    digitalWrite(ledPin, HIGH);
    Serial.println("entro high");
  }

  if (millis() > lastTimeBotRan + botRequestDelay)  {
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);

    while (numNewMessages) {
      Serial.println("got response");
      handleNewMessages(numNewMessages, currentHourBot);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }
    lastTimeBotRan = millis();
  }

  delay(1000);
}
