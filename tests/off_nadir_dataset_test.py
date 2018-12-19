import os
from cw_eval.challenge_eval.off_nadir_dataset import eval_off_nadir
import cw_eval
import pandas as pd


class TestEvalOffNadir(object):
    """Tests for the ``eval_off_nadir`` function."""
    def test_scoring(self):
        """Test a round of scoring."""
        # load predictions
        pred_results = pd.read_csv(os.path.join(cw_eval.data.data_dir,
                                                'test_results.csv'))
        pred_results_full = pd.read_csv(os.path.join(cw_eval.data.data_dir,
                                                     'test_results_full.csv'))
        results_df, results_df_full = eval_off_nadir(
            os.path.join(cw_eval.data.data_dir, 'sample_preds.csv'),
            os.path.join(cw_eval.data.data_dir, 'sample_truth.csv')
            )
        assert pred_results.equals(results_df.reset_index())
        assert pred_results_full.equals(results_df_full)
