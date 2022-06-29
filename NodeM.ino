#include <ESP8266WiFi.h>
#include <EEPROM.h>

#define EEPROM_SIZE 2


const char* ssid = "******";
const char* password = "********";
 
int ledPin = D0;
bool ledPinEEPROM = LOW;
int value = LOW;

IPAddress local_IP(192, 168, 0, 5);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8); 
IPAddress secondaryDNS(8, 8, 4, 4);
WiFiServer server(80);

  
void setup() {
  Serial.begin(115200);
  delay(10);
  EEPROM.begin(EEPROM_SIZE);
  EEPROM.get(0, ledPinEEPROM);
  delay(5);
 
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, ledPinEEPROM);
  value = ledPinEEPROM;
  
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.println(ssid);
  Serial.print("Connecting to ");


  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  }
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
 
  // Start the server
  server.begin();
  Serial.println("Server started");
 
  // Print the IP address
  Serial.print("Use this URL to connect: ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
 
}
 
void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
 
  // Wait until the client sends some data
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  }
 
  // Read the first line of the request
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();
 
  // Match the request
 

  if (request.indexOf("/TERMO=ON") != -1)  {
    digitalWrite(ledPin, LOW);
    value = LOW;
    EEPROM.put(0, value);
    EEPROM.commit();
  }
  if (request.indexOf("/TERMO=OFF") != -1)  {
    digitalWrite(ledPin, HIGH);
    value = HIGH;
    EEPROM.put(0, value);
    EEPROM.commit();
  }
 
// Set ledPin according to the request
//digitalWrite(ledPin, value);
 
  // Return the response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println(""); //  do not forget this one
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");
 
  client.print("Termo esta: ");
 
  if(value == LOW) {
    client.print("Prendido");
  } else {
    client.print("Apagado");
  }
  client.println("<br><br>");
  client.println("<a href=\"/TERMO=ON\"\"><button>On </button></a>");
  client.println("<a href=\"/TERMO=OFF\"\"><button>Off </button></a><br />");  
  client.println("</html>");
 
  delay(1);
  Serial.println("Client disonnected");
  Serial.println("");
 
}
