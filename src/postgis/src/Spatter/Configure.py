
import json


class Configure():
    def __init__(self, file_path) -> None:
        with open(file_path, "r") as of:
            self.d = json.load(of)

    def GetSyntaxTrans(self):
        return self.d["syntax_trans"]    
    
    def GetCoordinatesTrans(self):
        return self.d["coordinates_trans"]    
    
    def GetName(self):
        return self.d["name"]    
    
    def GetUnit(self):
        return self.d["unit"]

    def OffCoordinateTrans(self):
        self.d["coordinates_trans"] = False
    
    def OffSyntaxTrans(self):
        self.d["syntax_trans"] = False
        
    def __str__(self) -> str:
        return str(self.d)
        
