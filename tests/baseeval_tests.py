import os
from cw_eval.baseeval import EvalBase
import cw_eval
import geopandas as gpd


class TestEvalBase(object):
    def test_init_from_file(ground_truth_vector_file):
        """Test instantiation of an EvalBase instance from a file."""
        base_instance = EvalBase(os.path.join(cw_eval.data.data_dir,
                                              'gt.geojson'))
        gt_gdf = cw_eval.data.gt_gdf()
        assert base_instance.ground_truth_sindex == gt_gdf.sindex
        assert base_instance.proposal_gdf == gpd.GeoDataFrame([])
        assert base_instance.ground_truth_GDF == base_instance.ground_truth_GDF_Edit

    def test_init_from_gdf(gdf):
        """Test instantiation of an EvalBase from a pre-loaded GeoDataFrame."""
        gdf = cw_eval.data.gt_gdf()
        base_instance = EvalBase(gdf)
        assert base_instance.ground_truth_sindex == gdf.sindex
        assert base_instance.proposal_gdf == gpd.GeoDataFrame([])
        assert base_instance.ground_truth_GDF == base_instance.ground_truth_GDF_Edit

    def test_init_empty_geojson(empty_geojson_path):
        """Test instantiation of EvalBase with an empty geojson file."""
        base_instance = EvalBase(os.path.join(cw_eval.data.data_dir,
                                              'empty.geojson'))
        expected_gdf = gpd.GeoDataFrame({'sindex': [],
                                         'condition': [],
                                         'geometry': []})
        assert base_instance.ground_truth_GDF == expected_gdf
