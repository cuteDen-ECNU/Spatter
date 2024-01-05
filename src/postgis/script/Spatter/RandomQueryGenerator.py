import enum
import random

from Spatter.TableUpdator import ORACLE


class SelectType(enum.Enum):
    DISTINCT = enum.auto()
    ALL = enum.auto()

class GeometryRelation2D(enum.Enum):
    # two geoms
    INTERSECTS = "Intersects"
    CONTAINS = "Contains"
    WITHIN = "Within"
    CONTAINSPROPERLY = "ContainsProperly"
    COVEREDBY = "CoveredBy"
    COVERS = "Covers"
    OVERLAPS = "Overlaps"
    CROSSES = "Crosses"

    # two geoms and float
    DWITHIN = "DWithin"
    DFULLYWITHIN = "DFullyWithin"
    
    LINECROSSINGDIRECTION = "LineCrossingDirection"
    ORDERINGEQUALS = "OrderingEquals"
    EQUALS = "Equals"
    DISJOINT = "Disjoint"
    TOUCHES = "Touches"

class BoundingBoxOperator(enum.Enum):    
    ANDAND = "&&"
    ANDLEFT = "&<"
    ANDBELOW = "&<|"
    ANDRIGHT = "&>"
    LEFT = "<<"
    RIGHT = ">>"
    BELOW = "<<|"


class GeometryRalation3D(enum.Enum):
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
        self.errors = ['GEOSOverlaps']

    def useGeometryRelationWithIndex(self):
        self.errors.append('GeoContains')

    def createBoolPrediction3D(self, t0, t1):
        join_type = random.choice(list(JOINTYPE)).value
        index_functions = list(GeometryRalation3D)
        relation_func = random.choice(index_functions)

        if relation_func in [GeometryRalation3D.THREEDINTERSECTS]:
            cdt3D = f'''ST_{relation_func.value}''' + f'''(a1.geom, a2.geom)'''
            cdt2D = f'''ST_{relation_func.value[2:]}''' + f'''(a1.geom, a2.geom)'''

        elif relation_func in [GeometryRalation3D.THREEDFULLYWITHIN
                               ,GeometryRalation3D.THREEDDWITHIN]:
            distance = random.randint(0, 1000)
            cdt3D = f'''ST_{relation_func.value}''' + f'''(a1.geom, a2.geom, {distance})'''
            cdt2D = f'''ST_{relation_func.value[2:]}''' + f'''(a1.geom, a2.geom, {distance})'''
        else:
            print(relation_func)
            # exit(0)

        where_clause = f''' a1.valid = True and a2.valid = True and a1.id <> a2.id'''
        
        q1 = f'''SELECT COUNT(*)
        FROM {t0} As a1 
        {join_type} {t0} As a2 ON ''' + cdt2D + ''' 
        WHERE ''' + where_clause + ";"

        q2 = f'''SELECT COUNT(*)
        FROM {t1} As a1 
        {join_type} {t1} As a2 ON ''' + cdt3D + ''' 
        WHERE ''' + where_clause + ";"

        self.query_pair = [q1, q2]
        self.t_pair = [t0, t1]

        # add posible error
        self.errors.append('TopologyException')


    def createBoolPrediction(self, table_relation):
        t0, t1 = random.sample(self.table_list, 2)

        if table_relation[t0] == ORACLE.Affine3D:
            self.createBoolPrediction3D(t1, t0)
            return

        elif table_relation[t1] == ORACLE.Affine3D:
            self.createBoolPrediction3D(t0, t1)
            return

        join_type = random.choice(list(JOINTYPE)).value
        index_functions = list(GeometryRelation2D)

        remove_list = set()
        if table_relation[t0] == ORACLE.PointOnSurface or table_relation[t1] == ORACLE.PointOnSurface:
            remove_list.add(GeometryRelation2D.TOUCHES)
        
        if (table_relation[t0] in [ORACLE.ForcePolygonCCW, ORACLE.ForcePolygonCW, ORACLE.Normalize,
                           ORACLE.Multi, ORACLE.ForceCollection, ORACLE.CollectionHomogenize]
        or table_relation[t1] in [ORACLE.ForcePolygonCCW, ORACLE.ForcePolygonCW, ORACLE.Normalize,
                               ORACLE.Multi, ORACLE.ForceCollection, ORACLE.CollectionHomogenize]):
            remove_list.add(GeometryRelation2D.ORDERINGEQUALS)

        for r in remove_list:
            index_functions.remove(r)

        relation_func = random.choice(index_functions)

        if relation_func in [GeometryRelation2D.INTERSECTS
                              , GeometryRelation2D.CONTAINS
                              , GeometryRelation2D.WITHIN
                              , GeometryRelation2D.CONTAINSPROPERLY
                              , GeometryRelation2D.COVEREDBY
                              , GeometryRelation2D.COVERS
                              , GeometryRelation2D.OVERLAPS
                              , GeometryRelation2D.CROSSES
                              , GeometryRelation2D.EQUALS
                              , GeometryRelation2D.DISJOINT
                              , GeometryRelation2D.ORDERINGEQUALS
                              , GeometryRelation2D.TOUCHES]:
            condition = f'''ST_{relation_func.value}''' + f'''(a1.geom, a2.geom)'''
        elif relation_func in [GeometryRelation2D.DFULLYWITHIN
                                , GeometryRelation2D.DWITHIN]:
            distance = random.randint(0, 1000)
            condition = f'''ST_{relation_func.value}''' + f'''(a1.geom, a2.geom, {distance})'''
        elif relation_func == GeometryRelation2D.LINECROSSINGDIRECTION:
            
            condition = f'''ST_{relation_func.value}''' + f'''(a1.geom, a2.geom) > {random.randint(-3,3)}'''
        elif relation_func in [GeometryRelation2D.ANDAND,
                               GeometryRelation2D.ANDBELOW,
                               GeometryRelation2D.ANDLEFT,
                               GeometryRelation2D.ANDRIGHT,
                               GeometryRelation2D.BELOW,
                               GeometryRelation2D.RIGHT,
                               GeometryRelation2D.LEFT]:
            condition = f'''a1.geom {relation_func.value} a2.geom'''
            
        else:
            print(relation_func)
            # exit(0)
            
        where_clause = f''' a1.valid = True and a2.valid = True and a1.id <> a2.id'''
        
        q1 = f'''SELECT COUNT(*)
        FROM {t0} As a1 
        {join_type} {t0} As a2 ON ''' + condition + ''' 
        WHERE ''' + where_clause + ";"

        q2 = f'''SELECT COUNT(*)
        FROM {t1} As a1 
        {join_type} {t1} As a2 ON ''' + condition + ''' 
        WHERE ''' + where_clause + ";"


        self.query_pair = [q1, q2]
        self.t_pair = [t0, t1]

        # add posible error
        if relation_func == GeometryRelation2D.LINECROSSINGDIRECTION:
            self.errors.append('This function only accepts LINESTRING as arguments.')
        self.errors.append('TopologyException')


