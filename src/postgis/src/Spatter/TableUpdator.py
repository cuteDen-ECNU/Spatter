
import copy
import enum
import random

from Spatter.MatrixGenerator import *
from Spatter.Configure import *

class ORACLE(enum.Enum):
    DoNothing = enum.auto()
    Normalize = enum.auto()
    Collect = enum.auto()
    Multi = enum.auto()
    CollectionHomogenize = enum.auto()
    ForceCollection = enum.auto()
    ForcePolygonCCW = enum.auto()
    ForcePolygonCW = enum.auto()
    PointOnSurface = enum.auto()
    RemoveRepeatedPoints = enum.auto()
    FlipCoordinates = enum.auto()
    # Rotate = enum.auto()
    Affine3D = enum.auto()
    Affine2D = enum.auto()

class SYNTAX_TRANS(enum.Enum):
    Normalize = ORACLE.Normalize
    Collect = ORACLE.Collect
    Multi = ORACLE.Multi
    CollectionHomogenize = ORACLE.CollectionHomogenize
    ForceCollection = ORACLE.ForceCollection
    ForcePolygonCCW = ORACLE.ForcePolygonCCW
    ForcePolygonCW = ORACLE.ForcePolygonCW
    RemoveRepeatedPoints = ORACLE.RemoveRepeatedPoints

class COORDINATES_TRANS(enum.Enum):
    PointOnSurface = ORACLE.PointOnSurface
    FlipCoordinates = ORACLE.FlipCoordinates
    # Rotate = ORACLE.Rotate
    Affine3D = ORACLE.Affine3D
    Affine2D = ORACLE.Affine2D

class TableUpdator():
    def __init__(self, configure: Configure) -> None:
        self.relation = {'t0': None}
        self.update_first = None
        self.table_list = []
        if configure.GetCoordinatesTrans() == False and configure.GetSyntaxTrans() == False:
            self.oracle_list = [ORACLE.DoNothing]
        elif configure.GetCoordinatesTrans() == False:
            self.oracle_list = [member.value for member in SYNTAX_TRANS]
        elif configure.GetSyntaxTrans() == False:
            self.oracle_list = [member.value for member in COORDINATES_TRANS]
        else:
            self.oracle_list = list(ORACLE)
        

    def SelectOracle(self, table_list):
        self.table_list = copy.deepcopy(table_list)

        for t in self.table_list:
            oracle = random.choice(self.oracle_list)
                
            if oracle in [ORACLE.Affine3D, ORACLE.Affine2D]:    
                self.update_first = t
                self.oracle_list.remove(ORACLE.Affine3D)
                self.oracle_list.remove(ORACLE.Affine2D)
            
            self.relation[t] = oracle

    def UpdateTableScale(self, target_table: str, src_table: str, scale):
        query = f'''UPDATE {target_table} 
        SET geom = ST_Scale({src_table}.geom, {scale}, {scale})
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;'''
        return query

    def UpdateValidFromTable(self, target_table, src_table):
        return f'''UPDATE {target_table} SET valid = {src_table}.valid
        FROM {src_table}
        WHERE {target_table}.id = {src_table}.id;'''
    
    def UpdateTableIsValid(self, table:str):
        query = f'''UPDATE {table} SET valid = ST_IsValid(geom);'''
        return query
    
    def UpdateTableMulti(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_Multi(geom);'''
        return query
    
    def UpdateTableNormalize(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_Normalize(geom);'''
        return query
    
    def UpdateTableCollect(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_Collect(ARRAY[geom]);'''
        return query
    
    def UpdateTableCollectionHomogenize(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_CollectionHomogenize(geom);'''
        return query
    
    def UpdateTableForceCollection(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_ForceCollection(geom);'''
        return query
    
    def UpdateTableFlipCoordinates(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_FlipCoordinates(geom);'''
        return query
    
    def UpdateTablePointOnSurface(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_Collect(ST_PointOnSurface(geom), geom);'''
        return query
    
    def UpdateTableRemoveRepeatedPoints(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_RemoveRepeatedPoints(geom);'''
        return query

    def UpdateTableForcePolygonCCW(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_ForcePolygonCCW(geom);'''
        return query

    def UpdateTableForcePolygonCW(self, table:str):
        query = f'''UPDATE {table} SET geom = ST_ForcePolygonCW(geom);'''
        return query


    def updateTableAffine3D(self, target_table: str, src_table: str):
        Q, scale = random_fraction_matrix(Dimensions.ThreeD, 2)
        affine_para = Q_2_Affine_param(Q * scale)
        query1 = f'''UPDATE {target_table} SET geom = ST_Affine(ST_Force3D(geom),{affine_para});'''
        query2 = f'''UPDATE {src_table} SET geom = ST_Scale(geom, {scale}, {scale});'''
        return query1 + query2
    
    def UpdateTableAffine2D(self, target_table: str, src_table: str):
        Q, scale = random_fraction_matrix(Dimensions.TwoD, 2)
        affine_para = Q_2_Affine_param(Q * scale)
        query1 = f'''UPDATE {target_table} SET geom = ST_Affine(geom,{affine_para});'''
        query2 = f'''UPDATE {src_table} SET geom = ST_Scale(geom, {scale}, {scale});'''
        return query1 + query2
