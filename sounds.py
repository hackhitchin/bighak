import subprocess
import os

class Sounds:
    def __init__(self):
        """ Constructor for Member variables """
        self.playing = []  # List of dings and dongs
        self.limit_number = 4

    def Play(self, sound_file):
        """ Play Dong Sound """
        self.processPlaying(self.playing, self.limit_number)
        filename = 'sounds/' + sound_file
        if sound_file != "" and os.path.isfile(filename):
            self.playing.append(
                subprocess.Popen(["/usr/bin/aplay", '-q', filename])
            )
        return

    def processPlaying(self, playing, limit_number):
        """ Remove finished sound processes and
            limit sound processes to a set number """
        count = len(playing)
        if (count >= limit_number):
            # Remove the first few until process count is low enough
            for n in range(0, (count-limit_number)):
                item = playing[0]
                if item.poll() is None:
                    item.terminate()  # Wasnt finished, make it finished
                playing.pop(0)  # remove first item from list
