# git clone https://github.com/libgeos/geos.git

# tar cvjf geos-3.13.tar.bz2 geos
# cp /geos-3.13.tar.bz2 /duckdb_spatial/deps/vendor
rm /duckdb_spatial -r
git clone --recurse-submodules https://github.com/duckdblabs/duckdb_spatial


cd /duckdb_spatial
cp /script/compile/CMakeLists.txt /duckdb_spatial/
make clean
GEN=ninja make debug

