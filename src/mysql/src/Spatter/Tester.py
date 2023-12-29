
import enum
import random
import InsertGenerator
from Executor import Executor
from Log import Log
from MatrixGenerator import Q_2_Affine_param, random_fraction_matrix
from RandomQueryGenerator import RandomQueryGenerator
from TableUpdator import TableUpdator, ORACLE

log:Log = Log(0)
executor = Executor(log)

class INDEXTYPE(enum.Enum):
     BTREE = enum.auto()
     HASH  = enum.auto()
     GIST  = enum.auto()
    #  GIN   = enum.auto()

def createTable(table: str):
    executor.execute(f'''DROP TABLE IF EXISTS {table}; ''')
    executor.execute(f'''CREATE TABLE {table} (id int, geom geometry NOT NULL srid 0, valid boolean, gRelate int);''')
    # executor.execute(f'''DROP INDEX sp_index_geom ON {table};''')

def createIndex(table: str):
    executor.execute(f'''CREATE SPATIAL INDEX sp_index_geom ON {table}(geom);''')
 
# def createIndex(table: str):
#     index_type = random.choice(list(INDEXTYPE)).name
#     executor.execute(f'''CREATE INDEX {table}_idx ON {table} USING {index_type} (geom);''')

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

def updateTableValidValue(target_table: str, src_table: str):
    executor.execute(f'''UPDATE {target_table}
    SET valid = {src_table}.valid
    FROM {src_table}
    WHERE {target_table}.id = {src_table}.id;''')

def updateTableScale(target_table: str, src_table: str, scale):
    executor.execute(f'''UPDATE {target_table} 
    SET geom = ST_Scale({src_table}.geom, {scale}, {scale})
    FROM {src_table}
    WHERE {target_table}.id = {src_table}.id;''')

    updateTableValidValue(target_table, src_table)
    
def updateTableAffine(target_table: str, src_table: str, affine_para):
    executor.execute(f'''UPDATE {target_table} 
    SET geom = ST_Affine(ST_Force3D({src_table}.geom), {affine_para})
    FROM {src_table}
    WHERE {target_table}.id = {src_table}.id;''')
    
    updateTableValidValue(target_table, src_table)

def updateTableAddingPoint(target_table: str, src_table: str):
    editor = random.choice(['ST_Multi', 'ST_CollectionHomogenize', 'ST_FlipCoordinates'])

    if editor == 'ST_Multi':
        trans = f'''ST_Multi({src_table}.geom)'''
    else:
        trans = f'''{editor}(ST_Collect(ST_PointOnSurface({src_table}.geom), {src_table}.geom))'''
    

    executor.execute(f'''UPDATE {target_table} 
    SET geom = {trans}
    FROM {src_table}
    WHERE {target_table}.id = {src_table}.id
    and {src_table}.valid = True ;''', [])
    
    updateTableValidValue(target_table, src_table)

def main():
    # executor.execute("CREATE extension postgis;", [])
    # oracle = random.choice(list(ORACLE))
    executor.execute('''CREATE DATABASE IF NOT EXISTS nyc;''')
    executor.execute('''USE nyc;''')
    # create transform-based tables
    createTable("origin")
    createTable("tableA")
    createTable("tableB")
    gNum = 6
    
    for i in range(0, gNum):
        query = InsertGenerator.insertRandomly("origin", i)
        executor.execute(query)
    
    query = "UPDATE origin SET valid = ST_IsValid(origin.geom);"
    executor.execute(query)  

    insert_type = list(InsertGenerator.InsertType)

    insertorError = InsertGenerator.InsertorError()
    i = 0
    while(i < 2*gNum):
        insert_func = random.choice(insert_type)
        if insert_func == InsertGenerator.InsertType.GeometryN:
            query = InsertGenerator.insertGeometryN("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.Polygon:
            query = InsertGenerator.insertPolygon("origin", gNum + i)
            insertorError.usePolygon()
            print(insertorError.errors)
        elif insert_func == InsertGenerator.InsertType.Buffer:
            query = InsertGenerator.insertBuffer("origin", gNum + i)
        elif insert_func == InsertGenerator.InsertType.Collect:
            query = InsertGenerator.insertCollect("origin", gNum + i)
        
        else:
            print(insert_func)
        insert_num = executor.executeInsert(query, insertorError.errors)
        i += insert_num
        
    
    query = InsertGenerator.insertFromExist("tableA", "origin")
    executor.execute(query)
    query = InsertGenerator.insertFromExist("tableB", "origin")
    executor.execute(query)

    query = "UPDATE origin SET valid = ST_IsValid(origin.geom);"
    executor.execute(query)    
    

    # invarient transform
    table_list = ["tableA", "tableB"]
    tu = TableUpdator(table_list)

    for t in table_list:
        if tu.relation[t] == ORACLE.Dimensions:
            pass
        
        elif tu.relation[t] == ORACLE.GeomCollection:
            query = TableUpdator.updateTableCollect(t, "origin")
        elif tu.relation[t] == ORACLE.Difference:
            query = TableUpdator.updateTableDifference(t, "origin")
        elif tu.relation[t] == ORACLE.SwapXY:
            query = TableUpdator.updateTableSwapXY(t, "origin")
        else:
            print(tu.relation[t])
            exit(0)
        executor.execute(query)
    
    for t in table_list:
        query = TableUpdator.updateValid(t)
        executor.execute(query)
        
    # createIndex("origin")
    createIndex("tableA")
    createIndex("tableB")

    for _ in range(0, 100):
        
            # Q, scale = random_fraction_matrix(2)
            # affine_para = Q_2_Affine_param(Q * scale)
            
            # # log.write_result('Q:\n' + str(Q) + '\nscale:' + str(scale) + '\n')
            # if oracle == ORACLE.Dimensions:
            #     updateTableScale("tableA", "origin", scale)
            #     updateTableAffine("tableB", "origin", affine_para)
            # elif oracle == ORACLE.PointAdding:
            #     updateTableAddingPoint("tableA", "origin")
            #     updateTableAddingPoint("tableB", "origin")
            # else:
            #     print(oracle)
            # executor.conn.commit()

            # # oracle: the validation of geometries before and after transforming is invarient
            # query = '''SELECT COUNT(*) FROM tableA; SELECT COUNT(*) FROM tableB; 
            # '''
            # res = []
            # executor.execute(query, res)
            
            # log.write_result("--" + str(res))
            # for row in res:
            #     if row[0] == False:
            #         log.write_result("Error in Valid check!")
            #         exit(0)
            
        rqg = RandomQueryGenerator(["origin", "tableA", "tableB"])

        # if oracle == ORACLE.Dimensions:
        #     # oracle: geometry relations is invarient between before and after transforming
        #     rqg.createQueryDimension(scale)
        
        # oracle: geometry relations is invarient between before and after adding point.
        rqg.createQueryRelation(tu.relation)
        

        executor.executeSelect(rqg.query_pair[0], rqg.errors)
        res1 = executor.rows
        executor.executeSelect(rqg.query_pair[1], rqg.errors)
        res2 = executor.rows

        if compareResult(res1, res2) == False:
            log.write_result("Error in geometry relations")
            
            exit(0)

        
   

        


if __name__ == '__main__':

    for i in range(1, 10000):
        random.seed(i)
        log = Log(i)
        executor = Executor(log)
        main()
        
    executor.close()     
    