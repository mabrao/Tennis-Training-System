#include <Arduino.h>
#include <Arduino_LSM6DSOX.h> //library for the LSM6DSOX IMU
#include <SPI.h>
#include <WiFiNINA.h>

float Ax, Ay, Az; //accelerometer values
float Gx, Gy, Gz; //gyroscope values

char ssid[] = "Tennis Sensor";        // your network SSID (name)
char pass[] = "conectar";    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                // your network key index number (needed only for WEP)

int status = WL_IDLE_STATUS;
WiFiServer server(80); //create a server at port 80

unsigned long myTime; //this will be used for printing milliseconds

void printWiFiStatus();

void setup() {
  Serial.begin(9600);

  //while(!Serial); //this is only used when connected to serial monitor

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  //checking the firmware
  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // by default the local IP address will be 192.168.4.1
  // you can override it with the following:
  // WiFi.config(IPAddress(10, 0, 0, 1));

  // print the network name (SSID);
  Serial.print("Creating access point named: ");
  Serial.println(ssid);

  // Create open network. Change this line if you want to create an WEP network:
  status = WiFi.beginAP(ssid, pass);
  if (status != WL_AP_LISTENING) {
    Serial.println("Creating access point failed");
    // don't continue
    while (true);
  }

  // wait 10 seconds for connection:
  delay(10000);

  // start the web server on port 80
  server.begin();

  // you're connected now, so print out the status
  printWiFiStatus();


  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println("Hz");
  Serial.println();

  Serial.print("Gyroscope sample rate = ");  
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println("Hz");
  Serial.println();

}

void loop() {

  myTime = millis(); //update time since program started
  
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(Ax, Ay, Az);

    WiFiClient client = server.available();   // listen for incoming clients

    if (client) {
      // read bytes from the incoming client and write them back
      // to any clients connected to the server:
      //Serial.println("Client Connected");
      client.print("Time: ");
      client.print('\t');
      client.print(myTime);
      client.print('\n');
      client.println("Accelerometer data: ");
      client.print(Ax);
      client.print('\t');
      client.print(Ay);
      client.print('\t');
      client.println(Az);
      client.println();
    }
  }

  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(Gx, Gy, Gz);

    WiFiClient client = server.available();   // listen for incoming clients

    if (client) {
      // read bytes from the incoming client and write them back
      // to any clients connected to the server:
      //Serial.println("Client Connected");
      client.print("Time: ");
      client.print('\t');
      client.print(myTime);
      client.print('\n');
      client.println("Gyroscope data: ");
      client.print(Gx);
      client.print('\t');
      client.print(Gy);
      client.print('\t');
      client.println(Gz);
      client.println();
    }
    
  }

  // compare the previous status to the current status
  if (status != WiFi.status()) {
    // it has changed update the variable
    status = WiFi.status();

    if (status == WL_AP_CONNECTED) {
      // a device has connected to the AP
      Serial.println("Device connected to AP");
    } else {
      // a device has disconnected from the AP, and we are back in listening mode
      Serial.println("Device disconnected from AP");
    }
  }

delay(500);
}


void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print where to go in a browser:
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);

}