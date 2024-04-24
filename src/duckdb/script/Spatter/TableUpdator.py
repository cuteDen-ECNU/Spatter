
import copy
import random

from Spatter.MatrixGenerator import *
from Spatter.Configure import *


class ORACLE(enum.Enum):
    DoNothing = enum.auto()
    Collect = enum.auto()
    Collect0 = enum.auto()
    Normalize = enum.auto()
    PointOnSurface = enum.auto()
    FlipCoordinates = enum.auto()
    Reverse = enum.auto()
    RemoveRepeatedPoints = enum.auto()

class TableUpdator():
    def __init__(self, configure: Configure) -> None:
        self.relation = {'t0': None}
        self.update_first = None
        self.table_list = []
        self.oracle_list = list(ORACLE)
        self.oracle_list.remove(ORACLE.Collect)
        self.oracle_list.remove(ORACLE.DoNothing)
        
    def SelectOracle(self, table_list):
        self.table_list = copy.deepcopy(table_list)

        for t in self.table_list:
            oracle = random.choice(self.oracle_list)
            self.relation[t] = oracle
    
    def UpdateTableIsValid(self, table:str):
        query = f'''UPDATE {table} SET valid = ST_IsValid(geom);'''
        return query
    

    def updateTableScale(self, table: str, scale):
        query = f'''UPDATE {table} 
        SET geom = ST_Scale(geom, {scale}, {scale});
        '''
        return query

    def updateTablePointOnSurface(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_Collect([ST_PointOnSurface(geom), geom]) 
        WHERE geom is not NULL and valid = true;
        '''
        return query
        
    def updateTableNormalize(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_Normalize(geom)
        WHERE valid = true;
        '''
        return query
    
    def updateTableFlipCoordinates(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_FlipCoordinates(geom);
        '''
        return query
    
    def updateTableCollect(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_Collect([geom])
        WHERE geom is not NULL;
        '''
        return query
    
    def updateTableCollect0(self, table: str):
        empty = random.choice(['POINT EMPTY', 'LINESTRING EMPTY', 'POLYGON EMPTY',
                               'MULTIPOINT EMPTY', 'MULTILINESTRING EMPTY', 
                               'MULTIPOLYGON EMPTY', 'GEOMETRYCOLLECTION EMPTY'])
        collect_list = [f'''ST_GeomFromText('{empty}'), t1.geom''', f'''t1.geom, ST_GeomFromText('{empty}')''']
        query = f'''UPDATE {table} 
        SET geom = ST_Collect([{random.choice(collect_list)}])
        WHERE geom is not NULL;
        '''
        return query
    

    def updateTableReverse(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_Reverse(geom)
        WHERE valid = true;'''
        return query
    
    def updateTableRemoveRepeatedPoints(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_RemoveRepeatedPoints(geom)
        WHERE valid = true;'''
        return query
    

    def UpdateValidFromTable(self, target_table: str, src_table: str):
        return f'''UPDATE {target_table} SET valid = {src_table}.valid
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;'''
    