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
    def __init__(self) -> None:
        pass
    def randomIntPairs(n: int, ring: bool = False):
        
        x0 = random.randint(0, 100)
        y0 = random.randint(0, 100)
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
        for _ in range(0, random.randint(0, 1)):
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
        if NOEMPTY == True:
            no_empty = True
        else:
            no_empty = random.choice([True, False])
        
        
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
                s += RandomGenerator.randomLineString(5, no_empty)
            elif gtype == GeometryType.MULTILINESTRING:
                s += RandomGenerator.randomMultiLineString(2, no_empty)
            elif gtype == GeometryType.POLYGON:
                s += RandomGenerator.randomPolygon(5, no_empty)
                polygon_flag = True
            elif gtype == GeometryType.MULTIPOLYGON:
                s += RandomGenerator.randomMultiPolygon(5, no_empty)
                polygon_flag = True
            elif gtype == GeometryType.GEOMETRYCOLLECTION:
                s += RandomGenerator.randomGeomColl(recNum - 1, no_empty)
            elif gtype == GeometryType.POINT:
                s += f'''POINT{RandomGenerator.randomIntPairs(1)}'''
            elif gtype == GeometryType.MULTIPOINT:
                s += RandomGenerator.randomMultiPoint(3, no_empty)
            else:
                print(gtype)
            comma = True

            
        return s + ')'

    def insertRandomly(target_table: str, id: int):

        if NOEMPTY == True:
            no_empty = True
        else:
            no_empty = random.choice([True, False])
        
        type_list = list(GeometryType)
        gtype = random.choice(type_list)
        geom_str = RandomGenerator.getGeomStr(gtype, no_empty)
        query = f'''INSERT INTO {target_table} (id, geom) VALUES ({id},ST_Affine({geom_str}, 1, 0, 0, 1,{random.randint(-1000, 1000)},{random.randint(-1000, 1000)}));'''
        
        return query

    def getGeomStr(gtype: GeometryType, no_empty: bool = False):
        if gtype == GeometryType.LINESTRING:
            gstr = '\'' + RandomGenerator.randomLineString(3, no_empty) + '\'' 
            if random.randint(0,1):
                geom_str = f'''ST_LineFromText({gstr},0)'''
            else:
                geom_str = f'''ST_GeomFromText({gstr},0)'''
        
        elif gtype == GeometryType.MULTILINESTRING: 
            gstr = '\'' + RandomGenerator.randomMultiLineString(3, no_empty) + '\'' 
            if random.randint(0,1):
                geom_str = f'''ST_MLineFromText({gstr},0)'''
            else:
                geom_str = f'''ST_GeomFromText({gstr},0)'''
            
        elif gtype == GeometryType.POLYGON:
            gstr = '\'' + RandomGenerator.randomPolygon(10, no_empty) + '\''
            choice = random.randint(0,2)
            if choice == 0:
                geom_str = f'''ST_PolygonFromText({gstr},0)'''
            elif choice == 1:
                geom_str = f'''ST_GeomFromText({gstr},0)'''
            else:
                geom_str = f'''ST_ConvexHull(ST_MPointFromText('{RandomGenerator.randomMultiPoint(10, no_empty)}', 0))'''
        elif gtype == GeometryType.MULTIPOLYGON:
            gstr = '\'' + RandomGenerator.randomMultiPolygon(5, no_empty) + '\''
            if random.randint(0,1):
                geom_str = f'''ST_MPolyFromText({gstr},0)'''
            else:
                geom_str = f'''ST_GeomFromText({gstr},0)'''
        elif gtype == GeometryType.POINT:
            gstr = f'''\'POINT{RandomGenerator.randomIntPairs(1)}\''''
            if random.randint(0,1):
                geom_str = f'''ST_PointFromText({gstr},0)'''
            else:
                geom_str = f'''ST_GeomFromText({gstr},0)'''
        elif gtype == GeometryType.MULTIPOINT:
            gstr = '\'' + RandomGenerator.randomMultiPoint(10, no_empty) + '\''
            if random.randint(0,1):
                geom_str = f'''ST_MPointFromText({gstr},0)'''
            else:
                geom_str = f'''ST_GeomFromText({gstr},0)'''   
        elif gtype == GeometryType.GEOMETRYCOLLECTION:
            gstr = '\'' + RandomGenerator.randomGeomColl() + '\''
            if random.randint(0,1):
                geom_str = f'''ST_GeomCollFromText({gstr},0)'''
            else:
                geom_str = f'''ST_GeomFromText({gstr},0)'''
            
        else:
            print(gtype)
        
        return geom_str
        


