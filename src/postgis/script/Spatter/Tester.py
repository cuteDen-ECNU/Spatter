

import enum
import random
from Spatter.InsertGenerator import *
from Spatter.Executor import Executor
from Spatter.Log import Log
from Spatter.RandomQueryGenerator import RandomQueryGenerator
from Spatter.TableUpdator import TableUpdator, ORACLE
from Spatter.QueriesReduce import *
from Spatter.CoverageRecord import *
from Spatter.Configure import *

class INDEXTYPE(enum.Enum):
    BTREE = enum.auto()
    HASH  = enum.auto()
    GIST  = enum.auto()
    #  GIN   = enum.auto()


class IndexCreator():
    def __init__(self) -> None:
        self.table_index = {}
    
    def createIndex(self, table: str):
        index_type = random.choice(list(INDEXTYPE)).name
        query = f'''CREATE INDEX {table}_idx ON {table} USING {index_type} (geom);'''
        self.table_index[table] = index_type
        return query

class Spatter():
    def __init__(self, i) -> None:
        self.log:Log = Log(i)
        self.executor = Executor(self.log)
        self.induce_num = 0
        self.spatter_time = None

    def CreateTable(self, table: str):
        self.executor.Execute(f'''DROP TABLE IF EXISTS {table}; ''')
        self.executor.Execute(f'''CREATE TABLE {table} (id int, geom geometry, valid boolean);''')

    def RemoveEmpty(self, table: str):
        self.executor.Execute(f'''DELETE FROM {table} As a1 WHERE ST_IsEmpty(a1.geom) ; ''')

    def compareResult(self, rows1, rows2) -> bool:
        if (rows1 == None) and (rows2 == None):
            return True
        
        if (rows1 == None) or (rows2 == None):
            return False
        
        if len(rows1) != len(rows2):
            return False
        for i in range(0, len(rows1)):
            if len(rows1[i]) != len(rows2[i]):
                return False
            for j in range(0, len(rows1[i])):
                if rows1[i][j] != rows2[i][j]:
                    return False
        return True

    def Spatter(self, configure: Configure):
        self.spatter_time = Timer()
        
        self.log.WriteResult(json.dumps(configure.d), True)

        ic = IndexCreator()
        self.CreateTable("t0")
        query = ic.createIndex("t0")
        self.executor.Execute(query)

        self.CreateTable("t1")
        query = ic.createIndex("t1")
        self.executor.Execute(query)
        

        N = configure.GetGeometryNumber()
        if configure.GetSmartGeneratorOn() == True:
            random_n = N//3 + 1
            smart_n = N - random_n
        else:
            random_n = N
            smart_n = 0

        for i in range(0, random_n):
            query = RandomGenerator.insertRandomly("t0", i)
            self.executor.ExecuteInsert(query, None)

        insert_type = list(InsertGenerator.InsertType)

        insertErrorBox = InsertErrorBox()
        
        i = 0
        while(i < smart_n):
            insert_func = random.choices(insert_type, weights=list(InsertGenerator.insert_weights.values()), k = 1)[0]
            if insert_func == InsertGenerator.InsertType.GeometryN:
                query = InsertGenerator.insertGeometryN("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Polygonize:
                query = InsertGenerator.insertPolygonize("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Boundary:
                query = InsertGenerator.insertBoundary("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.BoundingDiagonal:
                query = InsertGenerator.insertBoundingDiagonal("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.CollectionExtract:
                query = InsertGenerator.insertCollectionExtract("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.SetPoint:
                query = InsertGenerator.insertSetPoint("t0", random_n + i)
                insertErrorBox.UseSetPoint()
            elif insert_func == InsertGenerator.InsertType.Dump:
                query = InsertGenerator.insertDump("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.DumpRings:
                query = InsertGenerator.insertDumpRings("t0", random_n + i)
                insertErrorBox.UseDumpRings()
            elif insert_func == InsertGenerator.InsertType.ConvexHull:
                query = InsertGenerator.insertConvexHull("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Collect0:
                query = InsertGenerator.insertCollect0("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Collect1:
                query = InsertGenerator.insertCollect1("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Collect2:
                query = InsertGenerator.insertCollect2("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Collect3:
                query = InsertGenerator.insertCollect0("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Scale:
                query = InsertGenerator.insertScale("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Normalize:
                query = InsertGenerator.insertNormalize("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Multi:
                query = InsertGenerator.insertMulti("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.CollectionHomogenize:
                query = InsertGenerator.insertCollectionHomogenize("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.ForceCollection:
                query = InsertGenerator.insertForceCollection("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Affine2D:
                query = InsertGenerator.insertAffine2D("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.PointOnSurface:
                query = InsertGenerator.insertPointOnSurface("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.RemoveRepeatedPoints:
                query = InsertGenerator.insertRemoveRepeatedPoints("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.FlipCoordinates:
                query = InsertGenerator.insertFlipCoordinates("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.ForcePolygonCCW:
                query = InsertGenerator.insertForcePolygonCCW("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.ForcePolygonCW:
                query = InsertGenerator.insertForcePolygonCW("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.NULL:
                query = InsertGenerator.insertNull("t0", random_n + i)
            else:
                print(insert_func)
                exit(-1)
            self.executor.ExecuteInsert(query, insertErrorBox.errors)
            i += self.executor.insert_num
            if self.executor.error == "crash":
                self.RecordCrash(query)
        
        if random.randint(0, 1) == 0:
            self.RemoveEmpty("t0")

        # invarient transform
        table_list = ["t1"]
        tu = TableUpdator(configure)
        tu.SelectOracle(table_list)
        
        query = tu.UpdateTableIsValid('t0')
        self.executor.ExecuteUpdate(query)   
        
        for t in table_list:
            query = InsertGenerator.insertFromExist(t, "t0")
            self.executor.ExecuteInsert(query, None)

        # Avoiding precision issues, rotation need scale. Thus, it is dealt first.
        if tu.update_first != None:
            t = tu.update_first
            if tu.relation[tu.update_first] == ORACLE.Affine3D:
                query = tu.updateTableAffine3D(t, "t0")
            elif tu.relation[tu.update_first] == ORACLE.Affine2D:
                query = tu.UpdateTableAffine2D(t, "t0")
            else:
                print(tu.relation[t])
                exit(-1)
            self.executor.ExecuteUpdate(query)

            query = tu.UpdateValidFromTable(t, "t0")
            self.executor.ExecuteUpdate(query)
            table_list.remove(t)


        for t in table_list:
            
            if tu.relation[t] == ORACLE.DoNothing:
                query = tu.UpdateTableIsValid(t)
                self.executor.ExecuteUpdate(query)
                continue
            elif tu.relation[t] == ORACLE.Normalize:
                query = tu.UpdateTableNormalize(t)
            elif tu.relation[t] == ORACLE.Collect:
                query = tu.UpdateTableCollect(t)
            elif tu.relation[t] == ORACLE.Multi:
                query = tu.UpdateTableMulti(t)
            elif tu.relation[t] == ORACLE.CollectionHomogenize:
                query = tu.UpdateTableCollectionHomogenize(t)
            elif tu.relation[t] == ORACLE.ForceCollection:
                query = tu.UpdateTableForceCollection(t)
            elif tu.relation[t] == ORACLE.PointOnSurface:
                query = tu.UpdateTablePointOnSurface(t)
            elif tu.relation[t] == ORACLE.RemoveRepeatedPoints:
                query = tu.UpdateTableRemoveRepeatedPoints(t)
            elif tu.relation[t] == ORACLE.FlipCoordinates:
                query = tu.UpdateTableFlipCoordinates(t)
            elif tu.relation[t] == ORACLE.ForcePolygonCCW:
                query = tu.UpdateTableForcePolygonCCW(t)
            elif tu.relation[t] == ORACLE.ForcePolygonCW:
                query = tu.UpdateTableForcePolygonCW(t)
            else:
                print(tu.relation[t])
                exit(-1)
            self.executor.ExecuteUpdate(query)
            if self.executor.error == "crash":
                self.RecordCrash(query)

            if tu.relation[t] in [ORACLE.ForceCollection
                                  , ORACLE.Collect
                                  , ORACLE.CollectionHomogenize]: 
                query = tu.UpdateValidFromTable(t, "t0")
            else:
                query = tu.UpdateTableIsValid(t)
            
            self.executor.ExecuteUpdate(query)
           
                
            
        tu.table_list.append("t0") 

        reduce = QueriesReducor(self.executor)
        reduce.GetAllQueriesByline(self.log.GetResultPath())

        for i in range(0, 100):
            randomQueryGenerator = RandomQueryGenerator(tu.table_list)
            randomQueryGenerator.createBoolPrediction(tu.relation)
            
            self.executor.ExecuteSelect(randomQueryGenerator.query_pair[0], randomQueryGenerator.errors)
            res1 = self.executor.rows
            if self.executor.error == "crash":
                self.RecordCrash(query)

            self.executor.ExecuteSelect(randomQueryGenerator.query_pair[1], randomQueryGenerator.errors)
            res2 = self.executor.rows
            if self.executor.error == "crash":
                self.RecordCrash(query)

            if self.compareResult(res1, res2) == False:
                self.log.WriteResult(f"Error in geometry relations: {res1}, {res2}.", note=True)
                
                d = {}
                d['query1'] = ' '.join(randomQueryGenerator.query_pair[0].split('\n'))
                d['res1'] = str(res1)
                d['query2'] = ' '.join(randomQueryGenerator.query_pair[1].split('\n'))
                d['res2'] = str(res2)
                d['t0_queries'] = ' '.join(' '.join(reduce.t0_queries_list).split('\n'))
                file_name = time.strftime(f"%Y-%m-%d-%H:%M:%S-" + str(self.induce_num), time.localtime())
                file_path = os.path.join(reduce.induce_cases_dir, file_name)
                with open(file_path, 'w') as of:
                    json.dump(d, of)
                self.induce_num += 1

                # reduce.SetErrors(insertErrorBox.errors + randomQueryGenerator.errors)
                # reduce.Reduce(randomQueryGenerator.query_pair[0], randomQueryGenerator.query_pair[1])

                # if reduce.cause_type == None:
                #     self.log.WriteResult("reduce.cause_type == None", note=True)
                    # exit(0)

        self.log.WriteResult(self.executor.exe_time, True)
        self.log.WriteResult(self.spatter_time.end(), True)

    def RecordCrash(self, crash_query):
        reduce = QueriesReducor(self.executor)
        reduce.GetAllQueriesByline(self.log.GetResultPath())
        d = {}
        d['t0_queries'] = ' '.join(' '.join(reduce.t0_queries_list[:-1]).split('\n'))
        d['crash'] = crash_query
        file_name = time.strftime(f"%Y-%m-%d-%H:%M:%S-crash-" + str(self.induce_num), time.localtime())
        file_path = os.path.join(reduce.induce_cases_dir, file_name)
        with open(file_path, 'w') as of:
            json.dump(d, of)
        self.induce_num += 1

