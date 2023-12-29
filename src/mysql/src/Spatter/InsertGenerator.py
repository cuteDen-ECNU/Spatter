import enum
import random
from  GeometryEnum import GeometryType

def randomIntPairs(n: int, ring: bool = False):
    x_b = random.randint(0, 1000)
    y_b = random.randint(0, 1000)
    x0 = random.randint(0, 100) + x_b
    y0 = random.randint(0, 100) + y_b
    s = f'({x0} {y0}'
    for _ in range(0, n - 1):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        s += (f',{x} {y} ')
    if ring == True:
        s += f',{x0} {y0})'
    else:
        s += ')'
    return s

def randomMultiPoint(maxn: int = 100, no_empty: bool = False):
    if no_empty == False and random.randint(0,1):
        return '''MULTIPOINT EMPTY'''
    s = '''MULTIPOINT('''
    for _ in range(0, random.randint(0, maxn)):
        s = s + randomIntPairs(1) + ','
    return s + randomIntPairs(1) + ')'
    
def randomLineString(maxn:int = 1000, no_empty: bool = False):
    if no_empty == False and random.randint(0,1):
        return '''LINESTRING EMPTY'''
    s = '''LINESTRING{int_pairs}'''  
    n = random.randint(3, maxn)
    return s.format(int_pairs = randomIntPairs(n, random.choice([True, False])))

def randomMultiLineString(maxn: int = 1000, no_empty: bool = False):
    n = random.randint(2, maxn)
    if no_empty == False and random.randint(0,1):
        return '''MULTILINESTRING EMPTY'''
    s = f'''MULTILINESTRING('''
    for _ in range(0, random.randint(0, 1)):
        s += (f'{randomIntPairs(n, random.choice([True, False]))}, ')
    
    s += (f'{randomIntPairs(n, random.choice([True, False]))})')
    return s

def randomPolygon(maxn: int = 1000, no_empty: bool = False):
    if no_empty == False and random.randint(0,2) == 0:
        return '''POLYGON EMPTY'''
    n = random.randint(3, maxn)
    s = '''POLYGON({int_pairs})'''.format(int_pairs = randomIntPairs(n, True))
    return s

def randomMultiPolygon(maxn: int = 1000, no_empty: bool = False):
    n = random.randint(3, maxn)
    if no_empty == False and random.randint(0,1):
        return '''MULTIPOLYGON EMPTY'''
    s = '''MULTIPOLYGON(({int_pairs})'''.format(int_pairs = randomIntPairs(n, True))
    for _ in range(0, random.randint(1, 3)):
        s += ''',({int_pairs})'''.format(int_pairs = randomIntPairs(n, True))
    return s + ')'

def randomGeomColl(recNum: int = 2, no_empty: bool = False):
    if recNum == 2:
        polygon_flag = False # only one polygon are allowed in geomcoll to avoid self-intersection 
    else:
        polygon_flag = True

    if no_empty == False and random.randint(0,1):
        return '''GEOMETRYCOLLECTION EMPTY'''
    s = '''GEOMETRYCOLLECTION('''
    geomNum = random.randint(1,2)
    comma = False
    
    
    
    for _ in range(0, geomNum):
        if comma == True:
            s += ','  
        else: 
            s += ''
        gtype_list = list(GeometryType)
        if recNum <= 0:
            gtype_list.remove(GeometryType.GEOMETRYCOLLECTION)
        if polygon_flag == True:
            gtype_list.remove(GeometryType.POLYGON)
            gtype_list.remove(GeometryType.MULTIPOLYGON)
        gtype = random.choice(gtype_list)
        
        if gtype == GeometryType.LINESTRING:
            s += randomLineString(5, no_empty=True)
        elif gtype == GeometryType.MULTILINESTRING:
            s += randomMultiLineString(2, no_empty=True)
        elif gtype == GeometryType.POLYGON:
            s += randomPolygon(5, no_empty=True)
            polygon_flag = True
        elif gtype == GeometryType.MULTIPOLYGON:
            s += randomMultiPolygon(5, no_empty=True)
            polygon_flag = True
        elif gtype == GeometryType.GEOMETRYCOLLECTION:
            s += randomGeomColl(recNum - 1, no_empty=True)
        elif gtype == GeometryType.POINT:
            s += f'''POINT{randomIntPairs(1)}'''
        elif gtype == GeometryType.MULTIPOINT:
            s += randomMultiPoint(3, no_empty=True)
        else:
            print(gtype)
        comma = True

        
    return s + ')'

