# Import triangula module to interact with SixAxis
from triangula.input import SixAxis, SixAxisResource

# Button handler, will be bound to the square button later
def handler(button):
  print 'Button {} pressed'.format(button)

# Get a joystick, this will fail unless the SixAxis controller is paired and active
# The bind_defaults argument specifies that we should bind actions to the SELECT and START buttons to
# centre the controller and reset the calibration respectively.
with SixAxisResource(bind_defaults=True) as joystick:
    # Register a button handler for the square button
    joystick.register_button_handler(handler, SixAxis.BUTTON_SQUARE)
    try:
        # Loop indefinitely
        while 1:
            # Read the x and y axes of the left hand stick
            lx = joystick.axes[0].corrected_value()
            ly = joystick.axes[1].corrected_value()
            # Read the x and y axes of the right hand stick
            rx = joystick.axes[2].corrected_value()
            ry = joystick.axes[3].corrected_value()
            # Show the values to the screen
            print(lx,ly, rx,ry)

    except KeyboardInterrupt:
        # Handle CTRL+C
        print("Keyboard Interupt")
