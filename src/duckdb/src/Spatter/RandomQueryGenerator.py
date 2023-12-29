import enum
import random
from TableUpdator import ORACLE

class SelectType(enum.Enum):
    DISTINCT = enum.auto()
    ALL = enum.auto()

class GeometryRelationWithIndex(enum.Enum):
    # two geoms
    WITHIN = "Within"
    TOUCHES = "Touches"
    OVERLAPS = "Overlaps"
    CONTAINS = "Contains"
    COVEREDBY = "CoveredBy"
    COVERS = "Covers"
    CROSSES = "Crosses"
    # DIFFERENCE = "Difference"
    DISJOINT = "Disjoint"
    INTERSECTS = "Intersects"
    EQUALS = "Equals"
    CONTAINSPROPERLY = "ContainsProperly"
    INTERSECTSEXTENT = "Intersects_Extent"

    # two geoms and float
    DWITHIN = "DWithin"
    # DFULLYWITHIN = "DFullyWithin"
    
    
    # LINECROSSINGDIRECTION = "LineCrossingDirection"
    # ORDERINGEQUALS = "OrderingEquals"
    # EQUALS = "Equals"

class ThreeDRalationWithIndex(enum.Enum):
    THREEDINTERSECTS = "3DIntersects"
    THREEDDWITHIN = "3DDWithin"
    THREEDFULLYWITHIN = "3DDFullyWithin"

class JOINTYPE(enum.Enum):
    INNERJOIN = "JOIN"
    LEFTOUTJOIN = "LEFT OUTER JOIN"
    RIGHTOUTJOIN = "RIGHT OUTER JOIN"
    # FULLOUTJOIN = "FULL OUTER JOIN"



