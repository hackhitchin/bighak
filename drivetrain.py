import serial

# Mixer and serial comms
class DriveTrain:
    def __init__(self):
        """Constructor"""
        self.enabled = False
        self.motor_left = 0
        self.motor_right = 0
        self.ser = serial.Serial('/dev/ttyACM0', 9600)

    def mix_tank(self, lx, ly, rx, ry):
        """Mix [-1,1] values for Left and Right X,Y axis"""
        # Worlds simplest mixer, for tank driving only
        # need to send ly and ry direct to motors.
        self.motor_left = ly
        self.motor_right = ry

    def mix_channels_and_send(self, lx, ly, rx, ry):
        """Mix axis and send the motors"""
        # Send left and right axis values to appropriate mixer
        self.mix_tank(lx, ly, rx, ry)
        # Left and Right motor values will 
        # have been updated by above method
        self.send_to_motors()

    def send_to_motors(self):
        """Send motor Left and Right values to arduino"""
        if self.enabled and self.ser:
            self.ser.write("[%f,%f]" % (self.motor_left, self.motor_right))

    def set_neutral(self):
        """Set motors to neutral"""
        self.motor_left = 0
        self.motor_right = 0
        self.send_to_motors()

    def enable_motors(self, enable):
        """Enable or disable motors"""
        self.enabled = enable
        # If now disabled, send neutral to motors
        if not self.enabled:
            self.set_neutral()
