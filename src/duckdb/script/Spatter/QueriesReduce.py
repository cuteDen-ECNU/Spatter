import copy
import json
import re
import os

from Spatter.Executor import *
from Spatter.Log import *
from Spatter.RandomQueryGenerator import *
from Spatter.InsertGenerator import *

class CauseType(enum.Enum):
    SingleQuery = enum.auto()
    GEOSOverlaps = enum.auto()
    OnlyAccept = enum.auto()
    TopologyException = enum.auto()
    Crash = enum.auto()


class QueriesReducor:
    def __init__(self, executor: Executor) -> None:
        self.t0_queries_list = []
        self.insert_queries_list = []
        self.executor = executor
        self.spatter_path = None
        self.query1 = ""
        self.query2 = ""
        self.table_index = {}
        self.cause_type = None
        self.errors = None
        # unknown issue id pair
        self.cdt_pair = [-1, -1]
        self.induce_num = 0

        self.induce_cases_dir = "/log/trigger-cases/"
        if not os.path.exists(self.induce_cases_dir):
            os.makedirs(self.induce_cases_dir)
        

    def SetErrors(self, errors):
        self.errors = errors
    
    def Reduce(self):

        self.executor.log.WriteResult("Get all queries.", True)
        
        if self.IsKownIssue():
            self.executor.log.WriteResult("Caused by kown issue.", True)
            return
        
        self.executor.log.ChangeFileName(self.executor.log.name + '-reduce')
        reduce_queries = self.DetaDebugging() + [self.query1, self.query2]
        self.executor.log.ChangeFileName(self.executor.log.name + '-reduce-result')
        self.executor.log.WriteResult('\n'.join(reduce_queries))

        self.executor.log.ChangeFileName(self.executor.log.name)
        

    def IsKownIssue(self):
        
        table1 = re.findall(r'\bFROM ([A-Za-z0-9_]+) As\b', self.query1)[0]
        table2 = re.findall(r'\bFROM ([A-Za-z0-9_]+) As\b', self.query2)[0]
        
        query1 = self.query1.replace('COUNT(*)', 'a1.id, a2.id').replace(';', ' ORDER BY a1.id, a2.id;')
        query2 = self.query2.replace('COUNT(*)', 'a1.id, a2.id').replace(';', ' ORDER BY a1.id, a2.id;')
        
        self.executor.ExecuteSelect(query1, self.errors)
        rows1 = self.executor.rows

        if self.executor.error != None:
           self.cause_type = self.InnerErrorToType(self.executor.error)
           self.executor.log.WriteResult(self.cause_type, True)
           return True

        self.executor.ExecuteSelect(query2, self.errors)
        rows2 = self.executor.rows

        if self.executor.error != None:
           self.cause_type = self.InnerErrorToType(self.executor.error)
           self.executor.log.WriteResult(self.cause_type, True)
           return True

        set0 = set(rows1)
        set2 = set(rows2)
        

        if len(rows1)> len(rows2):
            dif_rows = set0.difference(set2)
        else:
            dif_rows = set2.difference(set0)

        self.executor.log.WriteResult(dif_rows, True)
        
        func1 = query1.split('ON')[1].split('WHERE')[0]
        func2 = query2.split('ON')[1].split('WHERE')[0]

        for dif_row in dif_rows:
            id1 = dif_row[0]
            id2 = dif_row[1]

            simple1 = f'''SELECT {func1} FROM {table1} as a1, {table1} as a2 WHERE a1.id = {id1} and a2.id = {id2};'''
            simple2 = f'''SELECT {func2} FROM {table2} as a1, {table2} as a2 WHERE a1.id = {id1} and a2.id = {id2};'''

            self.executor.ExecuteSelect(simple1, self.errors)
            
            if self.executor.error != None:
                self.executor.log.WriteResult(f'Difference in a1.id = {id1} and a2.id = {id2} is caused by {self.executor.error}', True)
                continue
                
            rows1 = self.executor.rows

            self.executor.ExecuteSelect(simple2, self.errors)
            
            if self.executor.error != None:
                self.executor.log.WriteResult(f'Difference in a1.id = {id1} and a2.id = {id2} is caused by {self.executor.error}', True)
                continue
            
            rows2 = self.executor.rows

            if rows1 == rows2: 
                self.cdt_pair[0] = simple1
                self.cdt_pair[1] = simple2
                return False
            else:
                self.executor.log.WriteResult(f'Difference in a1.id = {id1} and a2.id = {id2} is caused by single query', True)
                self.executor.log.WriteResult(f'SELECT ST_AsText(geom) FROM t0 WHERE id = {id1} or id = {id2};', True)
                self.executor.log.WriteResult(f'SELECT ST_AsText(geom) FROM t1 WHERE id = {id1} or id = {id2};', True)

        self.cause_type = CauseType.SingleQuery

        
        return True

    def GetAllQueriesByDict(self, d):
        assert(len(self.t0_queries_list) == 0)
        self.query1 = d["query1"].strip()
        self.query2 = d["query2"].strip()
        t0_queries = d["t0_queries"].split(';')
        self.t0_queries_list = [q.strip() for q in t0_queries if q != '']
        for q in self.t0_queries_list:
            if q.startswith('INSERT INTO t0'):
                self.insert_queries_list.append(q)

    def GetAllQueriesByJson(self, json_path):
        assert(len(self.t0_queries_list) == 0)
        with open(json_path) as of:
            d = json.load(of)
        self.query1 = d["query1"].strip()
        self.query2 = d["query2"].strip()
        t0_queries = d["t0_queries"].split(';')
        self.t0_queries_list = [q.strip() + ';' for q in t0_queries if q != '']
        for q in self.t0_queries_list:
            if q.startswith('INSERT INTO t0'):
                self.insert_queries_list.append(q)
    
    def GetAllQueriesByline(self, spatter_path):
        assert(len(self.t0_queries_list) == 0)
        with open(spatter_path) as of:
            line = of.readline()
            while(line):
                if line.startswith('SELECT'):
                    self.query1, self.query2 = line.split(';')[0], line.split(';')[1]
                    line = of.readline()
                    continue
                if line[0] != '-' and line != '\n':
                    self.t0_queries_list.append(line)
                if line.startswith('INSERT INTO t0'):
                    self.insert_queries_list.append(line)
                
                line = of.readline()




    def DetaDebugging(self):
        self.executor.log.WriteResult("Deta debugging begins...", True)
        ql = len(self.insert_queries_list)
        
        i = ql // 2
        
        current_queries = copy.deepcopy(self.t0_queries_list)

        while(i >= 1):
            
            l = list(range(0, len(self.insert_queries_list), i))
            remove_insert = []
            self.executor.log.WriteResult(l, True)
            for e in l:
                start = e; end = min(e + i, len(self.insert_queries_list) - 1)
                execute_queries = copy.deepcopy(current_queries)
                for j in range(start, end):
                    
                    execute_queries.remove(self.insert_queries_list[j])
                
                self.ExecuteQueries(execute_queries)
                self.executor.log.WriteResult(f'start: {start}, end: {end},', True)
                del_suc = self.TestCondition()

                if del_suc:
                    self.executor.log.WriteResult(f'delete success: {del_suc}', True)
                    current_queries = copy.deepcopy(execute_queries)
                    remove_insert += list(range(start, end))
                else:
                    self.executor.log.WriteResult(f'delete success: {del_suc}', True)

            if len(remove_insert) == 0:   
                i = i // 2
            else:
                new_insert = []
                for i in range(len(self.insert_queries_list)):
                    if i not in remove_insert:
                        new_insert.append(self.insert_queries_list[i])
                self.insert_queries_list = new_insert
                i = len(self.insert_queries_list) // 2
        
        self.executor.log.WriteResult('\n'.join(current_queries), True)
        current_queries = [q+";" for q in current_queries if q != ""]
        return current_queries
    
    def ExecuteQueries(self, queries):
        # insert_errors = ['Line has no points', 'First argument must be a LINESTRING']
        # select_errors = ["This function only accepts LINESTRING as arguments.", 'TopologyException']
        for q in queries:
            if q == '': continue
            if q.startswith('SELECT'):
                self.executor.ExecuteSelect(q, self.errors)
            elif q.startswith('INSERT'):
                self.executor.ExecuteInsert(q, self.errors)
            elif q.startswith('UPDATE'):
                self.executor.ExecuteUpdate(q, self.errors)
            else:
                self.executor.Execute(q)
    
    def TestCdtPair(self):
        self.executor.ExecuteSelect(self.cdt_pair[0], self.errors)
        rows1 = self.executor.rows
        if(0 == len(rows1)):
            return False
        self.executor.ExecuteSelect(self.cdt_pair[1], self.errors)
        rows2 = self.executor.rows
        if(0 == len(rows2)):
            return False
        if rows1 == rows2:
            return True
        else:
            print(self.cdt_pair)
            exit(-1)

    def TestCondition(self):

        if self.TestCdtPair() == False:
            return False
        
        self.executor.ExecuteSelect(self.query1, self.errors)
        rows1 = self.executor.rows
        self.executor.ExecuteSelect(self.query2, self.errors)
        rows2 = self.executor.rows
        
        if rows1 == rows2:
            return False
        else:
            return True     

    def InnerErrorToType(self, error):
        if error == 'crash':
            return CauseType.Crash
        elif error == 'GEOSOverlaps':
            return CauseType.GEOSOverlaps
        elif 'only accepts' in error:
            return CauseType.OnlyAccept
        elif error == 'TopologyException':
            return CauseType.TopologyException
        else:
            print(f"Unkown InnerErrorToType: {error}")
            # exit(0)

