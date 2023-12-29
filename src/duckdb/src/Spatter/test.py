import duckdb
from Executor import *
from Log import *

query = '''
FORCE INSTALL spatial FROM 'http://nightly-extensions.duckdb.org';
LOAD spatial;
pragma version;
DROP TABLE IF EXISTS origin; 
CREATE TABLE origin (id int, geom geometry);
INSERT INTO origin (id, geom) VALUES (0, ST_Boundary(ST_GeomFromText('GEOMETRYCOLLECTION EMPTY')));
INSERT INTO origin (id, geom) VALUES (1, (ST_Boundary(ST_GeomFromText('MULTILINESTRING((7 33,4 31 ,9 31 ,13 27 ,7 33))'))));
SELECT  ST_Disjoint(a1.geom, a2.geom) FROM origin as a1, origin as a2 WHERE a1.id = 1 and a2.id = 0;
SELECT ST_Disjoint(a1, a2) FROM
(SELECT ST_Boundary(ST_GeomFromText('GEOMETRYCOLLECTION EMPTY')) As a1
, ST_CollectionExtract(ST_Boundary(ST_GeomFromText('MULTILINESTRING((7 33,4 31 ,9 31 ,13 27 ,7 33))'))) As a2) As subquery;

'''
log = Log(0)
executor = Executor(log)

lines = query.split(';')
for line in lines:
    line = line[1:] + ';'
    print(line.startswith('\n'))
    if line.startswith('SELECT') or line.startswith('pragma'):
        executor.executeSelect(line, None)
    else:
        executor.execute(line)
    