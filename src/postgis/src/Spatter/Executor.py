import pdb
from time import sleep
import time
import psycopg2
from Spatter.Log import *

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
        self.error_list = ['TopologyException']
        
    def ExecuteInsert(self, query: str, errors) -> int:
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.log.WriteResult(cursor.statusmessage, True)
            num = int(cursor.statusmessage.split(' ')[2])
            return num
        except psycopg2.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            if 'abnormally' in str(e):
                print("ExecuteInsert abnormally")
                self.check_recovery_status()
                self.log.WriteResult("ExecuteInsert check_recovery_status end", True)
                self.error = "crash"
                return 0
            if str(e).split('\n')[0] not in errors:
                print(str(e).split('\n')[0])
                print(errors)
                # exit(0)
            self.connect()

            return 0

    def ExecuteUpdate(self, query: str, errors = None):
        self.clear()
        query_list = query.split(";")
        query_list = [item for item in query_list if item != ""]
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
                    self.check_recovery_status()
                    self.error = "crash"
                    print("return")
                    return
                if str(e).split('\n')[0] not in errors:
                    print(str(e).split('\n')[0])
                    print(errors)
                    # exit(0)
                self.connect()    

    def ExecuteSelect(self, query: str, errors = None):
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.rows = cursor.fetchall()
            self.log.WriteResult(str(self.rows), True)
            
        except psycopg2.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            if 'abnormally' in str(e):
                print("ExecuteSelect abnormally")
                self.check_recovery_status()
                self.error = "crash"
                return
            for error in errors:
                e_first_line = str(e).split('\n')[0]
                if (error in str(e)) or (e_first_line in error):
                    self.connect()
                    self.error = error
                    break
            if self.error == None:
                print(e)

    def Execute(self, query: str) -> bool:
        self.conn.commit()
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.log.WriteResult(cursor.statusmessage, True)

        except psycopg2.Error as e:
            self.log.WriteError(f"Database error: {e}\n")
            if 'abnormally' in str(e):
                print("Execute abnormally")
                self.check_recovery_status()
                self.error = "crash"
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
                # exit(0)
            
            return False
        cursor.close()
        return True
    
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