class InsertGenerator():

    class InsertType(enum.Enum):
        GeometryN = enum.auto()
        Polygonize = enum.auto()
        Boundary = enum.auto()
        BoundingDiagonal = enum.auto()
        CollectionExtract = enum.auto()
        SetPoint = enum.auto()
        Dump = enum.auto()
        DumpRings = enum.auto()
        ConvexHull = enum.auto()
        Collect0 = enum.auto()
        Collect1 = enum.auto()
        Collect2 = enum.auto()
        Collect3 = enum.auto()
        Scale = enum.auto()
        Normalize = enum.auto()
        Multi = enum.auto()
        CollectionHomogenize = enum.auto()
        ForceCollection = enum.auto()
        Affine2D = enum.auto()
        PointOnSurface = enum.auto()
        RemoveRepeatedPoints = enum.auto()
        FlipCoordinates = enum.auto()
        ForcePolygonCCW = enum.auto()
        ForcePolygonCW = enum.auto()
        NULL = enum.auto()

    insert_weights = {
        InsertType.GeometryN: 6,
        InsertType.Polygonize: 6,
        InsertType.Boundary: 6,
        InsertType.BoundingDiagonal: 6,
        InsertType.CollectionExtract: 6,
        InsertType.SetPoint: 6,
        InsertType.Dump: 6,
        InsertType.DumpRings: 6,
        InsertType.ConvexHull: 6,
        InsertType.Collect0: 6,
        InsertType.Collect1: 6,
        InsertType.Collect2: 6,
        InsertType.Collect3: 1,
        InsertType.Scale: 6,
        InsertType.Normalize: 1,
        InsertType.Multi: 1,
        InsertType.CollectionHomogenize: 1,
        InsertType.ForceCollection: 1,
        InsertType.Affine2D: 6,
        InsertType.PointOnSurface: 1,
        InsertType.RemoveRepeatedPoints: 1,
        InsertType.FlipCoordinates: 1,
        InsertType.ForcePolygonCCW: 1,
        InsertType.ForcePolygonCW: 1,
        InsertType.NULL: 1
    }

    def insertGeometryN(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_GeometryN({src_table}.geom, {random.randint(0,10)})  
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query

    def insertPolygonize(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Polygonize({src_table}.geom)  
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query

    def insertBoundary(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Boundary({src_table}.geom) 
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query

    def insertBoundingDiagonal(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_BoundingDiagonal({src_table}.geom)
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query

    def insertCollectionExtract(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_CollectionExtract({src_table}.geom)  
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query

    def insertSetPoint(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_SetPoint({src_table}.geom, 0, 'POINT(-1 1)') 
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query


    def insertDump(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT row_number() OVER () + {id} - 1, sub_query.geom
        FROM (
        SELECT
            (ST_DUMP(geom)).geom AS geom 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}
        ) AS sub_query;
        '''
        return query


    def insertDumpRings(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT row_number() OVER () + {id} - 1, sub_query.geom 
        FROM (
        SELECT
            (ST_DumpRings(geom)).geom AS geom 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}
        ) AS sub_query;
        '''
        return query

    def insertConvexHull(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom)
        SELECT {id}, ST_ConvexHull(geom) 
        FROM {src_table}
        WHERE {src_table}.id = {base};
        '''
        return query

    def insertCollect0(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect(t0.geom, t2.geom) 
        FROM {src_table} As t0, {src_table} As t2
        WHERE t0.id = {random.randint(0, id - 1)}
        and t2.id = {random.randint(0, id - 1)}; '''
        return query

    def insertCollect1(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect(t0.geom, {RandomGenerator.getGeomStr(random.choice(list(GeometryType)))}) 
        FROM {src_table} As t0
        WHERE t0.id = {random.randint(0, id - 1)}; '''
        return query

    def insertCollect2(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect(ARRAY[t0.geom, t2.geom]) 
        FROM {src_table} As t0, {src_table} As t2
        WHERE t0.id = {random.randint(0, id - 1)}
        and t2.id = {random.randint(0, id - 1)}; '''
        return query

    def insertCollect3(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Collect({src_table}.geom) 
        FROM {src_table}; '''
        return query

    def insertScale(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Scale(t.geom, {random.randint(2,4)}, {random.randint(2,4)}) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertNormalize(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Normalize(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertMulti(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Multi(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertCollectionHomogenize(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_CollectionHomogenize(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertForceCollection(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_ForceCollection(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertAffine2D(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_Affine(t.geom, {random.randint(-10, 10)}, {random.randint(-10, 10)}, {random.randint(-10, 10)}, {random.randint(-10, 10)}, 0, 0) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertPointOnSurface(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_PointOnSurface(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertRemoveRepeatedPoints(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_RemoveRepeatedPoints(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertFlipCoordinates(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_FlipCoordinates(t.geom) 
        FROM {src_table} As t
        WHERE t.id = {random.randint(0, id - 1)}; 
        '''
        return query

    def insertForcePolygonCCW(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_ForcePolygonCCW({src_table}.geom)  
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query

    def insertForcePolygonCW(src_table: str, id: int):
        base = random.randint(0, id - 1)
        query = f'''INSERT INTO {src_table} (id, geom) 
        SELECT {id}, ST_ForcePolygonCW({src_table}.geom) 
        FROM {src_table}
        WHERE {src_table}.id = {base}; '''
        return query
    
    def insertNull(src_table: str, id: int):
        query = f'''INSERT INTO {src_table} (id, geom) SELECT {id}, NULL; '''
        return query

    def insertFromExist(target_table: str, src_table: str):
        query = f'''INSERT INTO {target_table} (id, geom) SELECT id, geom FROM {src_table}; '''
        return query


    def insertFromExist3D(target_table: str, src_table: str, id: int):
        query = f'''INSERT INTO {target_table} (id, geom) SELECT {id}, ST_Force3D(geom) FROM {src_table} WHERE {src_table}.id = {id};'''
        return query


    
class InsertErrorBox():
    def __init__(self) -> None:
        self.errors = []
        self.use_type = []
    
    def UseSetPoint(self):
        if InsertGenerator.InsertType.SetPoint not in self.use_type:
            self.errors.append('Line has no points') 
            self.errors.append('First argument must be a LINESTRING') 
            self.use_type.append(InsertGenerator.InsertType.SetPoint)

    def UseDumpRings(self):
        if InsertGenerator.InsertType.DumpRings not in self.use_type:
            self.errors.append('Input is not a polygon') 
            self.use_type.append(InsertGenerator.InsertType.DumpRings)

    def UseAll(self):
        self.UseDumpRings()
        self.UseSetPoint()