class RandomQueryGenerator():
    def __init__(self, table_list) -> None:
        self.table_list = table_list
        self.t_pair = []
        self.query_pair = []
        self.errors = []

    def useGeometryRelationWithIndex(self):
        self.errors.append('GeoContains')

    def createQueryDimension(self, scale: int):

        #where id clause
        gid1 = random.randint(0, 100); gid2 = random.randint(gid1, 100); gid3 = random.randint(0, 100); gid4 = random.randint(gid3, 100); 
        where_clause_a = f" a1.valid = True and a2.valid = True and a1.id <> a2.id"
        where_clause_b = f" b1.valid = True and b2.valid = True and b1.id <> b2.id"
        
        #join condition clause
        relation = random.choice(list(ThreeDRalationWithIndex))

        relation3D = relation.value
        relation2D = relation3D[2:]

        distance = random.randint(1, 1000)
        if relation == ThreeDRalationWithIndex.THREEDFULLYWITHIN or relation == ThreeDRalationWithIndex.THREEDDWITHIN:
            conditionO = f'''ST_{relation2D}''' + f'''(a1.geom, a2.geom, {distance})'''
            condition2D = f'''ST_{relation2D}''' + f'''(a1.geom, a2.geom, {distance*scale})'''
            condition3D = f'''ST_{relation3D}''' + f'''(b1.geom, b2.geom, {distance*scale})''' 
        else:
            conditionO = f'''ST_{relation2D}''' + f'''(a1.geom, a2.geom)'''
            condition2D = f'''ST_{relation2D}''' + f'''(a1.geom, a2.geom)'''
            condition3D = f'''ST_{relation3D}''' + f'''(b1.geom, b2.geom)''' 

        # if relation == ThreeDRalationWithIndex.THREEDDWITHIN:
        #     where_clause_a += ''' and a1.geom <> a2.geom'''
        #     where_clause_b += ''' and a1.geom <> a2.geom'''
        
        join_type = random.choice(list(JOINTYPE)).value

        sO = f'''SELECT COUNT(*)
        FROM {self.o} As a1 
        {join_type} {self.o} As a2 ON ''' + conditionO + ''' 
        WHERE ''' + where_clause_a + ";"

        s2D = f'''SELECT COUNT(*)
        FROM {self.a} As a1 
        {join_type} {self.a} As a2 ON ''' + condition2D + ''' 
        WHERE ''' + where_clause_a + ";"

        s3D = f'''SELECT COUNT(*)
        FROM {self.b} As b1 
        {join_type} {self.b} As b2 ON ''' + condition3D + ''' 
        WHERE ''' + where_clause_b + ";"
        
        # s = f'''SELECT ST_Intersects(a1.geom, a2.geom) = ST_3DIntersects(b1.geom, b2.geom) 
        # FROM {self.a} As a1
        # JOIN {self.b} As b1 ON b1.id = a1.id
        # {join_type} {self.a} As a2 ON ({condition2D})
        # {join_type} {self.b} As b2 ON ({condition3D}) and a2.id = b2.id
        # WHERE a2.valid = true and a1.id != a2.id and b1.id != b2.id;
        # '''



        self.query_pair = [sO, s2D, s3D]

    def createRandomQuery(self) -> str:

        

        if random.randint(0,1) == 0:
            # all geometry is valid
            s = '''SELECT a.id, ST_AsText({a})\n'''
            s += f'''FROM {self.a} As a1
            JOIN {self.a} As a2 ON ST_Cover(a1.geom, a2.geom)
            JOIN {self.b} As b1 ON a1.id = b1.id 
            JOIN {self.b} As b2 ON ST_Cover(b1.geom, b2.geom)'''

        s = '''SELECT a.id
        , ST_AsText({a})
        , ST_IsValid({a})
        , ST_IsValid({b})
        FROM tableA As a1
        JOIN tableA As a2 ON ST_Cover(a1.geom, a2.geom)
        JOIN tableB As b1 ON a1.id = b1.id 
        JOIN tableB As b2 ON ST_Cover(b1.geom, b2.geom)
        WHERE a1.id = {gid}'''
        
        return s
    
    def createQueryRelation(self, table_relation):
        t1, t2 = random.sample(self.table_list, 2)
        join_type = random.choice(list(JOINTYPE)).value

        index_functions = list(GeometryRelationWithIndex)
        
        remove_list = set()
 
        for r in remove_list:
            index_functions.remove(r)
    
        index_function = random.choice(index_functions)

        if index_function in [GeometryRelationWithIndex.INTERSECTS
                              , GeometryRelationWithIndex.CONTAINS
                              , GeometryRelationWithIndex.WITHIN
                              , GeometryRelationWithIndex.CONTAINSPROPERLY
                              , GeometryRelationWithIndex.COVEREDBY
                              , GeometryRelationWithIndex.COVERS
                              , GeometryRelationWithIndex.OVERLAPS
                              , GeometryRelationWithIndex.CROSSES
                              , GeometryRelationWithIndex.INTERSECTSEXTENT
                              , GeometryRelationWithIndex.TOUCHES
                              , GeometryRelationWithIndex.EQUALS
                              , GeometryRelationWithIndex.DISJOINT]:
            condition = f'''ST_{index_function.value}''' + f'''(a1.geom, a2.geom)'''
        elif index_function in [GeometryRelationWithIndex.DWITHIN]:
            distance = random.randint(1, 1000)
            condition = f'''ST_{index_function.value}''' + f'''(a1.geom, a2.geom, {distance})'''
        else:
            print(index_function)
            
        where_clause = f''' a1.valid = True and a2.valid = True and a1.id <> a2.id'''

        
        q1 = f'''SELECT COUNT(*)
        FROM {t1} As a1 
        {join_type} {t1} As a2 ON ''' + condition + ''' 
        WHERE ''' + where_clause + ";"

        q2 = f'''SELECT COUNT(*)
        FROM {t2} As a1 
        {join_type} {t2} As a2 ON ''' + condition + ''' 
        WHERE ''' + where_clause + ";"


        self.query_pair = [q1, q2]
        self.t_pair = [t1, t2]
        
        self.errors.append('TopologyException')
