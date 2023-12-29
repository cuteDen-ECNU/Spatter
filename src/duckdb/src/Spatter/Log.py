import os
import time

class Log():

    def __init__(self, i) -> None:
        self.name = time.strftime("%Y-%m-%d-%H:%M:%S-" + str(i), time.localtime()) 
        log_directory = "/log"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        self.of_result = open(f"/log/result-{self.name}.log", "a+")
        self.of_error = open(f"/log/error-{self.name}.log","a+")
    
    def WriteResult(self, log: str, note = False):
        with open(f"/log/result-{self.name}.log", "a+") as of:
            if note == True:
                prefix = "-- "
            else:
                prefix = ''
            of.write(prefix + str(log) + '\n')
            of.flush()

    def WriteError(self, log:str):
        self.of_error.write(log + '\n')
        self.of_error.flush()

    def GetResultPath(self) -> str:
        return f"/log/result-{self.name}.log"
    
    def ChangeFilePath(self, name):
        
        self.of_result = open(f"/log/result-{name}.log", "a+")
        self.of_error = open(f"/log/error-{name}.log","a+")
