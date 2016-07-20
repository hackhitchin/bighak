#define SERIAL_BOARD_RATE 57600

#define MOTOR_NEUTRAL 2.5
// Millisecond timeout. If timeout reached, neutral is automatically kicked in.
#define SAFETY_TIMEOUT 1000

#define LEFT_MOTOR 0
#define RIGHT_MOTOR 1

// Pin possibilities [PWM: 3, 5, 6, 9, 10, and 11]
// WARNING: pins 5 and 6 share internal timer with 
// millis() and delay() functions so aren't a great choice.
#define LEFT_MOTOR_PIN 9
#define RIGHT_MOTOR_PIN 10
#define LEFT_REVERSE_PIN 8
#define RIGHT_REVERSE_PIN 11

#define MAX_PARAMS 3
#define SPEED_MIN -1.0
#define SPEED_MAX 1.0
#define VOLT_MIN -5.0
#define VOLT_MAX 5.0

#define LED 13

bool m_bDebugMessages = false;
String m_szString;
double m_dMotors_Current_V[2] = {MOTOR_NEUTRAL, MOTOR_NEUTRAL};
double m_dMotors_Target_V[2] = {MOTOR_NEUTRAL, MOTOR_NEUTRAL};
int m_nLastMilli = 0;
int m_nLastMilliSerial = 0;
double m_dVPerMilliSec = 0.0;

void setup()
{
  // Configure USB serial
  Serial.begin(SERIAL_BOARD_RATE, SERIAL_8N1);

  // Setup LED flash pin
  pinMode(LED, OUTPUT);

  pinMode(LEFT_MOTOR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_PIN, OUTPUT);
  pinMode(LEFT_REVERSE_PIN, OUTPUT);
  pinMode(RIGHT_REVERSE_PIN, OUTPUT);

  // Calculate acceleration based on number of seconds from zero to full throttle.
  calculate_acceleration(1.0);
}

void calculate_acceleration(float fSeconds)
{
  // Calculate acceleration based on number of seconds from zero to full throttle.
  // [ratio of volts per second]
  double dRangeV = (VOLT_MAX - VOLT_MIN) / 2.0; // Half range as want from zero speed to full in a set time.
  m_dVPerMilliSec = dRangeV / (fSeconds*1000.0);
}

double speed_to_v(double dSpeed)
{
  // Convert range [-1,1] to [0,5]
  double dV = MOTOR_NEUTRAL;
  double dRangeSpeed = SPEED_MAX - SPEED_MIN;
  double dRangeV = VOLT_MAX - VOLT_MIN;
  double dDistanceSpeed = dSpeed - SPEED_MIN;
  double dRatio = dDistanceSpeed / dRangeSpeed;
  dV = VOLT_MIN + (dRangeV * dRatio);

  // Ensure result is within [VOLT_MIN,VOLT_MAX]
  if (dV < VOLT_MIN)
    dV = VOLT_MIN;
  if (dV > VOLT_MAX)
    dV = VOLT_MAX;
    
  return dV;
}

int v_to_byte(double dV, bool &bInReverse)
{
  // Convert range [0,5] to [0,255]
  double dRangeByte = 255 - 0;
  double dRangeV = (VOLT_MAX - VOLT_MIN) / 2.0; // half range as byte value should be [0,5] not [-5,5] and if V negative then set REVERSE flag true.
  double dDistanceV = fabs(dV) - (VOLT_MIN + dRangeV);
  double dRatio = dDistanceV / dRangeV;
  int nByte = 0 + (int)(dRangeByte * dRatio);

  // Ensure result is within [0,255]
  if (nByte < 0)
    nByte = 0;
  if (nByte > 255)
    nByte = 255;
    
  Serial.println(nByte);

  bInReverse = (dV<0.0? true:false);
  return nByte;
}

void set_motor_target_speed(int nMotor, double dSpeed)
{
  // Ensure speed is within [-1,1]
  if (dSpeed < SPEED_MIN)
    dSpeed = SPEED_MIN;
  if (dSpeed > SPEED_MAX)
    dSpeed = SPEED_MAX;
    
  // nMotor is index (L/R) and the speed is in range [-1,1]
  m_dMotors_Target_V[nMotor] = speed_to_v(dSpeed);
}

void blink_LED(int nTimes)
{
  // Blink LED a set number of times.
  for (int i=0; i<nTimes; i++)
  {
    digitalWrite(LED, HIGH);
    delay(500);    
    digitalWrite(LED, LOW);
    delay(500);
  }
}

