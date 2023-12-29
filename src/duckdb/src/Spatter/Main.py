
import enum
import random
import InsertGenerator

from Executor import Executor
from Log import Log
from MatrixGenerator import Q_2_Affine_param, random_fraction_matrix
from RandomQueryGenerator import RandomQueryGenerator
from TableUpdator import ORACLE, TableUpdator
from QueriesReduce import *

log:Log = None
executor = None

class INDEXTYPE(enum.Enum):
     BTREE = enum.auto()
     HASH  = enum.auto()
     GIST  = enum.auto()
    #  GIN   = enum.auto()

def createTable(table: str):
    executor.execute(f'''DROP TABLE IF EXISTS {table}; ''')
    executor.execute(f'''CREATE TABLE {table} (id int, geom geometry, valid boolean, gRelate int);''')

def createIndex(table: str):
    index_type = random.choice(list(INDEXTYPE)).name
    executor.execute(f'''CREATE INDEX {table}_idx ON {table} USING {index_type} (geom);''')

def compareResult(rows1, rows2) -> bool:
    if len(rows1) != len(rows2):
        return False
    for i in range(0, len(rows1)):
        if len(rows1[i]) != len(rows2[i]):
            return False
        for j in range(0, len(rows1[i])):
            if rows1[i][j] != rows2[i][j]:
                return False
    return True

def recordTable(t):
    executor.execute(f'''COPY {t} TO '/log/{t}.csv' (FORMAT 'csv');''')

def main():
    
    oracle = ORACLE.PointOnSurface

    # create transform-based tables
    createTable("origin")
    createTable("tableA"); #createIndex("tableA")
    createTable("tableB"); #createIndex("tableB")
    gNum = 6
    
    for i in range(0, gNum):
        query = InsertGenerator.insertRandomly("origin", i)
        if oracle == ORACLE.PointOnSurface:
            pass
        else:
            print(oracle)
        executor.execute(query)
    
    query = TableUpdator.updateValid('origin')
    executor.execute(query)  

    insert_type = list(InsertGenerator.InsertType)

    insert_type.remove(InsertGenerator.InsertType.Buffer)
    insert_type.remove(InsertGenerator.InsertType.Centroid)
    insertErrorBox = InsertGenerator.InsertErrorBox()
    i = 0
    while(i < 2 * gNum):
        insert_func = random.choice(insert_type)
        if insert_func == InsertGenerator.InsertType.Boundary:
            query = InsertGenerator.insertBoundary("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.CollectionExtract:
            query = InsertGenerator.insertCollectionExtract("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.ConvexHull:
            query = InsertGenerator.insertConvexHull("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.Buffer:
            query = InsertGenerator.insertBuffer("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.Centroid:
            query = InsertGenerator.insertCentroid("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.Collect:
            query = InsertGenerator.insertCollect("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.Normalize:
            query = InsertGenerator.insertNormalize("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.MakeLine:
            query = InsertGenerator.insertMakeLine("origin", gNum + i)
            insertErrorBox.useMakeLine()
        else:
            print(insert_func)
        insert_num = executor.executeInsert(query, insertErrorBox.errors)
        i += insert_num
        
    
    query = InsertGenerator.insertFromExist("tableA", "origin")
    executor.execute(query)
    query = InsertGenerator.insertFromExist("tableB", "origin")
    executor.execute(query)

    query = TableUpdator.updateValid('origin')
    executor.execute(query)  
    
    # invarient transform
    table_list = ["tableA", "tableB"]
    tu = TableUpdator(table_list)

    for t in table_list:
        if tu.relation[t] == ORACLE.PointOnSurface:
            query = TableUpdator.updateTablePointOnSurface(t, "origin")
        elif tu.relation[t] == ORACLE.Normalize:
            query = TableUpdator.updateTableNormalize(t, "origin")
        elif tu.relation[t] == ORACLE.FlipCoordinates:
            query = TableUpdator.updateTableFlipCoordinates(t, "origin")
        elif tu.relation[t] == ORACLE.Collect:
            query = TableUpdator.updateTableCollect(t, "origin")

        else:
            print(tu.relation[t])
        executor.execute(query)
      
    for t in table_list:
        query = TableUpdator.updateValid(t)
        executor.execute(query)
        

    for i in range(0, 100):
        
        randomQueryGenerator = RandomQueryGenerator(["origin", "tableA", "tableB"])

        randomQueryGenerator.createQueryRelation(tu.relation)

        executor.executeSelect(randomQueryGenerator.query_pair[0], randomQueryGenerator.errors)
        res1 = executor.rows
        executor.executeSelect(randomQueryGenerator.query_pair[1], randomQueryGenerator.errors)
        res2 = executor.rows
         
        if compareResult(res1, res2) == False:
            log.WriteResult(f"Error in geometry relations: {res1}, {res2}.", note=True)
            reduce_file_path = log.GetResultPath()

            reduce = QueriesReducor(executor, reduce_file_path)

            reduce.SetErrors(insertErrorBox.errors + randomQueryGenerator.errors)
            reduce.Reduce(randomQueryGenerator)

            if reduce.cause_type == None:
                print("reduce.cause_type == None")
                exit(0)
        

    

if __name__ == '__main__':

    for i in range(0, 10000):
        random.seed(i)
        log = Log(i)
        executor = Executor(log)
        main()
        
    executor.close()     
    