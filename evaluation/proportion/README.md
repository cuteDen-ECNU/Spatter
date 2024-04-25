# Small efficiency study

## Purpose
We aim to show where the bottleneck is in Spatter.

To this end, we measure the proportion of time spent in the SDBMS and the time spent in Spatter. It helps users decide on how to configure the number of geometries in a database.

## Result
PostGIS, 1  
spatter: 47.873122692108154 &plusmn; 2.4189205215708083  
dbms: 40.641844272613525 &plusmn; 2.265266196239746  
PostGIS, 10  
spatter: 235.49625635147095 &plusmn; 203.93299923778991  
dbms: 225.3288984298706 &plusmn; 202.2946197938809  
PostGIS, 50  
spatter: 586.8813061714172 &plusmn; 271.8446801832471  
dbms: 572.8755259513855 &plusmn; 269.3272655450885  
PostGIS, 100  
spatter: 1553.1445384025574 &plusmn; 516.6533911850064  
dbms: 1532.0515131950378 &plusmn; 512.775052232603  
MySQL GIS, 1  
spatter: 89.03729438781738 &plusmn; 7.667122094173985  
dbms: 67.74123668670654 &plusmn; 5.859649340759701  
MySQL GIS, 10  
spatter: 251.32888078689575 &plusmn; 53.11170490645368  
dbms: 224.58387851715088 &plusmn; 52.283087767298035  
MySQL GIS, 50  
spatter: 1675.9042644500732 &plusmn; 315.4498794692578  
dbms: 1619.1365957260132 &plusmn; 314.2459233282975  
MySQL GIS, 100  
spatter: 4984.684872627258 &plusmn; 860.5729822390041  
dbms: 4889.3186712265015 &plusmn; 859.5715494018666  
DuckDB Spatial, 1  
spatter: 165.90538501739502 &plusmn; 12.981062370353477  
dbms: 158.0299687385559 &plusmn; 12.972708465372918  
DuckDB Spatial, 10  
spatter: 292.14897632598877 &plusmn; 116.94552277193417  
dbms: 283.5539937019348 &plusmn; 116.83970144249162  
DuckDB Spatial, 50  
spatter: 1922.5085520744324 &plusmn; 1331.4701615966278  
dbms: 1911.4439487457275 &plusmn; 1331.4077689709684  
DuckDB Spatial, 100  
spatter: 5803.981223106384 &plusmn; 2264.00153011549  
dbms: 5789.749295711517 &plusmn; 2263.702746210628  


## Reproduce

Run Spatter for PostGIS
```
cd src/postgis
docker_name=postgis-spatter
docker exec -it $docker_name sh -c "rm -r /log/*"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 1"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 10"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 50"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 100"
```

Run Spatter for MySQL GIS
```
cd src/mysql
docker_name=mysql-spatter
docker exec -it $docker_name sh -c "rm -r /log/*"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 1"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 10"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 50"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 100"
```

Run Spatter for DuckDB Spatial
```
cd src/duckdb
docker_name=duckdb-spatter
docker exec -it $docker_name sh -c "rm -r /log/*"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 1"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 10"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 50"
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py --geometry_number 100"
```