void parse_command()
{
  // Parse the command just read in and enact on it.

  // Parse command type from string
  int nParam = 0;
  String szParams[MAX_PARAMS];
  bool bReading = false;
  int nStrLength = m_szString.length();
  for (int i=0; i<nStrLength; i++)
  {
    char chChar = m_szString[i];
    if (chChar == '[')
      bReading = true; // Found start of command string
    else if (chChar == ',')
      nParam++; // Comma means we move to next parameter index.
    else if (chChar == ']' || chChar == '\0')
      i=nStrLength; // Stop parsing string
    else if (bReading)
      szParams[nParam] += chChar;
  }
  // Convert found string to command index
  int nCommand = 0;
  if (szParams[0].length())
    nCommand = szParams[0].toInt();
  else
    nCommand = -1; // If no command read, set to -1 so we know its not a valid command

  // Blink LED to count command index
  //blink_LED(nCommand);
  
  // Based on command type, read command parameters
  switch(nCommand)
  {
    // CHANGE MOTOR SPEED
    case 1:
    {
      // Blink when command recognised
      //blink_LED(nParam+1);
      
      if (nParam == 2) // NOTE, nParam is zero based index so 2 == 3 parameters.
      {
        // Pull left and right motor speeds from command string.
        float fLeftMotor = MOTOR_NEUTRAL, fRightMotor = MOTOR_NEUTRAL;
        if (szParams[1].length()) // Only convert to float if string has a length.
          fLeftMotor = szParams[1].toFloat();
        if (szParams[2].length()) // Only convert to float if string has a length.
          fRightMotor = szParams[2].toFloat();

        // Set new TARGET speed. Note, doesn't actually set motor voltages here.
        set_motor_target_speed(LEFT_MOTOR, fLeftMotor);
        set_motor_target_speed(RIGHT_MOTOR, fRightMotor);
      }
    }break;
  }
}

void read_command()
{
  // Read serial comms if available
  bool bReadCMDEnd = false;
  while (Serial.available()>0)
  {
    // Blink for each character read
    //blink_LED(1);

    char chChar = Serial.read();
    m_szString += chChar;

    if (chChar == ']')
      bReadCMDEnd = true;
  }
  
  // If we have read a command, attempt to parse out the details
  if (bReadCMDEnd)
  {
    // Blink when end of command read
    //blink_LED(1);
    
    parse_command();
    m_szString = ""; // clear out string
    // Store time when we last recieved a command over serial comms.
    m_nLastMilliSerial = millis();
  }
}

void loop()
{
  // Read serial comms if available
  read_command();

  // First time ever into this loop.
  // Ensure millis is time NOW.
  int nMillis = millis();
  if (m_nLastMilli == 0)
    m_nLastMilli = nMillis;

  // Safety cutout timer
  int nSerialDiff = nMillis-m_nLastMilliSerial;
  if (nSerialDiff>SAFETY_TIMEOUT)
  {
    // Serial comms last sentrecognised message over a second ago, can't 
    // be sure comms have failed so set motors into neutral.
    m_dMotors_Target_V[LEFT_MOTOR] = MOTOR_NEUTRAL;
    m_dMotors_Target_V[RIGHT_MOTOR] = MOTOR_NEUTRAL;

    // Turn on LED when in safety cutout mode
    digitalWrite(LED, HIGH);
  }
  else
    digitalWrite(LED, LOW);

  // Loop motors [L/R] and update current voltage value based on acceleration ramps.
  int nMilliDiff = nMillis-m_nLastMilli;
  if (nMilliDiff>0)
  {
    int nMotor = 0;
    int nMotors = 2;
    for (nMotor = 0; nMotor < nMotors; nMotor++)
    {
      // Calculate difference from current value and target value.
      double dDiff = m_dMotors_Target_V[nMotor] - m_dMotors_Current_V[nMotor];
      if (fabs(dDiff) > 0.001)
      {
        double dVIncrease = m_dVPerMilliSec * ((double)nMilliDiff);
        if (dDiff<0.0)
          dVIncrease = -dVIncrease; // Invert difference to decelerate
        m_dMotors_Current_V[nMotor] += dVIncrease;

        // Ensure voltage is capped to min/max
        if (m_dMotors_Current_V[nMotor]<VOLT_MIN)
          m_dMotors_Current_V[nMotor] = VOLT_MIN;
        if (m_dMotors_Current_V[nMotor]>VOLT_MAX)
          m_dMotors_Current_V[nMotor] = VOLT_MAX;
      }
    }
  }

  // Send signal voltage to Motors in PWM range of [0,255]
  bool bLeftReverse=false, bRightReverse=false;
  analogWrite(LEFT_MOTOR_PIN, v_to_byte(m_dMotors_Current_V[LEFT_MOTOR], bLeftReverse));
  analogWrite(RIGHT_MOTOR_PIN, v_to_byte(m_dMotors_Current_V[RIGHT_MOTOR], bRightReverse));
  // Update reverse pins 1:0 values
  digitalWrite(LEFT_REVERSE_PIN, bLeftReverse? HIGH:LOW);
  digitalWrite(RIGHT_REVERSE_PIN, bRightReverse? HIGH:LOW);


  // Blink once each time round loop for status.
  //blink_LED(1);
    
  // Must always update nLastMilli!
  m_nLastMilli = nMillis;
}

