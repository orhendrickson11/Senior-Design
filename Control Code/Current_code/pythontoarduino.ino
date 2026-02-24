int incomingByte = 0; // for incoming serial data
String message = "Hello";

void setup() {
  pinMode(7,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
  }
  if (incomingByte == '1') {
    digitalWrite(7,HIGH);
    delay(1000);
    digitalWrite(7,LOW);
    delay(1000);
    digitalWrite(7,HIGH);
    delay(1000);
    digitalWrite(7,LOW);
    delay(1000);
    digitalWrite(7,HIGH);
    delay(1000);
    digitalWrite(7,LOW);
    Serial.println(message);
  }
  
  
incomingByte = 0;

}
