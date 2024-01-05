git clone https://github.com/mysql/mysql-server.git
cd mysql-server
mkdir -p build
cd build
wget https://boostorg.jfrog.io/artifactory/main/release/1.77.0/source/boost_1_77_0.tar.bz2
tar -xjvf boost_1_77_0.tar.bz2

cmake .. -DDOWNLOAD_BOOST=1 -DWITH_BOOST=boost_1_77_0

make -j8
make install

pip install mysql-connector-python numpy