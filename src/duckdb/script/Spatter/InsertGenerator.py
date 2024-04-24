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
        x, y = RandomGenerator.randomIntList(n)
        s = f'({x[0]} {y[0]}'
        for i in range(0, n - 1):
            s += (f',{x[i + 1]} {y[i + 1]} ')
        if ring == True:
            s += f',{x[0]} {y[0]})'
        else:
            s += ')'
        return s
    
    def randomIntList(n: int):
        x_b = random.randint(0, 100)
        y_b = random.randint(0, 100)
        x = [random.randint(0, 10) + x_b]
        y = [random.randint(0, 10) + y_b]
        for _ in range(0, n - 1):
            if random.randint(0, 4) == 0:
                x.append(x[-1])
                y.append(y[-1])
            else:
                x.append(random.randint(0, 10) + x_b)
                y.append(random.randint(0, 10) + y_b)
        return x, y

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
        s = '''MULTIPOLYGON(({int_pairs}'''.format(int_pairs = RandomGenerator.randomIntPairs(n, True))
        for _ in range(0, random.randint(1, 3)):
            s += ''',{int_pairs}'''.format(int_pairs = RandomGenerator.randomIntPairs(n, True))
        return s + '))'

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
        Collect0 = enum.auto()
        Collect1 = enum.auto()
        Collect2 = enum.auto()
        Dump = enum.auto()
        Envelope = enum.auto()
        EndPoint = enum.auto()
        ExteriorRing = enum.auto()
        FlipCoordinates = enum.auto()
        LineMerge = enum.auto()
        MakeLine = enum.auto()
        MakePolygon = enum.auto()
        Normalize = enum.auto()
        PointN = enum.auto()
        PointOnSurface = enum.auto()
        Reverse = enum.auto()
        RemoveRepeatedPoints = enum.auto()
        StartPoint = enum.auto()
        NULL = enum.auto()
    
    insert_weights = {
        InsertType.Boundary: 1,
        InsertType.CollectionExtract: 1,
        InsertType.ConvexHull: 4,
        InsertType.Collect0: 6,
        InsertType.Collect1: 4,
        InsertType.Collect2: 2,
        InsertType.Dump: 1,
        InsertType.Envelope: 4,
        InsertType.EndPoint: 1,
        InsertType.ExteriorRing: 1,
        InsertType.FlipCoordinates: 6,
        InsertType.LineMerge: 4,
        InsertType.MakeLine: 1,
        InsertType.MakePolygon: 4,
        InsertType.Normalize: 6,
        InsertType.PointN: 1,
        InsertType.PointOnSurface: 6,
        InsertType.Reverse: 4,
        InsertType.RemoveRepeatedPoints: 6,
        InsertType.StartPoint: 1,
        InsertType.NULL: 6
    }
    
    def insertFromExist(target_table: str, src_table: str):
        query = f'''INSERT INTO {target_table} (id, geom) SELECT id, geom FROM {src_table}; '''
        return query

    def insertNull(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) SELECT {id}, NULL; '''
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
        if random.randint(0, 1) == 0:
            sec_arg = ''
        else:
            sec_arg = f', {random.randint(1, 3)}'

        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_CollectionExtract(t.geom{sec_arg}) FROM {src_table} As t
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
    
    def insertCollect0(src_table: str, id: int):
        empty = random.choice(['POINT EMPTY', 'LINESTRING EMPTY', 'POLYGON EMPTY',
                               'MULTIPOINT EMPTY', 'MULTILINESTRING EMPTY', 
                               'MULTIPOLYGON EMPTY', 'GEOMETRYCOLLECTION EMPTY'])
        collect_list = [f'''ST_GeomFromText('{empty}'), t1.geom''', f'''t1.geom, ST_GeomFromText('{empty}')''']
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect([{random.choice(collect_list)}]) 
        FROM {src_table} As t1
        WHERE t1.id = {random.randint(0, id - 1)}; 
        '''
        return query
    
    def insertCollect1(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect([t1.geom]) 
        FROM {src_table} As t1
        WHERE t1.id = {random.randint(0, id - 1)}; 
        '''
        return query
    

    def insertCollect2(src_table: str, id: int):
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
        SELECT {id}, ST_MakeLine([geom]) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)} or t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertMakePolygon(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_MakePolygon(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertEnvelope(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_Envelope(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query
    
    def insertFlipCoordinates(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_FlipCoordinates(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query
    
    def insertPointN(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_PointN(t.geom, {random.randint(0, 10)}) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query
    
    def insertStartPoint(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_StartPoint(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query
    
    def insertEndPoint(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_EndPoint(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query
    
    def insertExteriorRing(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_ExteriorRing(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query            
    
    def insertReverse(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_Reverse(t.geom) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query            

    def insertRemoveRepeatedPoints(src_table: str, id: int):
        if random.randint(0, 1) == 0:
            sec_arg = ''
        else:
            sec_arg = f', {random.random() * random.randint(0, 10)}'

        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_RemoveRepeatedPoints(t.geom {sec_arg}) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query            

    def insertLineMerge(src_table: str, id: int):
        if random.randint(0, 1) == 0:
            sec_arg = ''
        else:
            sec_arg = f', {random.choice([True, False])}'

        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_LineMerge(t.geom {sec_arg}) FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query    
    
    def insertDump(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT row_number() OVER () + {id} - 1, sub_query.geom
        FROM (
        SELECT
            UNNEST(ST_DUMP(t.geom)).geom AS geom 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}
        ) AS sub_query;
        '''
        return query    
    
    def insertPointOnSurface(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_PointOnSurface(t.geom) 
        FROM {src_table} As t
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
    
    def useMakePolygon(self):
        if InsertGenerator.InsertType.MakePolygon not in self.use_type:
            self.errors.append('shell') 
            self.errors.append('only accepts') 
            self.use_type.append(InsertGenerator.InsertType.MakePolygon)
    
    def useRemoveRepeatedPoints(self):
        if InsertGenerator.InsertType.RemoveRepeatedPoints not in self.use_type:
            self.errors.append('IllegalArgumentException')
            self.use_type.append(InsertGenerator.InsertType.RemoveRepeatedPoints)
    
    def useNormalize(self):
        if InsertGenerator.InsertType.Normalize not in self.use_type:
            self.errors.append('IllegalArgumentException')
            self.use_type.append(InsertGenerator.InsertType.Normalize)
    
    def UseAll(self):
        self.useMakeLine()
        self.useRemoveRepeatedPoints()
        self.useNormalize()
