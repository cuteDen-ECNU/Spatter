import enum
import random

NOEMPTY = False

class GeometryType(enum.Enum):
    POINT = enum.auto()
    MULTIPOINT = enum.auto()
    LINESTRING = enum.auto()
    MULTILINESTRING = enum.auto()
    POLYGON = enum.auto()
    MULTIPOLYGON = enum.auto()
    GEOMETRYCOLLECTION = enum.auto()


class RandomGenerator():
    def randomIntPairs(n: int, ring: bool = False):
        x_b = random.randint(0, 100)
        y_b = random.randint(0, 100)
        x0 = random.randint(0, 10) + x_b
        y0 = random.randint(0, 10) + y_b
        s = f'({x0} {y0}'
        for _ in range(0, n - 1):
            x = random.randint(0, 10) + x_b
            y = random.randint(0, 10) + y_b
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
            s = s + RandomGenerator.randomIntPairs(1) + ','
        return s + RandomGenerator.randomIntPairs(1) + ')'
        
    def randomLineString(maxn:int = 1000, no_empty: bool = False):
        if no_empty == False and random.randint(0,1):
            return '''LINESTRING EMPTY'''
        s = '''LINESTRING{int_pairs}'''  
        n = random.randint(3, maxn)
        return s.format(int_pairs = RandomGenerator.randomIntPairs(n, random.choice([True, False])))

    def randomMultiLineString(maxn: int = 1000, no_empty: bool = False):
        n = random.randint(2, maxn)
        if no_empty == False and random.randint(0,1):
            return '''MULTILINESTRING EMPTY'''
        s = f'''MULTILINESTRING('''
        for _ in range(0, random.randint(1, 2)):
            s += (f'{RandomGenerator.randomIntPairs(n, random.choice([True, False]))}, ')
        
        s += (f'{RandomGenerator.randomIntPairs(n, random.choice([True, False]))})')
        return s

    def randomPolygon(maxn: int = 1000, no_empty: bool = False):
        if no_empty == False and random.randint(0,2) == 0:
            return '''POLYGON EMPTY'''
        n = random.randint(3, maxn)
        s = '''POLYGON({int_pairs})'''.format(int_pairs = RandomGenerator.randomIntPairs(n, True))
        return s

    def randomMultiPolygon(maxn: int = 1000, no_empty: bool = False):
        n = random.randint(3, maxn)
        if no_empty == False and random.randint(0,1):
            return '''MULTIPOLYGON EMPTY'''
        s = '''MULTIPOLYGON(({int_pairs})'''.format(int_pairs = RandomGenerator.randomIntPairs(n, True))
        for _ in range(0, random.randint(1, 3)):
            s += ''',({int_pairs})'''.format(int_pairs = RandomGenerator.randomIntPairs(n, True))
        return s + ')'

    def randomGeomColl(recNum: int = 2, no_empty: bool = False):
        if recNum == 2:
            polygon_flag = False # only one polygon are allowed in geomcoll to avoid self-intersection 
        else:
            polygon_flag = True

        if no_empty == False and random.randint(0,1):
            return '''GEOMETRYCOLLECTION EMPTY'''
        s = '''GEOMETRYCOLLECTION('''
        geomNum = random.randint(3, 4)
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
                s += RandomGenerator.randomLineString(5, no_empty=True)
            elif gtype == GeometryType.MULTILINESTRING:
                s += RandomGenerator.randomMultiLineString(2, no_empty=True)
            elif gtype == GeometryType.POLYGON:
                s += RandomGenerator.randomPolygon(5, no_empty=True)
                polygon_flag = True
            elif gtype == GeometryType.MULTIPOLYGON:
                s += RandomGenerator.randomMultiPolygon(5, no_empty=True)
                polygon_flag = True
            elif gtype == GeometryType.GEOMETRYCOLLECTION:
                s += RandomGenerator.randomGeomColl(recNum - 1, no_empty=True)
            elif gtype == GeometryType.POINT:
                s += f'''POINT{RandomGenerator.randomIntPairs(1)}'''
            elif gtype == GeometryType.MULTIPOINT:
                s += RandomGenerator.randomMultiPoint(5, no_empty=True)
            else:
                print(gtype)
            comma = True

            
        return s + ')'

    def insertRandomly(target_table: str, id: int):
        
        if NOEMPTY == True:
            no_empty = True
        else:
            no_empty = random.choice([True, False])
        
        
        gtype = random.choice(list(GeometryType))
        if gtype == GeometryType.LINESTRING:
            gstr = '\'' + RandomGenerator.randomLineString(10, no_empty) + '\'' 
            geom_str = f'''ST_GeomFromText({gstr})'''
        
        elif gtype == GeometryType.MULTILINESTRING: 
            gstr = '\'' + RandomGenerator.randomMultiLineString(10, no_empty) + '\'' 
            geom_str = f'''ST_GeomFromText({gstr})'''   
            
        elif gtype == GeometryType.POLYGON:
            gstr = '\'' + RandomGenerator.randomPolygon(10, no_empty) + '\''
            geom_str = f'''ST_GeomFromText({gstr})'''   
            
        elif gtype == GeometryType.MULTIPOLYGON:
            gstr = '\'' + RandomGenerator.randomMultiPolygon(10, no_empty) + '\''
            geom_str = f'''ST_GeomFromText({gstr})'''   
            
        elif gtype == GeometryType.POINT:
            gstr = f'''\'POINT{RandomGenerator.randomIntPairs(1)}\''''
            geom_str = f'''ST_GeomFromText({gstr})'''   
            
        elif gtype == GeometryType.MULTIPOINT:
            gstr = '\'' + RandomGenerator.randomMultiPoint(10, no_empty) + '\''
            geom_str = f'''ST_GeomFromText({gstr})'''   
            
        elif gtype == GeometryType.GEOMETRYCOLLECTION:
            gstr = '\'' + RandomGenerator.randomGeomColl(no_empty) + '\''
            geom_str = f'''ST_GeomFromText({gstr})'''

            
        else:
            print(gtype)
        
        query = f'''INSERT INTO {target_table} (id, geom) VALUES ({id}, {geom_str});'''
        
        return query


