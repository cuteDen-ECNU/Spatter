from Executor import Executor
from Log import Log
import re


log: Log = Log(0)
executor: Executor = Executor(log)

def TestCondition():
    query = '''SELECT COUNT(*) FROM table As a1 RIGHT OUTER JOIN table As a2 ON ST_Disjoint(a1.geom, a2.geom) WHERE a1.id <> a2.id;'''
    query1 = query.replace('table', 't1')
    query2 = query.replace('table', 't2')
    executor.execute(query1)
    rows1 = executor.rows
    executor.execute(query2)
    rows2 = executor.rows
    if rows1 == rows2:
        return False
    else:
        return True

def DropData(query):
    query1 = query.replace('table', 't1')
    query2 = query.replace('table', 't2')
    executor.execute(query1)
    executor.execute(query2)


def CreateTemp():   
    executor.execute('DROP table IF EXISTS temp1;')
    executor.execute('CREATE table temp1 SELECT * FROM t1;')
    executor.execute('DROP table IF EXISTS temp2;')
    executor.execute('CREATE table temp2 SELECT * FROM t2;')

def RecoverTemp():
    executor.execute('DROP table IF EXISTS t1;')
    executor.execute('DROP table IF EXISTS t2;')
    executor.execute('CREATE table t1 SELECT * FROM temp1;')
    executor.execute('CREATE table t2 SELECT * FROM temp2;')

def SortTable():
    CreateTemp()
    
    executor.execute(f'''TRUNCATE TABLE t1;''')
    executor.execute(f'''TRUNCATE TABLE t2;''')
    # executor.execute(f'''create spatial index spidx2 on t2(geom);''')
    executor.execute(f'''SET @row_number = 0;''')
    executor.execute(f'''INSERT INTO t1 (id, geom)
                        SELECT @row_number:=@row_number+1 AS id, geom FROM temp1;
                        ''')
    executor.execute(f'''SET @row_number = 0;''')
    executor.execute(f'''INSERT INTO t2 (id, geom)
                        SELECT @row_number:=@row_number+1 AS id, geom FROM temp2;
                        ''')
    

def delta_debugging():
    executor.execute('''SELECT COUNT(*) FROM t1;''')
    tl = executor.rows[0][0]
    print(tl)

    dquery = '''DELETE FROM table As a1 WHERE '''
    i = tl//2 
    while(i >= 2):
        l = list(range(0, tl, i))
        flag = False
        
        CreateTemp()
        for e in l:
            start = e; end = e + i
            print('start:' + str(start) + ' end:' + str(end))
            DropData(dquery + f'''a1.id >= {start} and a1.id < {end} ;''')
            if TestCondition():
                flag = True
                CreateTemp()
                
            else:
                RecoverTemp()
                
        
        if flag == True:
            print('return true')
            return True
        i //= 2
    return False



def main():
    origin1 = '''
SELECT COUNT(*)         FROM tableA As a1          JOIN tableA As a2 FORCE INDEX (sp_index_geom)         ON ST_Contains(a1.geom, a2.geom)          WHERE  a1.valid = True and a2.valid = True and a1.id <> a2.id;
    '''
    origin2 = '''
SELECT COUNT(*)         FROM origin As a1          JOIN origin As a2          ON ST_Contains(a1.geom, a2.geom)          WHERE  a1.valid = True and a2.valid = True and a1.id <> a2.id;
    '''

    query1 = origin1.replace('COUNT(*)', 'a1.id, a2.id').replace(';', ' ORDER BY a1.id, a2.id;')
    query2 = origin2.replace('COUNT(*)', 'a1.id, a2.id').replace(';', ' ORDER BY a1.id, a2.id;')

    

    executor.execute("USE nyc;")

    executor.execute(query1)
    rows1 = executor.rows

    executor.execute(query2)
    rows2 = executor.rows

    print('query1: ' + str(len(rows1)))
    print('query2: ' + str(len(rows2)))


    set1 = set(rows1)
    set2 = set(rows2)

    if len(rows1)> len(rows2):
        dif = set1.difference(set2)
    else:
        dif = set2.difference(set1)

    print(dif)

    id1 = list(dif)[0][0]
    id2 = list(dif)[0][1]

    func = re.findall(r'\bST_([A-Za-z_]+)\b', query1)[0]
    print(func)

    table1 = re.findall(r'\bFROM ([A-Za-z_]+) As\b', query1)[0]
    table2 = re.findall(r'\bFROM ([A-Za-z_]+) As\b', query2)[0]
    print(table1)
    print(table2)

    simple1 = f'''
    SELECT ST_{func}(a1.geom, a2.geom) FROM {table1} as a1, {table1} as a2 WHERE a1.id = {id1} and a2.id = {id2};
    '''

    simple2 = f'''
    SELECT ST_{func}(a1.geom, a2.geom) FROM {table2} as a1, {table2} as a2 WHERE a1.id = {id1} and a2.id = {id2};
    '''

    executor.execute(simple1)
    rows1 = executor.rows

    executor.execute(simple2)
    rows2 = executor.rows

    print('simple query ' + str(rows1 == rows2) + simple1 + simple2)

    if rows1 != rows2: exit(0)

    
    executor.execute(f'''DROP TABLE IF EXISTS t1;''')
    executor.execute(f'''DROP TABLE IF EXISTS t2;''')
    executor.execute(f'''CREATE TABLE t1 AS SELECT * FROM {table1};''')
    executor.execute(f'''CREATE TABLE t2 AS SELECT * FROM {table2};''')
    # executor.execute(f'''create spatial index spidx2 on t2(geom);''')
    
    if TestCondition() == False:
        print('err')
        exit(-1)
        
    print('begin detla debugging...')

    while delta_debugging():
        executor.execute('''SELECT COUNT(*) FROM t1;''')
        tl1 = executor.rows[0][0]
        
        SortTable()

        executor.execute('''SELECT COUNT(*) FROM t1;''')
        tl2 = executor.rows[0][0]
        
        assert(tl1 == tl2)

        if TestCondition() == False: 
            print('err')
            exit(-1)
main()