def insertRandomly(target_table: str, id: int):
    gtype = random.choice(list(GeometryType))
    if gtype == GeometryType.LINESTRING:
        gstr = '\'' + randomLineString(maxn=3, no_empty=True) + '\'' 
        if random.randint(0,1):
            geom_str = f'''ST_LineFromText({gstr},0)'''
        else:
            geom_str = f'''ST_GeomFromText({gstr},0)'''
    
    elif gtype == GeometryType.MULTILINESTRING: 
        gstr = '\'' + randomMultiLineString(maxn=3, no_empty=True) + '\'' 
        if random.randint(0,1):
            geom_str = f'''ST_MLineFromText({gstr},0)'''
        else:
            geom_str = f'''ST_GeomFromText({gstr},0)'''
        
    elif gtype == GeometryType.POLYGON:
        gstr = '\'' + randomPolygon(maxn=4, no_empty=True) + '\''
        choice = random.randint(0,2)
        if choice == 0:
            geom_str = f'''ST_PolygonFromText({gstr},0)'''
        elif choice == 1:
            geom_str = f'''ST_GeomFromText({gstr},0)'''
        else:
            geom_str = f'''ST_ConvexHull(ST_MPointFromText('{randomMultiPoint(maxn=10, no_empty=True)}', 0))'''
    elif gtype == GeometryType.MULTIPOLYGON:
        gstr = '\'' + randomMultiPolygon(maxn=5, no_empty=True) + '\''
        if random.randint(0,1):
            geom_str = f'''ST_MPolyFromText({gstr},0)'''
        else:
            geom_str = f'''ST_GeomFromText({gstr},0)'''
    elif gtype == GeometryType.POINT:
        gstr = f'''\'POINT{randomIntPairs(1)}\''''
        if random.randint(0,1):
            geom_str = f'''ST_PointFromText({gstr},0)'''
        else:
            geom_str = f'''ST_GeomFromText({gstr},0)'''
    elif gtype == GeometryType.MULTIPOINT:
        gstr = '\'' + randomMultiPoint(maxn=10, no_empty=True) + '\''
        if random.randint(0,1):
            geom_str = f'''ST_MPointFromText({gstr},0)'''
        else:
            geom_str = f'''ST_GeomFromText({gstr},0)'''   
    elif gtype == GeometryType.GEOMETRYCOLLECTION:
        gstr = '\'' + randomGeomColl() + '\''
        if random.randint(0,1):
            geom_str = f'''ST_GeomCollFromText({gstr},0)'''
        else:
            geom_str = f'''ST_GeomFromText({gstr},0)'''
        
    else:
        print(gtype)
    
    query = f'''INSERT INTO {target_table} (id, geom) VALUES ({id}, {geom_str});'''
    
    return query

def insertFromExist(target_table: str, src_table: str):
    query = f'''INSERT INTO {target_table} (id, geom) SELECT id, geom FROM {src_table} '''
    return query


def insertFromExist3D(target_table: str, src_table: str, id: int):
    query = f'''INSERT INTO {target_table} (id, geom) SELECT {id}, ST_Force3D(geom) FROM {src_table} WHERE {src_table}.id = {id};'''
    return query


class InsertType(enum.Enum):
    GeometryN = enum.auto()
    Polygon = enum.auto()
    Buffer = enum.auto()
    Collect = enum.auto()


class InsertorError():
    def __init__(self) -> None:
        self.errors = ['''3673 (23000): Column 'geom' cannot be null''']
        self.use_type = []
    
    def usePolygon(self):
        if InsertType.Polygon not in self.use_type:
            self.errors.append('3037 (22023): Invalid GIS data provided to function polygon.') 
            self.use_type.append(InsertType.Polygon)

def insertGeometryN(src_table: str, id: int):
    query = f'''INSERT INTO origin (id, geom) SELECT {id}, ST_GeometryN(t.geom, {random.randint(0,10)}) FROM {src_table} As t 
    WHERE (ST_GeometryType(geom) = 'GEOMETRYCOLLECTION' or ST_GeometryType(geom) = 'MULTIPOLYGON' or ST_GeometryType(geom) = 'MULTILINESTRING') and valid = True
    ORDER BY RAND() LIMIT 1;'''
    return query

def insertPolygon(src_table: str, id: int):
    query = f'''INSERT INTO {src_table} (id, geom) 
    SELECT {id}, subquery.g
    FROM (
        SELECT Polygon(o.geom) As g FROM {src_table} As o
        WHERE ST_GeometryType(o.geom) = 'LINESTRING'
        ORDER BY RAND() LIMIT 1
    ) As subquery; '''
    return query

def insertBuffer(src_table: str, id: int):
    query = f'''INSERT INTO {src_table} (id, geom)
    SELECT {id}, ST_Buffer(geom, {random.randint(0, 10)}) FROM {src_table} As t
    WHERE valid = True
    ORDER BY RAND() LIMIT 1;
    '''
    return query

def insertCollect(src_table: str, id: int):
    query = f'''INSERT INTO {src_table} (id, geom)
    SELECT {id}, ST_Collect(DISTINCT geom) FROM {src_table} As t
    WHERE valid = True;
    '''
    return query
