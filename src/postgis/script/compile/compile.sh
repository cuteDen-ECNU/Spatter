
postgis_new=$1
geos_new=$2

rm -r /usr/local/pgsql/

# rm -r /postgres
# git clone https://github.com/postgres/postgres.git || exit -1
# rm -r /geos
# git clone https://github.com/libgeos/geos.git || exit -1
# rm -r /postgis
# git clone https://github.com/postgis/postgis.git || exit -1

cd /postgres
./configure --without-readline --without-icu
make -j8
make install

cd /geos
git config --global --add safe.directory /geos
git checkout $geos_new
rm -r build
mkdir build
cd build
../configure
cmake .. 
make -j8 
make install


cd /postgis
git config --global --add safe.directory /postgis
git checkout $postgis_new
make distclean
./autogen.sh
CFLAGS="-O0" CPPFLAGS="-O0" \
LDFLAGS="" \
./configure --with-pgconfig=/usr/local/pgsql/bin/pg_config \
 --with-geosconfig=/usr/local/bin/geos-config \
 --without-protobuf --without-raster --without-topology --enable-debug 
make -j8
make install

export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/pgsql/lib:$LD_LIBRARY_PATH
ldconfig
