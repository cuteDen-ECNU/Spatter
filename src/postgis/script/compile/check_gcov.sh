mkdir -p /log/coverage
lcov -c -d /postgis -o /log/coverage/postgis.info || exit -1
lcov -c -d /geos -o /log/coverage/geos.info || exit -1

lcov --summary /log/coverage/postgis.info || exit -1
lcov --summary /log/coverage/geos.info || exit -1
