# Import triangula module to interact with SixAxis
from triangula.input import SixAxis, SixAxisResource
import drivetrain
import time
import sounds


class rc:
    def __init__(self, drive, sounds):
        """ Class Constructor """
        self.killed = False
        self.drive = drive
        self.sounds = sounds

    def stop(self):
        """ Simple method to stop the RC loop """
        self.killed = True

    def loop(self, joystick, buttons):
        """ Single loop to determin controller state and send to motors
        NOTE: DO NOT RUN ANYTHING THAT BLOCKS IN THIS METHOD """

        # Read the x and y axes of the left hand stick
        lx = joystick.axes[0].corrected_value()
        ly = joystick.axes[1].corrected_value()
        # Read the x and y axes of the right hand stick
        rx = joystick.axes[2].corrected_value()
        ry = joystick.axes[3].corrected_value()

        # DPad Buttons
        if buttons & 1 << SixAxis.BUTTON_D_DOWN:
            print('DPad Down pressed since last check')
            self.sounds.Play("pew.wav")

        # DPad Buttons
        if buttons & 1 << SixAxis.BUTTON_D_UP:
            print('DPad Up pressed since last check')
            self.sounds.Play("start.wav")

        # DPad Buttons
        if buttons & 1 << SixAxis.BUTTON_D_LEFT:
            print('DPad Left pressed since last check')

        # DPad Buttons
        if buttons & 1 << SixAxis.BUTTON_D_RIGHT:
            print('DPad Right pressed since last check')

        # Square Button
        if buttons & 1 << SixAxis.BUTTON_SQUARE:
            print('SQUARE pressed since last check')

        # Triangle Button
        # Cross Button
        # These buttons are handled by the launcher app.

        # Show the values to the screen
        if self.drive is not None:
            self.drive.mix_channels_and_send(lx, ly, rx, ry)

    def run(self):
        """ Start listening to the controller and pass state to drivetrain """
        # Get a joystick, this will fail unless the SixAxis controller is
        # paired and active The bind_defaults argument specifies that we
        # should bind actions to the SELECT and START buttons to
        # centre the controller and reset the calibration respectively.
        self.sounds.Play("start.wav")
        while not self.killed:
            try:
                with SixAxisResource(bind_defaults=True) as joystick:
                    # Loop indefinitely
                    while not self.killed:
                        # Get button and joystick axis state
                        buttons = joystick.get_and_clear_button_press_history()

                        # Triangle Button
                        if buttons & 1 << SixAxis.BUTTON_TRIANGLE:
                            print('Enable Motors')
                            self.sounds.Play("start.wav")
                            self.drive.enable_motors(True)
                            # If in AUTONOMOUS mode, start now

                        # Cross Button
                        if buttons & 1 << SixAxis.BUTTON_CROSS:
                            print('Disable Motors')
                            self.drive.enable_motors(False)

                        # Perform joystick and rc mode operations
                        self.loop(joystick, buttons)

                        # Sleep a small amount between loop iterations
                        time.sleep(0.05)

            except (IOError):
                print("No PS3 Controller")
                # Sleep for half a second to give user
                # time to connect a PS3 Controller
                time.sleep(0.5)


if __name__ == "__main__":
    sound = sounds.Sounds()
    drive = drivetrain.DriveTrain()
    rc = rc(drive, sound)
    try:
        rc.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        rc.stop()
        drive.stop()
        print("Quitting")
