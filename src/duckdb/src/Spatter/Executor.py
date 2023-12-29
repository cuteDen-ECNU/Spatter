import duckdb
import Log

class Executor():
    def __init__(self, log) -> None:
        self.c = {
            'allow_unsigned_extensions' : True
        }
        self.conn = duckdb.connect(database=':memory:', config = self.c)


        self.conn.execute("FORCE INSTALL spatial FROM 'http://nightly-extensions.duckdb.org';")
        self.conn.execute("LOAD spatial;")
        self.log: Log.Log = log
        self.rows = []
        self.error_occur = False
        self.error_list = []
        self.error = None
        
    def executeInsert(self, query: str, errors) -> int:
        self.conn.commit()
        self.log.WriteResult(' '.join(query.split('\n')))
        self.error = None
        try:    
            self.conn.execute(query)
            self.rows = self.conn.fetchall()
            self.log.WriteResult(str(self.rows), True)
            num = int(self.rows[0][0])
            return num
        except duckdb.Error as e:
            self.log.WriteError(f"executeInsert error: {e}\n")
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
            return 0

    def executeSelect(self, query: str, errors):
        self.log.WriteResult(' '.join(query.split('\n')))
        self.error = None
        
        try:    
            self.conn.execute(query)
            self.rows = self.conn.fetchall()
            self.log.WriteResult(str(self.rows), True)
        except duckdb.Error as e:
            self.error_occur = True
            self.log.WriteError(f"executeSelect error: {e}\n")
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

            
            
    def execute(self, query: str) -> bool:
        self.log.WriteResult(' '.join(query.split('\n')))
        self.error = None
        try:    
            self.conn.execute(query)

            # self.rows = self.conn.fetchall()
            # self.log.WriteResult(str(self.rows), True)
        except duckdb.Error as e:
            self.error_occur = True
            self.log.WriteError(f"execute error: {e}\n")
            for error in self.errors:
                if error in str(e):
                    self.connect()
                    self.error = error
                    print("reconnet")
                    break
                else:
                    print(str(e).split('\n')[0])
                    exit(0)

    def connect(self):
        self.conn = duckdb.connect(database=':memory:', config = self.c)
        # self.conn.autocommit = True
        
    def close(self):
        self.conn.commit()
        self.conn.close()