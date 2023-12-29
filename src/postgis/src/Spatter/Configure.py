
import json


class Configure():
    def __init__(self) -> None:
        self.d = None

    def ReadConf(self, file_path: str):
        with open(file_path, "r") as of:
            self.d = json.load(of)
    
    def ReadDict(self, d: dict):
        self.d = d

    def GetSyntaxTrans(self):
        return self.d["syntax_trans"]    
    
    def GetCoordinatesTrans(self):
        return self.d["coordinates_trans"]    
    
    def GetName(self):
        return self.d["name"]    
    
    def GetUnit(self):
        return self.d["unit"]
    
    def GetGeneratorStatus(self):
        return self.d["completely_random_gen"]
    

    def __str__(self) -> str:
        return str(self.d)
        
