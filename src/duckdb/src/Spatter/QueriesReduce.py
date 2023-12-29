import copy
import enum
import re
from Executor import *
from Log import *
from RandomQueryGenerator import *


class CauseType(enum.Enum):
    SingleQuery = enum.auto()
    GEOSOverlaps = enum.auto()
    InvalidInput = enum.auto()
    TopologyException = enum.auto()


class QueriesReducor:
    def __init__(self, executor: Executor, reduce_file_path) -> None:
        self.origin_queries = []
        self.insert_queries = []
        self.executor = executor
        self.file_path = reduce_file_path
        self.query1 = ""
        self.query2 = ""
        self.table_index = {}
        self.cause_type = None
        self.errors = None

    def SetErrors(self, errors):
        self.errors = errors
    
    def Reduce(self, rqs: RandomQueryGenerator = None):

        self.query1 = ' '.join(rqs.query_pair[0].split('\n'))
        self.query2 = ' '.join(rqs.query_pair[1].split('\n'))
        
        self.GetAllQueries()
        self.executor.log.WriteResult("Get all queries.", True)
        
        if self.IsKownIssue(self.query1, self.query2):
            self.executor.log.WriteResult("Caused by kown issue.", True)
            return
        
        self.executor.log.ChangeFilePath(self.executor.log.name + '-reduce')
        reduce_queries = self.DetaDebugging() + [self.query1, self.query2]
        self.executor.log.ChangeFilePath(self.executor.log.name + '-reduce-result')
        self.executor.log.WriteResult(''.join(reduce_queries))
        self.executor.log.ChangeFilePath(self.executor.log.name)
        

    def IsKownIssue(self, o1: str, o2: str):
        
        table1 = re.findall(r'\bFROM ([A-Za-z_]+) As\b', o1)[0]
        table2 = re.findall(r'\bFROM ([A-Za-z_]+) As\b', o2)[0]
        
        query1 = o1.replace('COUNT(*)', 'a1.id, a2.id').replace(';', ' ORDER BY a1.id, a2.id;')
        query2 = o2.replace('COUNT(*)', 'a1.id, a2.id').replace(';', ' ORDER BY a1.id, a2.id;')
        
        self.executor.executeSelect(query1, self.errors)
        rows1 = self.executor.rows

        if self.executor.error != None:
           self.cause_type = self.InnerErrorToType(self.executor.error)
 
           return True

        self.executor.executeSelect(query2, self.errors)
        rows2 = self.executor.rows

        if self.executor.error != None:
           self.cause_type = self.InnerErrorToType(self.executor.error)
           return True

        set1 = set(rows1)
        set2 = set(rows2)
        

        if len(rows1)> len(rows2):
            dif_rows = set1.difference(set2)
        else:
            dif_rows = set2.difference(set1)

        self.executor.log.WriteResult(dif_rows, True)
        
        func = o1.split('ON')[1].split('WHERE')[0]
        self.executor.log.WriteResult(func, True)

        for dif_row in dif_rows:
            id1 = dif_row[0]
            id2 = dif_row[1]

            simple1 = f'''SELECT {func} FROM {table1} as a1, {table1} as a2 WHERE a1.id = {id1} and a2.id = {id2};'''
            simple2 = f'''SELECT {func} FROM {table2} as a1, {table2} as a2 WHERE a1.id = {id1} and a2.id = {id2};'''

            self.executor.executeSelect(simple1, self.errors)
            
            if self.executor.error != None:
                self.executor.log.WriteResult(f'Difference in a1.id = {id1} and a2.id = {id2} is caused by single query', True)
                continue
                
            rows1 = self.executor.rows

            self.executor.executeSelect(simple2, self.errors)
            
            if self.executor.error != None:
                self.executor.log.WriteResult(f'Difference in a1.id = {id1} and a2.id = {id2} is caused by single query', True)
                continue
            
            rows2 = self.executor.rows

            if rows1 == rows2: 
                return False
            else:
                self.executor.log.WriteResult(f'Difference in a1.id = {id1} and a2.id = {id2} is caused by single query', True)

        self.cause_type = CauseType.SingleQuery
        return True

    def GetAllQueries(self):
        with open(self.file_path) as of:
            line = of.readline()
            while(line):
                if line.startswith('SELECT'):
                    line = of.readline()
                    continue
                if line[0] != '-' and line != '\n':
                    self.origin_queries.append(line)
                if line.startswith('INSERT INTO origin'):
                    self.insert_queries.append(line)
                
                line = of.readline()



    def DetaDebugging(self):
        self.executor.log.WriteResult("Deta debugging begins...", True)
        ql = len(self.insert_queries)
        
        i = ql // 2
        
        current_queries = copy.deepcopy(self.origin_queries)

        while(i >= 1):
            
            l = list(range(0, len(self.insert_queries), i))
            remove_insert = []
            self.executor.log.WriteResult(l, True)
            for e in l:
                start = e; end = min(e + i, len(self.insert_queries) - 1)
                execute_queries = copy.deepcopy(current_queries)
                for j in range(start, end):
                    
                    execute_queries.remove(self.insert_queries[j])
                
                self.ExecuteQueries(execute_queries)
                del_suc = self.TestCondition()

                if del_suc:
                    self.executor.log.WriteResult('start:' + str(start) + ' end:' + str(end) + f', delete success: {del_suc}', True)
                    current_queries = copy.deepcopy(execute_queries)
                    remove_insert += list(range(start, end))
                else:
                    self.executor.log.WriteResult('start:' + str(start) + ' end:' + str(end) + f', delete success: {del_suc}', True)

            if len(remove_insert) == 0:   
                i = i // 2
            else:
                new_insert = []
                for i in range(len(self.insert_queries)):
                    if i not in remove_insert:
                        new_insert.append(self.insert_queries[i])
                self.insert_queries = new_insert
                i = len(self.insert_queries) // 2
        
        self.executor.log.WriteResult('\n'.join(current_queries), True)
        return current_queries
    
    def ExecuteQueries(self, queries):
        # insert_errors = ['Line has no points', 'First argument must be a LINESTRING']
        # select_errors = ["This function only accepts LINESTRING as arguments.", 'TopologyException']
        for q in queries:
            if q.startswith('SELECT'):
                self.executor.executeSelect(q, self.errors)
            elif q.startswith('INSERT'):
                self.executor.executeInsert(q, self.errors)
            else:
                self.executor.execute(q)
        

    def TestCondition(self):
        self.executor.executeSelect(self.query1)
        rows1 = self.executor.rows
        self.executor.executeSelect(self.query2)
        rows2 = self.executor.rows
        if rows1 == rows2:
            return False
        else:
            return True     

    def InnerErrorToType(self, error):
        if error == 'GEOSOverlaps':
            return CauseType.GEOSOverlaps
        elif 'Invalid Input Error' in error:
            return CauseType.InvalidInput
        elif error == 'TopologyException':
            return CauseType.TopologyException
        else:
            print(f"Unkown InnerErrorToType: {error}")
            exit(0)


# log = Log(0)
# executor = Executor(log)
# qr = QueriesReducor(log, "script/test.sql")
# origin_queries = []
# with open("script/test.sql") as of:
#     line = of.readline()
#     while(line):
#         if line[0] != '-' and line != '\n':
#             origin_queries.append(line)
        
#         line = of.readline()
# qr.ExecuteQueries(origin_queries)
# # qr.DetaDebugging()
# # executor = Executor(log)

# # executor.execute('DROP TABLE IF EXISTS tableB;  ')
# # executor.execute('CREATE TABLE tableB (id int, valid boolean, gRelate int); ')
# executor.execute('DROP TABLE IF EXISTS tableB; ')
