DROP TABLE IF EXISTS t0;
-- DROP TABLE
CREATE TABLE t0 (id int, geom geometry, valid boolean);
-- CREATE TABLE
CREATE INDEX t0_idx ON t0 USING HASH (geom);
-- CREATE INDEX
DROP TABLE IF EXISTS t1;
-- DROP TABLE
CREATE TABLE t1 (id int, geom geometry, valid boolean);
-- CREATE TABLE
CREATE INDEX t1_idx ON t1 USING BTREE (geom);
-- CREATE INDEX
INSERT INTO t0 (id, geom) VALUES (0,ST_Affine(ST_GeomCollFromText('GEOMETRYCOLLECTION(POINT(33 40))',0), 1, 0, 0, 1,298,341));
-- INSERT 0 1
INSERT INTO t0 (id, geom) VALUES (1,ST_Affine(ST_MPointFromText('MULTIPOINT((92 84))',0), 1, 0, 0, 1,82,-980));
-- INSERT 0 1
INSERT INTO t0 (id, geom) VALUES (2,ST_Affine(ST_LineFromText('LINESTRING(82 57,15 11 ,96 44 )',0), 1, 0, 0, 1,-734,944));
-- INSERT 0 1
INSERT INTO t0 (id, geom) VALUES (3,ST_Affine(ST_GeomFromText('MULTIPOLYGON EMPTY',0), 1, 0, 0, 1,591,-413));
-- INSERT 0 1
INSERT INTO t0 (id, geom) VALUES (4,ST_Affine(ST_MPolyFromText('MULTIPOLYGON EMPTY',0), 1, 0, 0, 1,-444,-92));
-- INSERT 0 1
INSERT INTO t0 (id, geom) VALUES (5,ST_Affine(ST_PointFromText('POINT(42 44)',0), 1, 0, 0, 1,-984,648));
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 6, ST_Collect(t0.geom, t2.geom)          FROM t0 As t0, t0 As t2         WHERE t0.id = 0         and t2.id = 1;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 7, ST_BoundingDiagonal(t0.geom)         FROM t0         WHERE t0.id = 3;
-- INSERT 0 1
INSERT INTO t0 (id, geom)         SELECT 8, ST_ConvexHull(geom)          FROM t0         WHERE t0.id = 2;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 9, ST_Collect(t0.geom, t2.geom)          FROM t0 As t0, t0 As t2         WHERE t0.id = 7         and t2.id = 2;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 10, ST_CollectionExtract(t0.geom)           FROM t0         WHERE t0.id = 7;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 11, ST_Collect(t0.geom, ST_LineFromText('LINESTRING EMPTY',0))          FROM t0 As t0         WHERE t0.id = 7;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 12, ST_Collect(t0.geom, t2.geom)          FROM t0 As t0, t0 As t2         WHERE t0.id = 7         and t2.id = 7;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 13, ST_SetPoint(t0.geom, 0, 'POINT(-1 1)')          FROM t0         WHERE t0.id = 9;
-- ['TopologyException']
INSERT INTO t0 (id, geom)          SELECT 13, ST_CollectionExtract(t0.geom)           FROM t0         WHERE t0.id = 5;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 14, ST_GeometryN(t0.geom, 9)           FROM t0         WHERE t0.id = 0;
-- INSERT 0 1
INSERT INTO t0 (id, geom)          SELECT 15, ST_Collect(t0.geom, t2.geom)          FROM t0 As t0, t0 As t2         WHERE t0.id = 13         and t2.id = 3;
-- INSERT 0 1
INSERT INTO t0 (id, geom)         SELECT row_number() OVER () + 16 - 1, sub_query.geom         FROM (         SELECT             (ST_DUMP(geom)).geom AS geom          FROM t0 As t         WHERE t.id = 6         ) AS sub_query;
-- INSERT 0 2
DELETE FROM t0 As a1 WHERE ST_IsEmpty(a1.geom) ;
-- DELETE 6
UPDATE t0 SET valid = ST_IsValid(geom);
-- UPDATE 12
INSERT INTO t1 (id, geom) SELECT id, geom FROM t0;
-- INSERT 0 12

-- ['TopologyException']
UPDATE t1 SET geom = ST_Collect(ST_PointOnSurface(geom), geom);
