import os
import time

class Log():

    def __init__(self, i = None) -> None:
        if i == None:
            return
        self.i = i
        self.name = time.strftime("%Y-%m-%d-%H:%M:%S-" + str(i), time.localtime()) 
        
        self.log_directory = "/log/spatter"
        self.result_path = os.path.join(self.log_directory,f"result-{self.name}.log")
        self.error_path = os.path.join(self.log_directory,f"error-{self.name}.log")

        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        self.of_result = open(self.result_path, "a+")
        self.of_error = open(self.error_path,"a+")
    

    def WriteResult(self, log: str, note = False):
        if note == True:
            prefix = "-- "
        else:
            prefix = ''
        self.of_result.write(prefix + str(log).strip() + '\n')
        self.of_result.flush()

    def WriteError(self, log:str):
        self.of_error.write(log + '\n')
        self.of_error.flush()
    
    def GetResultPath(self) -> str:
        return self.result_path
    
    def ChangeFileName(self, name):
        self.result_path = os.path.join(self.log_directory, f"result-{name}.log")
        self.error_path = os.path.join(self.log_directory, f"error-{name}.log")

        self.of_result = open(self.result_path, "a+")
        self.of_error = open(self.result_path, "a+")


    def ChangeFilePath(self, path):
        self.of_result = open(path + "-result.log", "a+")
        self.of_error = open(path + "-error.log", "a+")
