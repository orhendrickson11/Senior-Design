int incomingByte = 0; // for incoming serial data
#include <Servo.h>
String message1 = "Done Weave";
const int DIR = 7;
const int STEP = 6;
const int EN = 8;
const int steps = 200; // 200 is 1 rotation
const int step_init = 12;
const int step_back = 10;
//int y=1;
Servo myServo;

void setup() {
  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(EN, OUTPUT);
  myServo.attach(13);

  digitalWrite(DIR, LOW);
  digitalWrite(EN, LOW);

  Serial.begin(9600);
}

void loop() {
 // myServo.write(90);
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
  }

  // Actuate the weaving stepper motor
  if (incomingByte == '1') {
    for(int x = 0; x < steps; x++)
  {
    digitalWrite(STEP, HIGH);
    delay(2);
    digitalWrite(STEP, LOW);
    delay(2);
  }
  delay(1000); // 1 second delay
    Serial.println(message1);
    incomingByte = 0;
  }
  
  // Actuate the Ending Sequence
  if (incomingByte == '2') {

    // Servo to upward position
    myServo.write(90); 
    delay(1000);

  // Move Stepper back a bit
  for(int x = 0; x < step_init; x++) 
  {
    digitalWrite(STEP, HIGH);
    delay(2);
    digitalWrite(STEP, LOW);
    delay(2);
  }
delay(1000);
// Put servo arm down 
   myServo.write(8);
   delay(1000);

// CLick stepper back in place
   for(int x = 0; x < step_back; x++) 
  {
    digitalWrite(DIR, HIGH);
    digitalWrite(STEP, HIGH);
    delay(2);
    digitalWrite(STEP, LOW);
    delay(2);
  }

// Tell python to continue
   // Serial.println(message1);
    incomingByte = 0;
    myServo.write(8);
  }


}
