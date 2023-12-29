
import enum
import random


class ORACLE(enum.Enum):
    Dimensions = enum.auto()
    GeomCollection = enum.auto()
    Difference = enum.auto()
    SwapXY = enum.auto()


class TableUpdator():
    def __init__(self, table_list) -> None:
        self.relation = {'origin': None}
        self.table_list = table_list
        oracle_list = list(ORACLE)
        oracle_list.remove(ORACLE.Dimensions)
        oracle_list.remove(ORACLE.SwapXY)
        oracle_list.remove(ORACLE.Difference)
        
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

    def updateTableDifference(target_table: str, src_table: str):
        query = f'''UPDATE {target_table} 
        JOIN origin ON {target_table}.id = origin.id 
        SET {target_table}.geom = ST_Difference({src_table}.geom, ST_GeomFromText('GEOMETRYCOLLECTION EMPTY'))
        WHERE {src_table}.valid = True;'''
        return query

    def updateTableCollect(target_table: str, src_table: str):
        query = f'''UPDATE {target_table} 
        JOIN origin ON {target_table}.id = origin.id
        SET {target_table}.geom = GeomCollection({src_table}.geom)
        WHERE {src_table}.valid = True;'''
        return query
    
    def updateTableSwapXY(target_table: str, src_table: str):
        query = f'''UPDATE {target_table} 
        JOIN origin ON {target_table}.id = origin.id
        SET {target_table}.geom = ST_SwapXY({src_table}.geom)
        WHERE {src_table}.valid = True;'''
        return query
    