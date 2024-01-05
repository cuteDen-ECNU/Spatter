# git clone https://github.com/libgeos/geos.git

# tar cvjf geos-3.13.tar.bz2 geos
# cp /geos-3.13.tar.bz2 /duckdb_spatial/deps/vendor
rm /duckdb_spatial -r
git clone --recurse-submodules https://github.com/duckdblabs/duckdb_spatial

cd /duckdb_spatial/duckdb

cd /duckdb_spatial
make clean
GEN=ninja make debug

# now execute the script
# python3 /script/test.py

# export BUILD_PYTHON=1 GEN=ninja make
# cd duckdb/tools/pythonpkg
# python3 setup.py install