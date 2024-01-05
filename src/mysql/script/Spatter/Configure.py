
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
        return self.d["transformation_on"]    
    
    def GetCoordinatesTrans(self):
        return self.d["transformation_on"]    
    
    def GetName(self):
        return self.d["name"]    
    
    def GetUnit(self):
        return self.d["unit_coverage_on"]
    
    def GetSmartGeneratorOn(self):
        return self.d["smart_generator_on"]
    
    def GetGeometryNumber(self):
        return self.d["geometry_number"]

    def GetSeed(self):
        return self.d["seed"]

    def __str__(self) -> str:
        return str(self.d)
        
