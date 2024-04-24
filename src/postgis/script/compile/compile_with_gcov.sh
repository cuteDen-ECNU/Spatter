
postgis_hash=$1
geos_hash=$2

mkdir /gcov
cd /gcov
git clone https://github.com/postgres/postgres.git || exit -1
git clone https://github.com/libgeos/geos.git || exit -1
git clone https://github.com/postgis/postgis.git || exit -1

cd /gcov/postgres
./configure --without-readline --without-icu
make -j8 || exit -1
make install

cd /gcov/geos
git config --global --add safe.directory /geos
git checkout $geos_hash
mkdir build
cd build
../configure
cmake .. -D CMAKE_BUILD_TYPE=COVERAGE
make -j8 || exit -1
make install


cd /gcov/postgis
git config --global --add safe.directory /postgis
git checkout $postgis_hash
./autogen.sh

CFLAGS="-O0 -fprofile-arcs -ftest-coverage" CPPFLAGS="-O0 -fprofile-arcs -ftest-coverage" \
LDFLAGS="-fprofile-arcs -lgcov" \
./configure --with-pgconfig=/usr/local/pgsql/bin/pg_config \
 --with-geosconfig=/usr/local/bin/geos-config \
 --without-protobuf --without-raster --without-topology --enable-debug 
make -j8 || exit -1
make install

export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/pgsql/lib:$LD_LIBRARY_PATH
ldconfig