class InsertGenerator():

    class InsertType(enum.Enum):
        Boundary = enum.auto()
        CollectionExtract = enum.auto()
        ConvexHull = enum.auto()
        Collect = enum.auto()
        Normalize = enum.auto()
        MakeLine = enum.auto()

    
    def insertFromExist(target_table: str, src_table: str):
        query = f'''INSERT INTO {target_table} (id, geom) SELECT id, geom FROM {src_table}; '''
        return query


    def insertFromExist3D(target_table: str, src_table: str, id: int):
        query = f'''INSERT INTO {target_table} (id, geom) SELECT {id}, ST_Force3D(geom) FROM {src_table} WHERE {src_table}.id = {id};'''
        return query

    def insertConvexHull(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_ConvexHull(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)};
        '''
        return query

    def insertCollectionExtract(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_CollectionExtract(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; '''
        return query

    def insertBoundary(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_Boundary(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertBuffer(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_Buffer(t.geom, 4, 1) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertCentroid(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_Centroid(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertCollect(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect([t1.geom, t2.geom]) 
        FROM {src_table} As t1, {src_table} As t2
        WHERE t1.id = {random.randint(0, id - 1)}
        and t2.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertDifference(src_table: str, id: int):
        query = f'''SELECT {id}, ST_Difference(t1.geom, t2.geom) 
        FROM {src_table} As t1, {src_table} As t2
        WHERE t1.id = {random.randint(0, id - 1)}
        and t2.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertNormalize(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_Normalize(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertMakeLine(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_MakeLine([t.geom]) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query


class InsertErrorBox():
    def __init__(self) -> None:
        self.errors = []
        self.use_type = []
    
    def useMakeLine(self):
        if InsertGenerator.InsertType.MakeLine not in self.use_type:
            self.errors.append('Invalid Input Error') 
            self.use_type.append(InsertGenerator.InsertType.MakeLine)

    def UseAll(self):
        self.useMakeLine()
