mkdir -p /log/coverage

/duckdb_spatial/build/debug/duckdb < script/script/test.sql

lcov -c -d /duckdb_spatial/build/debug -o /log/coverage/spatial.info || exit -1

lcov --summary /log/coverage/spatial.info || exit -1
