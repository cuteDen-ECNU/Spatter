
import copy
import enum
import random

from Spatter.Configure import *

class ORACLE(enum.Enum):
    DoNothing = enum.auto()
    GeomCollection = enum.auto()
    Difference = enum.auto()
    SwapXY = enum.auto()


class TableUpdator():
    def __init__(self, configure: Configure) -> None:
        self.relation = {'t0': None}
        self.table_list = []
        self.oracle_list = list(ORACLE)
        
        
    def SelectOracle(self, table_list):
        self.table_list = copy.deepcopy(table_list)

        for t in self.table_list:
            oracle = random.choice(self.oracle_list)
            self.relation[t] = oracle


    def UpdateValidFromTable(self, target_table, src_table):
        return f'''UPDATE {target_table} 
        JOIN {src_table} ON {target_table}.id = {src_table}.id
        SET {target_table}.valid = {src_table}.valid;'''
    
    def UpdateTableIsValid(self, table:str):
        query = f'''UPDATE {table} SET valid = ST_IsValid(geom);'''
        return query

    def updateTableDifference(self, target_table: str):
        query = f'''UPDATE {target_table} 
        SET geom = ST_Difference(geom, ST_GeomFromText('GEOMETRYCOLLECTION EMPTY'))
        WHERE {target_table}.valid = True;'''
        return query

    def updateTableCollect(self, target_table: str):
        query = f'''UPDATE {target_table} 
        SET geom = GeomCollection(geom);'''
        return query
    
    def updateTableSwapXY(self, target_table: str):
        query = f'''UPDATE {target_table} 
        SET geom = ST_SwapXY(geom);'''
        return query
    