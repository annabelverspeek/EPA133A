import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon

def find_intersections(roads_gdf):
    intersections = []
    for i, road1 in roads_gdf.iterrows():
        for j, road2 in roads_gdf.iterrows():
            if i != j:
                intersection = road1['geometry'].intersection(road2['geometry'])
                if intersection.is_empty:
                    continue
                elif isinstance(intersection, MultiPolygon):
                    for polygon in intersection:
                        intersections.append(polygon)
                elif isinstance(intersection, Polygon):
                    intersections.append(intersection)
    return intersections
def plot_intersections(gdf, intersections_list, column='road'):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the roads
    gdf.plot(ax=ax, column=column, alpha=0.5, legend=True, legend_kwds={'bbox_to_anchor': (1.35, 1)})

    # Plot the intersections
    for intersection in intersections_list:
        if isinstance(intersection, MultiPolygon):
            for polygon in intersection:
                ax.plot(*polygon.exterior.xy, color='red')
        elif isinstance(intersection, Polygon):
            ax.plot(*intersection.exterior.xy, color='red')

    plt.show()

selected = ['N1', 'N102', 'N104', 'N105', 'N106', 'N2', 'N204', 'N207', 'N208']
shape = gpd.read_file('input/roads.shp')
shape_roads = shape[shape['ref'].isin(selected)]

intersections = find_intersections(shape_roads)
plot_found_intersections(shape_roads, intersections, 'ref')