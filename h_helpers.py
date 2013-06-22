import threading
import subprocess

class CommandRunner(threading.Thread):
    def __init__(self, command_str, callback=None, name=None):
        threading.Thread.__init__(self)
        self.callback = callback
        self.command = command_str
        self.start()
        if name is None:
            name = command_str
        self.name = name

    def run(self):
        result = None
        try:
            output = subprocess.check_output(self.command.split(' '))
            result = output.decode("utf-8").strip()
        except Exception as e:
            result = None
        if self.callback:
            self.callback(result)
