#include <Wire.h>        // include Arduino Wire library
#include "./Ultrasonic.h"  // include Seeed Studio ultrasonic ranger library


// define ultrasonic ranger data pin
#define RANGERPIN 4
#define BUTTONPIN 8
#define LEDPIN 7
#define BUZZERPIN 5

// initialize ultrasonic library
Ultrasonic ultrasonic(RANGERPIN);

void setup() {
  // open serial communication
  Serial.begin(9600);
  pinMode(BUTTONPIN, INPUT);
  pinMode(LEDPIN, OUTPUT);
  pinMode(BUZZERPIN, OUTPUT);
}

// main loop
void loop() {
  char s[5];
  int distance;
  int inches;
  int buttonState;
  // get distance in centimeters
  delay(100);  // wait 250 milliseconds between readings
  distance = ultrasonic.MeasureInCentimeters();
  // get button state
  buttonState = digitalRead(BUTTONPIN);	
  snprintf(s, 5, "%03u%u", distance, buttonState);
  Serial.println(s);
}



