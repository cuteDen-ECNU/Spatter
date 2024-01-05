import random

from Spatter.InsertGenerator import *
from Spatter.Timer import *
from Spatter.Executor import *
from Spatter.Log import *
from Spatter.RandomQueryGenerator import *
from Spatter.TableUpdator import *
from Spatter.Configure import *
from Spatter.QueriesReduce import *

class INDEXTYPE(enum.Enum):
    #  BTREE = enum.auto()
    #  HASH  = enum.auto()
     GIST  = enum.auto()
    #  GIN   = enum.auto()


class Spatter():
    def __init__(self, i) -> None:
        self.log:Log = Log(i)
        self.executor = Executor(self.log)
        self.induce_num = 0
        self.spatter_time = None
      
    def CreateIndex(self, table: str):
        self.executor.Execute(f'''CREATE SPATIAL INDEX sp_index_geom ON {table}(geom);''')

    def CreateTable(self, table: str):
        self.executor.Execute(f'''DROP TABLE IF EXISTS {table}; ''')
        self.executor.Execute(f'''CREATE TABLE {table} (id int, geom geometry NOT NULL srid 0, valid boolean, gRelate int);''')
    
    def RemoveEmpty(self, table: str):
        self.executor.Execute(f'''DELETE FROM {table} As a1 WHERE ST_IsEmpty(a1.geom) ; ''')

    def CompareResult(self, rows1, rows2) -> bool:
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

        self.executor.Execute('''USE nyc;''')
        
        self.CreateTable("t0")
        self.CreateIndex("t0")

        self.CreateTable("t1")
        self.CreateIndex("t1")
        
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

        insertorError = InsertorError()
        i = 0
        while(i < smart_n):
            insert_func = random.choice(insert_type)
            if insert_func == InsertGenerator.InsertType.GeometryN:
                query = InsertGenerator.insertGeometryN("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Polygon:
                query = InsertGenerator.insertPolygon("t0", random_n + i)
                insertorError.usePolygon()
                print(insertorError.errors)
            elif insert_func == InsertGenerator.InsertType.GeomCollection:
                query = InsertGenerator.insertGeomCollection("t0", random_n + i)
            elif insert_func == InsertGenerator.InsertType.Collect:
                query = InsertGenerator.insertCollect("t0", random_n + i)
            
            else:
                print(insert_func)
            self.executor.ExecuteInsert(query, insertorError.errors)
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
            if tu.relation[t] == ORACLE.GeomCollection:
                query = tu.updateTableCollect(t)
            elif tu.relation[t] == ORACLE.Difference:
                query = tu.updateTableDifference(t)
            elif tu.relation[t] == ORACLE.SwapXY:
                query = tu.updateTableSwapXY(t)
            else:
                print(tu.relation[t])
                exit(-1)
            self.executor.Execute(query)
            
            if tu.relation[t] in [ORACLE.GeomCollection]: 
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

            self.executor.ExecuteSelect(randomQueryGenerator.query_pair[1], randomQueryGenerator.errors)
            res2 = self.executor.rows

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

            
   

        
