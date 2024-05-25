#include <Wire.h> 

int ADXL345 = 0x53;
float X_out, Y_out, Z_out;


void configureADXL345() {
  Wire.beginTransmission(ADXL345);
  Wire.write(0x2D); // Power control register
  Wire.write(8);    // Enable measurement
  Wire.endTransmission();
  delay(10);
}

void calibrateADXL345(){
  float numReadings = 1000;
  float ySum = 0;
  Serial.print("Beginning Calibration...");
  Serial.println();
  for (int i = 0; i < numReadings; i++) {
    Serial.print(i);
    Serial.println("");
    Wire.beginTransmission(ADXL345);
    Wire.write(0x32);
    Wire.endTransmission(false);
    Wire.requestFrom(ADXL345, 6, true);
    X_out = (Wire.read() | Wire.read() <<8);
    //X_out = X_out/256;
    Y_out = (Wire.read() | Wire.read() <<8);  
    //Y_out = Y_out/256;
    Z_out = (Wire.read() | Wire.read() <<8);
    //Z_out = Z_out/256;
    ySum += Y_out;
    
  }
  int Y_ave = ySum / numReadings;
  float Y_offset = (256 - Y_ave) / 4;
  Serial.print("X_ave = ");
  Serial.println(Y_ave);
  Serial.print("Z_offset = ");
  Serial.println(Y_offset);


  Wire.beginTransmission(ADXL345);
  Wire.write(0x1F);
  Wire.write(-5);
  Wire.endTransmission();
  delay(5000);

}


void setup() {
  
  Serial.begin(115200);
  Wire.begin();
  //calibrateADXL345();
  configureADXL345(); 
}


void loop() {
  Wire.beginTransmission(ADXL345);
  Wire.write(0x32);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345, 6, true);
  X_out = (Wire.read() | Wire.read() <<8);
  X_out = X_out/256;
  Y_out = (Wire.read() | Wire.read() <<8);  
  Y_out = Y_out/256;
  Z_out = (Wire.read() | Wire.read() <<8);
  Z_out = Z_out/256;

  float time = micros()/1e6;

  Serial.print(time);
  Serial.print(", ");
  Serial.print(X_out, 5);
  Serial.print(", ");
  Serial.print(Y_out, 5);
  Serial.print(", ");
  Serial.println(Z_out, 5);



  delay(10);


}
