import time


class qr:
    def __init__(self, drive, sounds):
        """ Class Constructor """
        self.killed = False
        self.drive = drive
        self.sounds = sounds

        self.nPause_between_commands = 0.5  # pause between command
        self.nFBSeconds = 1.0  # Drive forward/backward for # seconds
        self.nLRSeconds = 0.125  # Turn left/right for # seconds
        self.nZPSeconds = 0.5  # Pause/fire for # seconds

        self.route = []  # array (Command,  Repeat Count, Finish Time)
        self.nCurrent_item = -1  # -1 means not running
        self.running = False

    def stop(self):
        """ Simple method to stop the RC loop """
        self.running = False
        self.nCurrent_item = -1
        self.killed = True

    def run(self):
        """ Simple method to stop the RC loop """
        self.running = True
        self.nCurrent_item = -1
        self.killed = False

        route_length = len(self.route)
        if route_length:
            # Start Route by setting current item to zero
            self.nCurrent_item = 0
            # Calculate a finished time for each element to the route
            self.calculate_finished_time()

    def command_seconds(self, command):
        """ return the number of seconds this command char takes. """
        seconds = 0.5
        if command == 'F' or command == 'B':
            seconds = self.nFBSeconds
        elif command == 'L' or command == 'R':
            seconds = self.nLRSeconds
        elif command == 'P' or command == 'Z':
            seconds = self.nZPSeconds
        return seconds

    def calculate_finished_time(self):
        """ Calculate a finished time for each element to the route
        base upon hard coded time per command multiplied by repeat count. """
        start_time = time.time()
        for index, x in enumerate(self.route):
            time_per_command = self.command_seconds(x[0])
            finish_time = (start_time +
                           (time_per_command * x[1]))
            self.route[index] = (x[0], x[1], finish_time)
            # The start time for the NEXT item is the
            # finish time for this item with a small gap
            start_time = finish_time + self.nPause_between_commands

    def loop(self, joystick, buttons):
        """ Single loop to determin controller state and send to motors
        NOTE: DO NOT RUN ANYTHING THAT BLOCKS IN THIS METHOD """
        if not self.running:
            return  # Don't bother doing anything

        route_length = len(self.route)
        if self.current_item >= 0 and self.current_item < route_length:
            # Get current time and current item
            current_time = time.time()
            command, repeat_count, finish_time = self.route[self.current_item]

            # Test if we have finished this item
            if current_time > finish_time:
                # Finished, skip to next item
                self.current_item = self.current_item + 1
                self.drive.set_neutral()
                time.sleep(self.nPause_between_commands)
            else:
                # Current item is the one we are working on right now.
                if command == 'F':
                    self.drive.mix_channels_and_send(0.0, 1.0, 0.0, 1.0)
                elif command == 'B':
                    self.drive.mix_channels_and_send(0.0, -1.0, 0.0, -1.0)
                elif command == 'L':
                    self.drive.mix_channels_and_send(0.0, -1.0, 0.0, 1.0)
                elif command == 'R':
                    self.drive.mix_channels_and_send(0.0, 1.0, 0.0, -1.0)
                elif command == 'P':
                    print('P')  # Pause, don't need to do anything
                elif command == 'Z':
                    print('Z')  # Pulse laser on/off once.
        else:
            self.current_item = -1

    def isNumber(self, c):
        """ Simple test for whether character is a number """
        if (c == '0' or c == '1' or c == '2' or c == '3' or c == '4' or
           c == '5' or c == '6' or c == '7' or c == '8' or c == '9'):
            return True
        else:
            return False

    def process_command(self, commandChar, count):
        """ Simply add command and count to array """
        self.route.append((commandChar, count))

    def parse_command_string(self, commandString):
        """ Parse command string and perform move operation """
        nIndex = 0
        commandChar = ' '
        commandCount = 0
        countString = ''  # Initialise count string
        for c in commandString:
            if self.isNumber(c) == False:
                if commandChar != ' ':
                    commandCount = int(countString)
                    self.process_command(commandChar, commandCount)
                # 'c' should be the command character
                # (but not garanteed, its only NOT A NUMBER)
                commandChar = c

                # New command char found, reset count info
                countString = ''
                commandCount = 0
            else:
                # Add int char to int string
                countString += c

            # If its the final char, send it
            if nIndex == len(commandString)-1 and commandChar != ' ':
                commandCount = int(countString)
                self.process_command(commandChar, commandCount)

            # Increment loop counter
            nIndex = nIndex+1
