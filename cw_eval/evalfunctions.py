from __future__ import print_function, with_statement, division
import pandas as pd
from osgeo import ogr
from rtree.core import RTreeError

def process_iou(pred_poly, test_data_GDF, remove_matching_element=True):
    """Get the maximum intersection over union score for a predicted polygon.

    Arguments
    ---------
    pred_poly : :py:class:`shapely.geometry.Polygon`
        Prediction polygon to test.
    test_data_GDF : :py:class:`geopandas.GeoDataFrame`
        GeoDataFrame of ground truth polygons to test ``pred_poly`` against.
    remove_matching_element : bool, optional
        Should the maximum IoU row be dropped from ``test_data_GDF``? Defaults
        to ``True``.

    Returns
    -------
    *This function doesn't currently return anything.*

    """

    iou_GDF = calculate_iou(pred_poly, test_data_GDF)

    max_iou_row = iou_GDF.loc[iou_GDF['iou_score'].idxmax(axis=0, skipna=True)]

    if remove_matching_element:
        test_data_GDF.drop(max_iou_row.name, axis=0, inplace=True)

    # Prediction poly had no overlap with anything
    # if not iou_list:
    #     return max_iou_row, 0, test_data_DF
    # else:
    #     max_iou_idx, max_iou = max(iou_list, key=lambda x: x[1])
    #     # Remove ground truth polygon from tree
    #     test_tree.delete(max_iou_idx, Polygon(test_data[max_iou_idx]['geometry']['coordinates'][0]).bounds)
    #     return max_iou_row['iou_score'], iou_GDF, test_data_DF


def find_max_IoU(geom_a, geom_b_list, geom_b_idxs=None, min_area=0):
    """Get maximum IoU between geom_a and a list of geoms from geom_b.

    Arguments
    ---------
    geom_a : osgeo.ogr.Geometry
        A geometry object in GDAL format.
    geom_b_list : list
        A list of geometries to compare geom_a against, all in GDAL format.
    geom_b_idxs : list, optional
        The indices that geom_b objects correspond to from their source gdf.
        This is present because the objects passed to `find_max_IoU` are often
        subsetted from a larger set of objects. If not passed, it will default
        to ``list(range(len(geom_b_list)))``.
    """
    if geom_b_idxs is None:
        geom_b_idxs = list(range(len(geom_b_list)))
    best_idx = None
    best_iou = 0
    for idx, geom_b in zip(geom_b_idxs, geom_b_list):
        if geom_b.GetArea() < min_area:
            continue
        # use try/except below to catch rare cases of bad geometry/non-overlap
        try:
            intersect = geom_a.Intersection(geom_b).GetArea()
            union = geom_a.Union(geom_b).GetArea()
            iou = intersect/union
        except AttributeError:
            iou = 0
        if iou > 0.5:
            # there can be no other object with better IoU, so return it
            return idx, iou
        elif iou > best_iou:  # if it's better but not > 0.5, keep trying
            best_idx = idx
            best_iou = iou
    return best_idx, best_iou


def gdal_best_IoU(gdf1, gdf2, min_area=0):
    """Find the highest IoU between two sets of objects using GDAL.

    Notes
    -----
    This is roughly equivalent to using geopandas overlay operations
    to calculate intersection and union, then return the values.
    However, it's much faster when implemented using GDAL.

    Arguments
    ---------
    gdf1 : geopandas.GeoDataFrame
        A geodataframe containing polygons.
    gdf2 : geopandas.GeoDataFrame
        Another geodataframe containing polygons.
    min_area : int or float, optional
        Minimum area for a geometry in gdf2 (the ground truth). Defaults to 0.
        Generally set to 20 in SpaceNet competitions.

    Returns
    -------
    A DataFrame with three columns:
    - idx_1 : The index from gdf1 that this IoU corresponds to.
        This will cover values for every idx in gdf1 (there can be iou=0)
    - idx_2 : The index from gdf2 that this IoU corresponds to.
        This will be `None` if there was no intersection.
    - iou : float
        The IoU score for the best overlap with the polygon from gdf1.

    """
    # Spatial Index to create intersections
    spatial_index = gdf2.sindex
