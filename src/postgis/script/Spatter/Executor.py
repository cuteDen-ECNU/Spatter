import time
import psycopg2
from Spatter.Log import *
from Spatter.Timer import *

class Executor():
    def __init__(self, log) -> None:
        self.db_params = {
            'host': "localhost",
            'port': "5432",
            'database': "nyc",
            'user': "postgres",
        }
        self.connect()
        self.log: Log = log
        self.rows = []
        self.error = None
        self.error_list = ['TopologyException', 'extension "postgis" does not exist', 'table "t" does not exist']
        self.insert_num = None

        self.exe_time = 0
        
    def ExecuteInsert(self, query: str, errors) -> int:
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()
        try:    
            cursor = self.conn.cursor()
            
            cursor.execute(query)
            
            self.log.WriteResult(cursor.statusmessage, True)
            self.insert_num = int(cursor.statusmessage.split(' ')[2])
        
        except psycopg2.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            
            if 'abnormally' in str(e):
                print("ExecuteInsert abnormally")
                self.error = "crash"
                self.check_recovery_status()
                self.log.WriteResult("ExecuteInsert check_recovery_status end", True)
                self.insert_num = 0
                return 
            
            for error in errors:
                e_first_line = str(e).split('\n')[0]
                if (error in str(e)) or (e_first_line in error):
                    self.connect()
                    self.error = error
                    break
            if self.error == None:
                print(e)
                print(errors)
                exit(-1)

            self.insert_num = 0
        
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
        
                self.log.WriteResult(cursor.statusmessage, True)
            except psycopg2.Error as e:
                self.log.WriteError(f"Database error: {e}\n")
                if 'abnormally' in str(e):
                    print("ExecuteUpdate abnormally")
                    self.error = "crash"
                    self.check_recovery_status()
                    self.log.WriteResult("ExecuteUpdate check_recovery_status end", True)
                    return
                for error in errors:
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

    def ExecuteSelect(self, query: str, errors = None):
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            self.rows = cursor.fetchall()
            self.log.WriteResult(self.rows, True) 
            
        except psycopg2.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            if 'abnormally' in str(e):
                print("ExecuteSelect abnormally")
                self.error = "crash"
                self.check_recovery_status()
                self.log.WriteResult("ExecuteSelect check_recovery_status end", True)
                return
            for error in errors:
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

    def Execute(self, query: str) -> bool:
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()

        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()

        except psycopg2.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            if 'abnormally' in str(e):
                print("Execute abnormally")
                self.error = "crash"
                self.check_recovery_status()
                self.log.WriteResult("Execute check_recovery_status end", True)
                return
            self.log.WriteResult(self.error_list, True)
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
        self.log.WriteResult(cursor.statusmessage, True)

    
    def ExecuteQueries(self, queries, errors):
        for q in queries:
            q = q.strip()
            if len(q) <= 1: continue
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
                self.conn = psycopg2.connect(**self.db_params)
                self.conn.autocommit = True
                break
            except psycopg2.Error as e:
                print(e)

    def check_recovery_status(self):
        self.connect()
        cursor = self.conn.cursor()
        
        while True:
            print("SELECT pg_is_in_recovery();")
            cursor.execute("SELECT pg_is_in_recovery();")
            recovery_status = cursor.fetchone()[0]
            print(f"recovery_status = {recovery_status}")
            if recovery_status:
                print("Database still in recovery mode. Sleeping for 1 second...")
                time.sleep(1)
            else:
                print("Database is no longer in recovery mode.")
                break    

    def close(self):
        self.conn.commit()
        self.conn.close()

    def clear(self):
        self.error = None
        self.rows = None
        self.insert_num = None



        