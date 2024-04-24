import os
import duckdb
c = {
            'allow_unsigned_extensions' : True
        }
db = '/log/spatter.db'
conn = duckdb.connect(database=db, config = c)

conn.execute("INSTALL '/duckdb_spatial/build/debug/extension/spatial/spatial.duckdb_extension';")
conn.execute("LOAD spatial;")
conn.execute("SELECT ST_GeomFromText('POINT(0 0 )');")
with open('/duckdb_spatial/build/debug/a.gcda', 'w') as of:
    of.write("111")
