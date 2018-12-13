import geopandas as gpd
import pytest
from cw_eval.evalfunctions import calculate_iou, process_iou
from cw_eval import data
from shapely.geometry import Polygon

class TestEvalFuncs(object):
    def test_overlap(self):
        gt_gdf = data.gt_gdf()
        pred_poly = Polygon(((736348.0, 3722762.5),
                             (736353.0, 3722762.0),
                             (736354.0, 3722759.0),
                             (736352.0, 3722755.5),
                             (736348.5, 3722755.5),
                             (736346.0, 3722757.5),
                             (736348.0, 3722762.5)))
        overlap_pred_gdf = calculate_iou(pred_poly, gt_gdf)
        assert overlap_pred_gdf.index[0] == 27
        assert overlap_pred_gdf.iou_score.iloc[0] == 0.073499798744833519
