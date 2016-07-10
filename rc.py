# Import triangula module to interact with SixAxis
from triangula.input import SixAxis, SixAxisResource

class rc:
    def __init__(self):
        """Class Constructor"""
        self.killed = False

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def handler(self, button):
        """Button handler, will be bound to the square button later"""
        print 'Button {} pressed'.format(button)

    def run(self):
        """Start listening to the controller and pass state to drivetrain"""
        # Get a joystick, this will fail unless the SixAxis controller is paired and active
        # The bind_defaults argument specifies that we should bind actions to the SELECT and START buttons to
        # centre the controller and reset the calibration respectively.
        with SixAxisResource(bind_defaults=True) as joystick:
            # Register a button handler for the square button
            joystick.register_button_handler(self.handler, SixAxis.BUTTON_SQUARE)
            # Loop indefinitely
            while not self.killed:
                # Read the x and y axes of the left hand stick
                lx = joystick.axes[0].corrected_value()
                ly = joystick.axes[1].corrected_value()
                # Read the x and y axes of the right hand stick
                rx = joystick.axes[2].corrected_value()
                ry = joystick.axes[3].corrected_value()
                # Show the values to the screen
                print(lx,ly, rx,ry)

if __name__ == "__main__":
    rc = rc()
    try:
        rc.run()
    except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        print("Quitting")
