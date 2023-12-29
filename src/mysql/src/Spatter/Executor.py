import mysql.connector
from mysql.connector import Error
import Log

class Executor():
    def __init__(self, log) -> None:
        self.db_params = {
            'host': "localhost",
            # 'database': "nyc",
            'user': "root",
        }
        self.conn = mysql.connector.connect(**self.db_params)
        self.log: Log.Log = log
        self.rows = []
        
    def executeInsert(self, query: str, errors) -> int:
        self.conn.commit()
        self.log.write_result(' '.join(query.split('\n')))
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)

            self.log.write_result("--" + str(cursor.rowcount))
            print(cursor.rowcount)
            num = int(cursor.rowcount)
            return num
        
        except Error as e:
            self.log.write_error(f"Error: {e}")
            if str(e).split('\n')[0] not in errors:
                print(str(e).split('\n')[0])
                # print(errors)
                exit(0)
            return 0

    def executeSelect(self, query: str, errors):
        self.conn.commit()
        self.log.write_result(' '.join(query.split('\n')))
        try:
            cursor = self.conn.cursor()
            cursor.execute('EXPLAIN ' + query)
            self.rows = cursor.fetchall()
            self.log.write_result('--' + str(self.rows))
            if self.rows[0][3] == 'range':
                exit(0)

            cursor.execute(query)
            self.rows = cursor.fetchall()
            self.log.write_result('--' + str(self.rows))
        except Exception as e:
            
            self.log.write_error(f"Database error: {e}\n")
            for error in errors:
                if error in str(e):
                    self.conn = mysql.connector.connect(**self.db_params)
                    print("reconnet")
                    break
                else:
                    print(self.error)
                    print(str(e).split('\n')[0])
                    exit(0)

            
            
    def execute(self, query: str) -> bool:
        
        self.log.write_result(' '.join(query.split('\n')))
        try:    
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.rows = cursor.fetchall()

            self.log.write_result("--" + str(self.rows))
            cursor.close()
            self.conn.commit()

        except Exception as e:
            self.log.write_error(f"Database error: {e}\n")
            if str(e).split('\n')[0] not in self.error:
                print(self.error)
                print(str(e).split('\n')[0])
                exit(0)
            self.conn = mysql.connector.connect(**self.db_params)
            print("reconnet")
            
            return False
        
        return True
    
    def close(self):
        self.conn.commit()
        self.conn.close()