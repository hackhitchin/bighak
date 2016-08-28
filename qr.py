from time import sleep


class qr:
    def __init__(self, drive, sounds):
        """ Class Constructor """
        self.killed = False
        self.drive = drive
        self.sounds = sounds

        self.nPause = 0.5  # pause between command
        self.nInterval = 0.5  # In Seconds

    def stop(self):
        """ Simple method to stop the RC loop """
        self.killed = True

    def isNumber(self, c):
        """ Simple test for whether character is a number """
        if (c == '0' or c == '1' or c == '2' or c == '3' or c == '4' or
           c == '5' or c == '6' or c == '7' or c == '8' or c == '9'):
            return True
        else:
            return False

    def repeatSend(self, commandChar, nSeconds):
        # Send a single char repeatedly at a specific
        # interval for a specific length of time.
        # Have to play fireing sound here as it sounds as it lights LED
        if commandChar == 'P':
            # Play a sound to show that we are scanning
            self.sounds.Play("pew.wav")

        if (commandChar == 'Z'):
            # Uppercase 'Z' to turn LED ON
            serial.write('Z')
            serial.write('Z')
            serial.write('Z')
            serial.write('Z')
            serial.write('Z')
            # Play sound
            self.sounds.Play("pew.wav")
            # Lower case 'z' to turn LED OFF
            serial.write('z')
            serial.write('z')
            serial.write('z')
            serial.write('z')
            serial.write('z')
            sleep(0.3)
        else:
            while (nSeconds > 0.0):
                print(commandChar)
                serial.write(commandChar)
                sleep(self.nInterval)
                nSeconds = nSeconds - self.nInterval

    def sendCommandString(self, commandChar, count):
        """ Simply write to the serial device """
        nFBSeconds = 1.0
        nLRSeconds = 0.125
        nPSeconds = 0.5
        loop = 0
        while loop < count:
            if commandChar == 'F' or commandChar == 'B':
                self.repeatSend(commandChar, nFBSeconds)
            if commandChar == 'L' or commandChar == 'R':
                self.repeatSend(commandChar, nLRSeconds)
            if commandChar == 'P' or commandChar == 'Z':
                self.repeatSend(commandChar, nPSeconds)
            loop = loop + 1

    def parseCommandString(self, commandString):
        """ Parse command string and perform move operation """
        nIndex = 0
        commandChar = ' '
        commandCount = 0
        countString = ''  # Initialise count string
        for c in commandString:
            if self.isNumber(c) == False:
                if commandChar != ' ':
                    sleep(self.nPause)
                    commandCount = int(countString)
                    self.sendCommandString(commandChar, commandCount)
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
                sleep(self.nPause)
                commandCount = int(countString)
                self.sendCommandString(commandChar, commandCount)

            # Increment loop counter
            nIndex = nIndex+1
