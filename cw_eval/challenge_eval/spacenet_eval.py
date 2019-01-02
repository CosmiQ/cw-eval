"""Script for executing eval for SpaceNet challenges."""
from __future__ import print_function, with_statement, division
from cw_eval.challenge_eval import off_nadir_dataset
import argparse
import pandas as pd
supported_challenges = ['off-nadir']#, 'spaceNet-buildings2', 'spaceNet-building1', 'spacenet-roads1', 'buildings', 'roads']


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate SpaceNet Competition CSVs')
    parser.add_argument('--proposal_csv', '-p', type=str,
                        help='Proposal CSV')
    parser.add_argument('--truth_csv', '-t', type=str,
                        help='Truth CSV')
    parser.add_argument('--challenge', type=str,
                        default='off-nadir',
                        choices=supported_challenges,
                        help='SpaceNet Challenge eval type')
    parser.add_argument('--output_file', '-o', type=str,
                        default='Off-Nadir',
                        help='Output file To write results to CSV')
    args = parser.parse_args()

    truth_file = args.truth_csv
    prop_file = args.proposal_csv

    if args.challenge.lower() == 'off-nadir':
        evalSettings = {'miniou': 0.5,
                        'minArea': 20}
        results_DF, results_DF_Full = off_nadir_dataset.eval_off_nadir(
            prop_csv=prop_file, truth_csv=truth_file, **evalSettings)

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(results_DF)

    if args.output_file:
        print("Writing summary results to {}".format(
            args.output_file.rstrip('.csv') + '.csv'))
        results_DF.to_csv(args.output_file.rstrip('.csv') + '.csv',
                          index=False)
        print("Writing full results to {}".format(
            args.output_file.rstrip('.csv')+"_full.csv"))
        results_DF_Full.to_csv(args.output_file.rstrip('.csv')+"_full.csv",
                               index=False)


if __name__ == '__main__':
    main()
