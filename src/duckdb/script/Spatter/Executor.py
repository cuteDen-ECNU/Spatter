import duckdb
from Spatter.Log import *
from Spatter.Timer import *

class Executor():
    def __init__(self, log) -> None:
        self.c = {
            'allow_unsigned_extensions' : True
        }
        self.db = '/log/spatter.db'
        self.conn = duckdb.connect(database=self.db, config = self.c)


        self.conn.execute("INSTALL 'duckdb_spatial/build/debug/extension/spatial/spatial.duckdb_extension';")
        self.conn.execute("LOAD spatial;")
        self.log: Log = log
        self.rows = []
        self.error_occur = False
        self.error_list = []
        self.error = None
        self.insert_num = None
        self.exe_time = 0
        
    def ExecuteInsert(self, query: str, errors) -> int:
        self.clear()
        self.log.WriteResult(' '.join(query.split('\n')))
        timer = Timer()
        try:    
            self.conn.execute(query)
            self.rows = self.conn.fetchall()
            
            self.log.WriteResult(str(self.rows), True)
            self.insert_num = int(self.rows[0][0])
        
        except duckdb.Error as e:
            self.log.WriteError(f"ExecuteInsert error: {e}\n")
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
            self.conn.execute(query)
            self.rows = self.conn.fetchall()
            self.log.WriteResult(str(self.rows), True)
        
        except duckdb.Error as e:
            self.log.WriteError(f"ExecuteSelect error: {e}\n")
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

    
    def ExecuteUpdate(self, query: str, errors = None):
        self.clear()
        query_list = [item for item in query.split(";") if item.strip() != ""]
        timer = Timer()
        for query in query_list:
            self.log.WriteResult(' '.join(query.split('\n')) + ';')
            try:    
                self.conn.execute(query)
                self.rows = self.conn.fetchall()
                self.log.WriteResult(str(self.rows), True)
            except duckdb.Error as e:
                self.error_occur = True
                self.log.WriteError(f"ExecuteUpdate error: {e}\n")
                for error in errors:
                    e_first_line = str(e).split('\n')[0]
                    if (error in str(e)) or (e_first_line in error):
                        self.connect()
                        print("reconnet")
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
            self.conn.execute(query)

            # self.rows = self.conn.fetchall()
            # self.log.WriteResult(str(self.rows), True)
        except duckdb.Error as e:
            self.log.WriteError(f"execute error: {e}\n")
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
                self.conn = duckdb.connect(database=self.db, config = self.c)
                break
            except duckdb.Error as e:
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
        self.conn.commit()
        self.error = None
        self.rows = None
        self.insert_num = None


