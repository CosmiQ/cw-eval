import geopandas as gpd

def calculate_iou(pred_poly, test_data_GDF): #, test_sindex):
    '''
    pred_poly: <shapely Polygon object>
    test_data: <geopandas dataframe>
    test_sindex: <rtree spatial index>

    For a given pred_poly, get all the ground truth indicies of overlaps.
    Using the indicies calculate the exact IOU score with every ground truth
    polygon that pred_poly overlaps with.  Store the result of the one with
    the most overlap and remove that ground truth polygon from the tree so it
    won't be considered again.
    '''
    #test_tree = test_sindex
    iou_list = []

    # Fix bowties and self-intersections
    if not pred_poly.is_valid:
        pred_poly = pred_poly.buffer(0.0)

    # Find all ground truth overlaps with prediction and get IOU score for each

    #possible_matches_index = list(test_tree.intersection(pred_poly.bounds))
    #possible_matches = test_data_GDF.iloc[possible_matches_index]
    precise_matches = test_data_GDF[test_data_GDF.intersects(pred_poly)]

    iou_row_list = []
    for idx, row in precise_matches.iterrows():
        # Load ground truth polygon and check exact iou

        test_poly = row.geometry

        # Ignore invalid polygons for now
        if pred_poly.is_valid and test_poly.is_valid:
            intersection = pred_poly.intersection(test_poly).area
            union = pred_poly.union(test_poly).area

            # Calculate iou
            iou_score = intersection / float(union)

        else:
            iou_score = 0

        row['iou_score'] = iou_score

        iou_row_list.append(row)

    iou_GDF = gpd.GeoDataFrame(iou_row_list)

    # print(results_DF['iou_score'].max())

    return iou_GDF


def process_iou(pred_poly, test_data_DF, remove_matching_element=True):

    iou_GDF = calculate_iou(pred_poly, test_data_DF)

    max_iou_row = iou_GDF.loc[iou_GDF['iou_score'].idxmax(axis=0, skipna=True)]

    if remove_matching_element:
        test_data_DF.drop(max_iou_row.name, axis=0, inplace=True)

    # Prediction poly had no overlap with anything
    #if not iou_list:
    #    return max_iou_row, 0, test_data_DF
    #else:
    #    max_iou_idx, max_iou = max(iou_list, key=lambda x: x[1])
    #    # Remove ground truth polygon from tree
    #    test_tree.delete(max_iou_idx, Polygon(test_data[max_iou_idx]['geometry']['coordinates'][0]).bounds)
    #    return max_iou_row['iou_score'], iou_GDF, test_data_DF