#    print('got spatial index at {} s'.format(time.time()-start_time))
    bbox = gdf1.geometry.apply(lambda x: x.bounds)
#    print('got bounding boxes at {} s'.format(time.time()-start_time))
    sidx = bbox.apply(lambda x: list(spatial_index.intersection(x)))
    sidx = sidx.dropna()
#    print('got overlapping sindices at {} s'.format(time.time()-start_time))
    # make series of geometries from gdf1 and gdf2 in GDAL format
    gdf1_geoms_ogr = gdf1.geometry.apply(
        lambda x: ogr.CreateGeometryFromWkt(str(x)))
    gdf2_geoms_ogr = gdf2.geometry.apply(
        lambda x: ogr.CreateGeometryFromWkt(str(x)))
#    print('made OGR series at {} s'.format(time.time()-start_time))
    # made OGR series
    gdf2_geom_list = sidx.apply(lambda x: list(gdf2_geoms_ogr.iloc[x]))
    gdf1_to_intersectors = pd.DataFrame(
        {'gdf1_geom': gdf1_geoms_ogr,
         'gdf2_geom_idxs': sidx,
         'gdf2_geom_list': gdf2_geom_list})
#    print('got intersection df at {} s'.format(time.time()-start_time))
    interactions = gdf1_to_intersectors.apply(_find_max_IoU_gdf,
                                              min_area=min_area,
                                              axis=1)
#    print('got max IoUs at {} s'.format(time.time()-start_time))
    interactions = interactions.apply(pd.Series)
    result_df = pd.concat([gdf1.index.to_series().rename('gdf1_idx'),
                           interactions[0].rename('gdf2_idx'),
                           interactions[1].rename('iou_score')],
                          axis=1)
    return result_df


def _find_max_IoU_gdf(row, min_area=0):
    """Helper function to pass pandas apply values to `find_max_IoU`."""
    return find_max_IoU(row['gdf1_geom'],
                        row['gdf2_geom_list'],
                        row['gdf2_geom_idxs'],
                        min_area)


def _get_intersectors(bbox, spatial_index):
    try:
        intersectors = list(spatial_index.intersection(bbox))
    except RTreeError:
        intersectors = []
    return intersectors

### DEPRECATED: DON'T USE!!! ###
def calculate_iou(pred_poly, test_data_GDF):
    """Get the best intersection over union for a predicted polygon.

    Arguments
    ---------
    pred_poly : :py:class:`shapely.Polygon`
        Prediction polygon to test.
    test_data_GDF : :py:class:`geopandas.GeoDataFrame`
        GeoDataFrame of ground truth polygons to test ``pred_poly`` against.

    Returns
    -------
    iou_GDF : :py:class:`geopandas.GeoDataFrame`
        A subset of ``test_data_GDF`` that overlaps ``pred_poly`` with an added
        column ``iou_score`` which indicates the intersection over union value.

    """

    # Fix bowties and self-intersections
    if not pred_poly.is_valid:
        pred_poly = pred_poly.buffer(0.0)
    matches = test_data_GDF[test_data_GDF.intersects(pred_poly)]
    matches['iou_score'] = matches.geometry.apply(_get_iou, poly_b=pred_poly)

    # iou_row_list = []
    # for _, row in precise_matches.iterrows():
    #     # Load ground truth polygon and check exact iou
    #     test_poly = row.geometry
    #     # Ignore invalid polygons for now
    #     if pred_poly.is_valid and test_poly.is_valid:
    #         intersection = pred_poly.intersection(test_poly).area
    #         union = pred_poly.union(test_poly).area
    #         # Calculate iou
    #         iou_score = intersection / float(union)
    #     else:
    #         iou_score = 0
    #     row['iou_score'] = iou_score
    #     iou_row_list.append(row)
    #
    # iou_GDF = gpd.GeoDataFrame(iou_row_list)

    return matches
