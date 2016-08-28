from triangula.input import SixAxis, SixAxisResource
import drivetrain
import time
import qr
import rc
import sounds
# GPIO


class launcher:
    def __init__(self):
        """ Class Constructor """
        self.killed = False
        self.sound = sounds.Sounds()
        self.drive = drivetrain.DriveTrain()
        # Modes
        self.rc = rc.rc(self.drive, self.sound)
        self.qr = qr.qr(self.drive, self.sound)

        self.MODE_RC = 1
        self.MODE_QR = 2
        self.mode = self.MODE_RC

    def stop(self):
        """ Simple method to stop the RC loop """
        self.killed = True

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
                            # If user hit STOP in ANY mode,
                            # stop and reset to RC mode
                            self.mode = self.MODE_RC

                        # Start Button
                        if buttons & 1 << SixAxis.BUTTON_START:
                            print('Start pressed')
                            if self.mode == self.MODE_QR:
                                self.qr.start()

                        # Pass "loop" call to either RC mode or QR mode
                        if self.mode == self.MODE_RC:
                            self.rc.loop(joystick, buttons)
                        elif self.mode == self.MODE_QR:
                            self.qr.loop()

                        # Sleep a small amount between loop iterations
                        time.sleep(0.05)

            except (IOError):
                print("No PS3 Controller")
                # Sleep for half a second to give user
                # time to connect a PS3 Controller
                time.sleep(0.5)


if __name__ == "__main__":
    launcher = launcher()
    try:
        launcher.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        launcher.stop()
        print("Quitting")
