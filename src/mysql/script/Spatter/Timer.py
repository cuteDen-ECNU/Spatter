
import time


class Timer():
    def __init__(self) -> None:
        self.start_time = time.time()
    
    def end(self):
        return (time.time() - self.start_time) * 1000
