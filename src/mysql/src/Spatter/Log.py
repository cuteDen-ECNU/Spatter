import os
import time

class Log():

    def __init__(self, i) -> None:
        self.t = time.strftime("%Y-%m-%d-%H:%M:%S-" + str(i), time.localtime()) 
        log_directory = "/log"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        self.of_result = open(f"/log/result-{self.t}.log", "a+")
        self.of_error = open(f"/log/error-{self.t}.log","a+")
    
    def write_result(self, log:str):
        self.of_result.write(str(log) + '\n')
        self.of_result.flush()
    
    def write_error(self, log:str):
        self.of_error.write(log + '\n')
        self.of_error.flush()