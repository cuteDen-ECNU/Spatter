
import copy
import random

from Spatter.MatrixGenerator import *
from Spatter.Configure import *


class ORACLE(enum.Enum):
    DoNothing = enum.auto()
    Collect = enum.auto()
    Normalize = enum.auto()
    PointOnSurface = enum.auto()
    FlipCoordinates = enum.auto()

class TableUpdator():
    def __init__(self, configure: Configure) -> None:
        self.relation = {'t0': None}
        self.update_first = None
        self.table_list = []
        self.oracle_list = list(ORACLE)
        
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
        SET geom = ST_Collect([ST_PointOnSurface(geom), geom]);
        '''
        return query
        
    def updateTableNormalize(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_Normalize(geom);
        '''
        return query
    
    def updateTableFlipCoordinates(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_FlipCoordinates(geom);
        '''
        return query
    
    def updateTableCollect(self, table: str):
        query = f'''UPDATE {table} 
        SET geom = ST_Collect([geom]);
        '''
        return query
    

    def UpdateValidFromTable(self, target_table: str, src_table: str):
        return f'''UPDATE {target_table} SET valid = {src_table}.valid
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;'''
    