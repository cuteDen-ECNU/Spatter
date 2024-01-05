
import random

from Spatter.InsertGenerator import *
from Spatter.Executor import *
from Spatter.Log import *
from Spatter.RandomQueryGenerator import RandomQueryGenerator
from Spatter.TableUpdator import ORACLE, TableUpdator
from Spatter.QueriesReduce import *
from Spatter.Configure import *
from Spatter.Timer import *


class Spatter():
    def __init__(self, i) -> None:
        self.log:Log = Log(i)
        self.executor = Executor(self.log)
        self.induce_num = 0
        self.spatter_time = None

    def CreateTable(self, table: str):
        self.executor.Execute(f'''DROP TABLE IF EXISTS {table}; ''')
        self.executor.Execute(f'''CREATE TABLE {table} (id int, geom geometry, valid boolean, gRelate int);''')

    def RemoveEmpty(self, table: str):
        self.executor.Execute(f'''DELETE FROM {table} As a1 WHERE ST_IsEmpty(a1.geom) ; ''')

    def CompareResult(self, rows1, rows2) -> bool:
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
        self.log.WriteResult(json.dumps(configure.d), True)
        self.spatter_time = Timer()

        # create transform-based tables
        self.CreateTable("t0")
        self.CreateTable("t1")
        

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
            insert_func = random.choice(insert_type)
            if insert_func == InsertGenerator.InsertType.Boundary:
                query = InsertGenerator.insertBoundary("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.CollectionExtract:
                query = InsertGenerator.insertCollectionExtract("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.ConvexHull:
                query = InsertGenerator.insertConvexHull("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Collect:
                query = InsertGenerator.insertCollect("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Normalize:
                query = InsertGenerator.insertNormalize("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.MakeLine:
                query = InsertGenerator.insertMakeLine("t0", random_n + i)
                insertErrorBox.useMakeLine()
            else:
                print(insert_func)
                exit(-1)
            self.executor.ExecuteInsert(query, insertErrorBox.errors)
            i += self.executor.insert_num

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
            
        for t in table_list:
            if tu.relation[t] == ORACLE.DoNothing:
                query = tu.UpdateTableIsValid(t)
                self.executor.ExecuteUpdate(query)
                continue
            elif tu.relation[t] == ORACLE.PointOnSurface:
                query = tu.updateTablePointOnSurface(t)
            elif tu.relation[t] == ORACLE.Normalize:
                query = tu.updateTableNormalize(t)
            elif tu.relation[t] == ORACLE.FlipCoordinates:
                query = tu.updateTableFlipCoordinates(t)
            elif tu.relation[t] == ORACLE.Collect:
                query = tu.updateTableCollect(t)

            else:
                print(tu.relation[t])
                exit(-1)
            self.executor.Execute(query)
            if self.executor.error == "crash":
                self.RecordCrash(query)     
            
            if tu.relation[t] in [ORACLE.Collect]: 
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

            if self.CompareResult(res1, res2) == False:
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
        

 