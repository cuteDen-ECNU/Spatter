from shapely.wkt import loads
import matplotlib.pyplot as plt

# 创建两个几何对象
# g1 = loads('POLYGON((445 614,26 30,30 80,445 614))')
# g2 = loads('POLYGON((1010 190,90 40,40 90,1010 190))')
g1 = loads('POLYGON((-63 -51,-65 -47,-62 -42,-63 -51,-63 -51))')
g3 = loads('POINT(-63 -49)')

# 可视化几何对象
fig, ax = plt.subplots()

def plot_geometry(geom):
    if geom.geom_type == 'Polygon':
        x, y = geom.exterior.xy
        ax.plot(x, y, label='Polygon')
    elif geom.geom_type == 'MultiLineString':
        for line in geom.geoms:
            x, y = line.xy
            ax.plot(x, y, label='MultiLineString')
    elif geom.geom_type == 'LineString':
        x, y = geom.xy
        ax.plot(x, y, label='LineString')
    elif geom.geom_type == 'Point':
        x, y = geom.xy
        ax.plot(x, y, label='Point', marker='o')
    
    elif geom.geom_type == 'GeometryCollection':
        for part in geom.geoms:
            plot_geometry(part)  # 递归调用处理 GeometryCollection 中的每个部分

plot_geometry(g1)
# plot_geometry(g2)
plot_geometry(g3)

# 限制x轴和y轴的范围
# ax.set_xlim(0, 1100)  # 设置x轴范围
# ax.set_ylim(0, 1100)  # 设置y轴范围

ax.set_aspect('equal', adjustable='box')
ax.legend()
plt.savefig('/log/a.png')
