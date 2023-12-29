
import re
import Executor
import Log

log = Log.Log(0)
executor = Executor.Executor(log)

def loadErrorFunc(wtx:str):
    return executor.execute(f'''SELECT ST_GeomFromText('{wtx}')''', [])

def up(i):
    return (i//10 + 1) * 10

def down(i):
    return i//10 * 10

def QueryResultsEquels(query1, query2):
    executor.executeSelect(query1,['Invalid Input Error'])
    if executor.error_occur == True:
        return True
    rows1 = executor.rows
    
    executor.executeSelect(query2,['Invalid Input Error'])
    if executor.error_occur == True:
        return True
    rows2 = executor.rows
    return rows1 == rows2

def GeometryApproximate(query1, query2):


    integer_list = []
    integer_list += re.findall(r"\d+", query1)
    integer_list = list(set(integer_list))

    log.WriteResult(str(integer_list))

    flag = False
    for e_str in integer_list:
        e = int(e_str)
        equal = QueryResultsEquels(query1.replace(str(e), str(up(e)), -1), query2.replace(str(e), str(up(e)), -1))
        if equal == False:
            query1 = query1.replace(str(e), str(up(e)), -1)
            query2 = query2.replace(str(e), str(up(e)), -1)
            flag = True
        else:
            equal = QueryResultsEquels(query1.replace(str(e), str(down(e)), -1), query2.replace(str(e), str(down(e)), -1))
            if equal == False:
                query1 = query1.replace(str(e), str(down(e)), -1)
                query2 = query2.replace(str(e), str(down(e)), -1)
                flag = True
            else:
                print(e_str)
    if flag == False:
        print(query1)
        print(query2)
        exit(0)
    return [query1, query2]

query1 = '''
SELECT ST_Overlaps(ST_GeomFromText('GEOMETRYCOLLECTION (POLYGON ((35 72, 36 77, 37 75, 35 72)), POINT (19 74))'),
ST_GeomFromText('POLYGON ((61 5, 26 59, 19 74, 61 5))'))
;  '''
query2 = '''
SELECT ST_Overlaps(ST_GeomFromText('GEOMETRYCOLLECTION (POLYGON ((35 72, 36 77, 37 75, 35 72)), POINT (19 74))')
, ST_GeomFromText('POLYGON ((19 74, 61 5, 26 59, 19 74))'))
;'''

query1, query2 = GeometryApproximate(query1, query2)
query1 = query1.replace('0 ', ' ', -1).replace('0)', ')', -1).replace('0,', ',', -1)
query2 = query2.replace('0 ', ' ', -1).replace('0)', ')', -1).replace('0,', ',', -1)
print(query1)
print(query2)
