import enum 

class GeometryType(enum.Enum):
    POINT = enum.auto()
    MULTIPOINT = enum.auto()
    LINESTRING = enum.auto()
    MULTILINESTRING = enum.auto()
    POLYGON = enum.auto()
    MULTIPOLYGON = enum.auto()
    GEOMETRYCOLLECTION = enum.auto()
    
    

