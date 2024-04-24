DROP extension postgis CASCADE;
-- ['TopologyException', 'extension "postgis" does not exist']
-- 2.60162353515625
-- 
-- cd /geos-commits/7d8455ce4/geos/build; make install;
-- cd /postgis-commits/cac91cf88-7d8455ce4/postgis; make install;
CREATE EXTENSION postgis;
-- 342.1130180358887
-- CREATE EXTENSION
SELECT postgis_full_version();
-- [('POSTGIS="3.5.0dev 3.4.0rc1-721-gcac91cf88" [EXTENSION] PGSQL="170" GEOS="3.13.0dev-CAPI-1.18.0" PROJ="8.2.1 NETWORK_ENABLED=OFF URL_ENDPOINT=https://cdn.proj.org USER_WRITABLE_DIRECTORY=/tmp/proj DATABASE_PATH=/usr/share/proj/proj.db" LIBXML="2.9.13"',)]
-- 6.562232971191406
DROP TABLE IF EXISTS t0;
-- 0.8509159088134766
-- DROP TABLE
CREATE TABLE t0 (id int, geom geometry, valid boolean);
-- 0.8947849273681641
-- CREATE TABLE
CREATE INDEX t0_idx ON t0 USING HASH (geom);
-- 0.49877166748046875
-- CREATE INDEX
DROP TABLE IF EXISTS t1;
-- 0.5269050598144531
-- DROP TABLE
CREATE TABLE t1 (id int, geom geometry, valid boolean);
-- 0.6885528564453125
-- CREATE TABLE
CREATE INDEX t1_idx ON t1 USING BTREE (geom);
-- 0.4932880401611328
-- CREATE INDEX
INSERT INTO t0 (id, geom) VALUES (0,ST_Affine(ST_GeomFromText('MULTIPOINT((71 6),(21 65))',0), 1, 0, 0, 1,716,595));
-- INSERT 0 1
-- 0.43511390686035156
INSERT INTO t0 (id, geom) VALUES (1,ST_Affine(ST_GeomCollFromText('GEOMETRYCOLLECTION EMPTY',0), 1, 0, 0, 1,-881,745));
-- INSERT 0 1
-- 0.3070831298828125
INSERT INTO t0 (id, geom) VALUES (2,ST_Affine(ST_GeomFromText('MULTIPOINT((97 72),(29 8),(63 68),(92 17),(37 98),(86 42),(73 84),(8 8))',0), 1, 0, 0, 1,489,147));
-- INSERT 0 1
-- 0.2338886260986328
INSERT INTO t0 (id, geom) VALUES (3,ST_Affine(ST_GeomCollFromText('GEOMETRYCOLLECTION(MULTILINESTRING((9 68,42 86 ), (96 69,56 15 ,96 69)),POINT(2 78))',0), 1, 0, 0, 1,119,-843));
-- INSERT 0 1
-- 0.2624988555908203
INSERT INTO t0 (id, geom)          SELECT 4, ST_Boundary(t0.geom)          FROM t0         WHERE t0.id = 3;
-- INSERT 0 1
-- 0.28228759765625
INSERT INTO t0 (id, geom)         SELECT row_number() OVER () + 5 - 1, sub_query.geom         FROM (         SELECT             (ST_DUMP(geom)).geom AS geom          FROM t0 As t         WHERE t.id = 3         ) AS sub_query;
-- INSERT 0 3
-- 0.3650188446044922
INSERT INTO t0 (id, geom)          SELECT 8, ST_SetPoint(t0.geom, 0, 'POINT(-1 1)')          FROM t0         WHERE t0.id = 5;
-- INSERT 0 1
-- 0.2486705780029297
INSERT INTO t0 (id, geom)          SELECT 9, ST_Polygonize(t0.geom)           FROM t0         WHERE t0.id = 0;
-- INSERT 0 1
-- 0.3323554992675781
DELETE FROM t0 As a1 WHERE ST_IsEmpty(a1.geom) ;
-- 0.2295970916748047
-- DELETE 2
UPDATE t0 SET valid = ST_IsValid(geom);
-- UPDATE 8
-- 0.2751350402832031
INSERT INTO t1 (id, geom) SELECT id, geom FROM t0;
-- INSERT 0 8
-- 0.4036426544189453
UPDATE t1 SET geom = ST_Collect(ST_PointOnSurface(geom), geom);
-- UPDATE 8
-- 0.37789344787597656
DROP extension postgis CASCADE;
-- 29.537200927734375
-- DROP EXTENSION
-- cd /geos-commits/7d8455ce4/geos/build; make uninstall;
-- cd /postgis-commits/cac91cf88-7d8455ce4/postgis; make uninstall;
