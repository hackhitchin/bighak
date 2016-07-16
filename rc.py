# Import triangula module to interact with SixAxis
from triangula.input import SixAxis, SixAxisResource
import drivetrain
import time

class rc:
    def __init__(self, drive):
        """Class Constructor"""
        self.killed = False
        self.drive = drive

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """Start listening to the controller and pass state to drivetrain"""
        # Get a joystick, this will fail unless the SixAxis controller is paired and active
        # The bind_defaults argument specifies that we should bind actions to the SELECT and START buttons to
        # centre the controller and reset the calibration respectively.
        try:
            with SixAxisResource(bind_defaults=True) as joystick:
                # Loop indefinitely
                while not self.killed:
                    # Get button and joystick axis state
                    buttons_pressed = joystick.get_and_clear_button_press_history()

                    # Read the x and y axes of the left hand stick
                    lx = joystick.axes[0].corrected_value()
                    ly = joystick.axes[1].corrected_value()
                    # Read the x and y axes of the right hand stick
                    rx = joystick.axes[2].corrected_value()
                    ry = joystick.axes[3].corrected_value()

                    # Square Button
                    if buttons_pressed & 1 << SixAxis.BUTTON_SQUARE:
                        print 'SQUARE pressed since last check'

                    # Triangle Button
                    if buttons_pressed & 1 << SixAxis.BUTTON_TRIANGLE:
                        print 'Enable Motors'
                        self.drive.enable_motors(True)

                    # Cross Button
                    if buttons_pressed & 1 << SixAxis.BUTTON_CROSS:
                        print 'Disable Motors'
                        self.drive.enable_motors(False)

                    # Show the values to the screen
#                    print(lx,ly, rx,ry)
                    if self.drive is not None:
                        self.drive.mix_channels_and_send(lx, ly, rx, ry)
                    # Sleep a small amount between loop iterations
                    time.sleep(0.05)

        except (IOError):
            print("No PS3 Controller")

if __name__ == "__main__":
    drive = drivetrain.DriveTrain()
    rc = rc(drive)
    try:
        rc.run()
    except (KeyboardInterrupt) as e:
        #except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        print("Quitting")
