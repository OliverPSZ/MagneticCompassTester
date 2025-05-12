#include <Wire.h>
#include <MechaQMC5883.h>

MechaQMC5883 qmc;

void setup() {
  Wire.begin();
  qmc.init();
  Serial.begin(9600);
}

void loop() {
  int x,y,z,a;
  qmc.read(&x,&y,&z, &a);

  Serial.print("x: ");
  Serial.print(x);
  Serial.print(" y: ");
  Serial.print(y);
  Serial.print(" z: ");
  Serial.print(z);
  Serial.print(" heading: ");
  Serial.print(a);
  Serial.println();
  delay(100);
}
