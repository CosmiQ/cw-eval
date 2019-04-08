import os
from cw_eval.challenge_eval.spacenet_buildings2_dataset import eval_spacenet_buildings2
import cw_eval
import subprocess
import pandas as pd


class TestEvalSpaceNetBuildings2(object):
    """Tests for the ``eval_spacenet_buildings2`` function."""
    def test_scoring(self):
        """Test a round of scoring."""
        # load predictions
        pred_results = pd.read_csv(os.path.join(cw_eval.data.data_dir,
                                                'SN2_test_results.csv'))
        pred_results_full = pd.read_csv(os.path.join(cw_eval.data.data_dir,
                                                     'test_results_full.csv'))
        results_df, results_df_full = eval_off_nadir(
            os.path.join(cw_eval.data.data_dir, 'SN2_sample_preds.csv'),
            os.path.join(cw_eval.data.data_dir, 'SN2_sample_truth.csv')
            )
        assert pred_results.equals(results_df.reset_index())
        assert pred_results_full.equals(results_df_full)


class TestEvalCLISN2(object):
    """Test the CLI ``spacenet_eval`` function, as applied to SpaceNet2."""
    def test_cli(self):
        """Test a round of scoring using the CLI."""
        pred_results = pd.read_csv(os.path.join(
            cw_eval.data.data_dir, 'SN2_test_results.csv'))
        pred_results_full = pd.read_csv(os.path.join(
            cw_eval.data.data_dir, 'SN2_test_results_full.csv'))
        proposal_csv = os.path.join(cw_eval.data.data_dir,
                                    'SN2_sample_preds.csv')
        truth_csv = os.path.join(cw_eval.data.data_dir,
                                 'SN2_sample_truth.csv')
        subprocess.call(['spacenet_eval', '--proposal_csv='+proposal_csv,
                         '--truth_csv='+truth_csv,
                         '--challenge=spaceNet-buildings2',
                         '--output_file=test_out'])
        test_results = pd.read_csv('test_out.csv')
        full_test_results = pd.read_csv('test_out_full.csv')

        assert pred_results.equals(test_results)
        assert pred_results_full.sort_values(by='imageID').reset_index(drop=True).equals(
            full_test_results.sort_values(by='imageID').reset_index(drop=True))
