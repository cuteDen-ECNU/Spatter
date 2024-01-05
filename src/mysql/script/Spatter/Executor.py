
from Spatter.Log import *
from Spatter.Timer import *

import mysql.connector

class Executor():
    def __init__(self, log) -> None:
        self.db_params = {
            'host': "localhost",
            'database': "nyc",
            'user': "root",
        }
        self.conn = mysql.connector.connect(**self.db_params)
        self.log: Log = log
        self.rows = []
        self.exe_time = 0
        self.error_list = []
        
    def ExecuteInsert(self, query: str, errors) -> int:
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)

            self.log.WriteResult(cursor.rowcount, True)
            self.insert_num = int(cursor.rowcount)
        
        except mysql.connector.Error as e:
            self.log.WriteError(f"ExecuteInsert error:: {e}")
            for error in errors:
                e_first_line = str(e).split('\n')[0]
                if (error in str(e)) or (e_first_line in error):
                    self.connect()
                    self.error = error
                    break
            if self.error == None:
                print(e)
                exit(-1)
            self.insert_num = 0
        
        exe_time = timer.end()
        self.exe_time += exe_time
        
        self.log.WriteResult(exe_time, True)

    def ExecuteSelect(self, query: str, errors):
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.rows = cursor.fetchall()
            self.log.WriteResult(str(self.rows), True)

        except mysql.connector.Error as e:
            
            self.log.WriteError(f"ExecuteSelect error: {e}\n")
            for error in errors:
                if error in str(e):
                    self.error = error
                    self.connect()
                    break
            if self.error == None:
                print(e)
                exit(-1)

        exe_time = timer.end()
        self.exe_time += exe_time
        self.log.WriteResult(exe_time, True)


    def ExecuteUpdate(self, query: str, errors = None):
        self.clear()
        query_list = query.split(";")
        query_list = [item for item in query_list if item != ""]
        timer = Timer()
        for query in query_list:
            self.log.WriteResult(' '.join(query.split('\n')) + ';')
            try:    
                cursor = self.conn.cursor()
                cursor.execute(query)
                self.log.WriteResult(cursor.rowcount, True)
            except mysql.connector.Error as e:
                self.error_occur = True
                self.log.WriteError(f"executeSelect error: {e}\n")
                for error in errors:
                    e_first_line = str(e).split('\n')[0]
                    if (error in str(e)) or (e_first_line in error):
                        self.connect()
                        self.error = error
                        break
                if self.error == None:
                    print(e)
                    exit(0)  
        exe_time = timer.end()
        self.exe_time += exe_time
        
        self.log.WriteResult(exe_time, True)
        
                     
            
    def Execute(self, query: str) -> bool:
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)


        except mysql.connector.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            for error in self.error_list:
                e_first_line = str(e).split('\n')[0]
                if (error in str(e)) or (e_first_line in error):
                    self.connect()
                    self.error = error
                    break
            if self.error == None:
                print(e)
                exit(-1)
        exe_time = timer.end()
        self.exe_time += exe_time
        
        self.log.WriteResult(exe_time, True)
        

    def ExecuteQueries(self, queries, errors):
        for q in queries:
            if q.startswith('SELECT'):
                self.ExecuteSelect(q, errors)
            elif q.startswith('INSERT'):
                self.ExecuteInsert(q, errors)
            elif q.startswith('UPDATE'):
                self.ExecuteUpdate(q, errors)
            else:
                self.Execute(q)

    def connect(self):
        while(1):
            try:
                self.conn = mysql.connector.connect(**self.db_params)
                break
            except mysql.connector.Error as e:
                print(e)
    

    def close(self):
        self.conn.commit()
        self.conn.close()
    
    def clear(self):
        self.conn.commit()
        self.error = None
        self.rows = None
        self.insert_num = None
    