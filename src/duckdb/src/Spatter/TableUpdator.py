
import enum
import random


class ORACLE(enum.Enum):
    # Dimensions = enum.auto()
    PointOnSurface = enum.auto()
    Normalize = enum.auto()
    FlipCoordinates = enum.auto()
    Collect = enum.auto()


class TableUpdator():
    def __init__(self, table_list) -> None:
        self.relation = {'origin': None}
        self.table_list = table_list
        oracle_list = list(ORACLE)
        for t in self.table_list:
            self.relation[t] = random.choice(oracle_list)

    def updateTableScale(target_table: str, src_table: str, scale):
        query = f'''UPDATE {target_table} 
        SET geom = ST_Scale({src_table}.geom, {scale}, {scale})
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;'''
        return query

    def updateValid(t):
        return f'''UPDATE {t} SET valid = ST_IsValid({t}.geom);'''

    def updateTablePointOnSurface(target_table: str, src_table: str):
        fuc = random.choice(['ST_Normalize', 'ST_FlipCoordinates', ''])
        query = f'''UPDATE {target_table} 
        SET geom = {fuc}(ST_Collect([ST_PointOnSurface({src_table}.geom), {src_table}.geom]))
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;
        '''
        return query
        
    def updateTableNormalize(target_table: str, src_table: str):
        query = f'''UPDATE {target_table} 
        SET geom = ST_Normalize({src_table}.geom)
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;
        '''
        return query
    
    def updateTableFlipCoordinates(target_table: str, src_table: str):
        query = f'''UPDATE {target_table} 
        SET geom = ST_FlipCoordinates({src_table}.geom)
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;
        '''
        return query
    
    def updateTableCollect(target_table: str, src_table: str):
        query = f'''UPDATE {target_table} 
        SET geom = ST_Collect([{src_table}.geom])
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;
        '''
        return query
    
