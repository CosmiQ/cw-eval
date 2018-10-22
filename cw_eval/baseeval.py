import shapely.wkt
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import os
from cw_eval import evalfunctions as eF
from fiona._err import CPLE_OpenFailedError




class eval_base():

    def __init__(self, ground_truth_vector_file):

        ## Load Ground Truth : Ground Truth should be in geojson or shape file
        try:
            self.ground_truth_GDF = gpd.read_file(ground_truth_vector_file)
        except CPLE_OpenFailedError:  # handles empty geojson
            self.ground_truth_GDF = gpd.GeoDataFrame({'sindex': [],
                                                      'condition': []})
        # force calculation of spatialindex
        self.ground_truth_sindex = self.ground_truth_GDF.sindex

        ## create deep copy of ground truth file for calculations
        self.ground_truth_GDF_Edit = self.ground_truth_GDF.copy(deep=True)

        self.proposal_GDF = gpd.GeoDataFrame([])


    def eval_iou(self, miniou=0.5, iou_field_prefix='iou_score',
                 ground_truth_class_field='',
                 calculate_class_scores=True,
                 class_list=['all']
                 ):



        scoring_dict_list = []
        if calculate_class_scores:
            class_list.extend(list(self.ground_truth_GDF['condition'].unique()))
            if not self.proposal_GDF.empty:
                class_list.extend(list(self.proposal_GDF['__max_conf_class'].unique()))
            class_list = list(set(class_list))






        for class_id in class_list:

            iou_field = "{}_{}".format(iou_field_prefix, class_id)

            if class_id is not 'all':
                self.ground_truth_GDF_Edit = self.ground_truth_GDF[
                    self.ground_truth_GDF[ground_truth_class_field]==class_id].copy(deep=True)
            else:
                self.ground_truth_GDF_Edit = self.ground_truth_GDF.copy(deep=True)






            for idx, pred_row in tqdm(self.proposal_GDF.iterrows()):


                if pred_row['__max_conf_class']== class_id or class_id=='all':
                    pred_poly = pred_row.geometry
                    iou_GDF = eF.calculate_iou(pred_poly, self.ground_truth_GDF_Edit) #, self.ground_truth_sindex)


                    # Get max iou
                    if not iou_GDF.empty:
                        max_iou_row = iou_GDF.loc[iou_GDF['iou_score'].idxmax(axis=0, skipna=True)]

                        if max_iou_row['iou_score']>miniou:

                            self.proposal_GDF.loc[pred_row.name, iou_field] = max_iou_row['iou_score']
                            #print(max_iou_row.name)
                            self.ground_truth_GDF_Edit = self.ground_truth_GDF_Edit.drop(max_iou_row.name, axis=0)

                        else:

                            self.proposal_GDF.loc[pred_row.name, iou_field] = 0
                    else:
                        self.proposal_GDF.loc[pred_row.name, iou_field] = 0

            if self.proposal_GDF.empty:
                TruePos = 0
                FalsePos = 0
            else:
                try:
                    TruePos = self.proposal_GDF[self.proposal_GDF[iou_field]>=miniou].shape[0]
                    FalsePos = self.proposal_GDF[self.proposal_GDF[iou_field]<miniou].shape[0]
                except:
                    print("iou field {} missing")
                    TruePos = 0
                    FalsePos = 0


            FalseNeg = self.ground_truth_GDF_Edit.shape[0]

            if float(TruePos+FalsePos) > 0:

                Precision = TruePos / float(TruePos + FalsePos)

            else:
                Precision = 0

            if float(TruePos + FalseNeg) > 0:
                Recall    = TruePos / float(TruePos + FalseNeg)

            else:
                Recall = 0

            if Recall*Precision>0:
                F1Score   = 2*Precision*Recall/(Precision+Recall)
            else:
                F1Score   = 0

            score_calc = {'class_id': class_id,
                          'iou_field': iou_field,
                          'TruePos': TruePos,
                          'FalsePos': FalsePos,
                          'FalseNeg': FalseNeg,
                          'Precision': Precision,
                          'Recall':  Recall,
                          'F1Score': F1Score
                          }

            scoring_dict_list.append(score_calc)

        return scoring_dict_list

    def load_proposal(self, proposal_vector_file, conf_field_list=['conf'], proposalCSV=False,
                      conf_field_mapping=[]):

        ## Load Proposal
        if os.path.isfile(proposal_vector_file):
            if proposalCSV:
                pred_data = pd.read_csv(proposal_vector_file)
                self.proposal_GDF = gpd.GeoDataFrame(pred_data,
                                            geometry=[shapely.wkt.loads(pred_row['coords_geo']) for idx, pred_row in
                                                      pred_data.iterrows()])


            else:
                self.proposal_GDF = gpd.read_file(proposal_vector_file)

            if conf_field_list:
                self.proposal_GDF['__total_conf'] = self.proposal_GDF[conf_field_list].max(axis=1)
                self.proposal_GDF['__max_conf_class'] = self.proposal_GDF[conf_field_list].idxmax(axis=1)
            else:
                self.proposal_GDF['__total_conf']=1.0
                self.proposal_GDF['__max_conf_class']=1


            if conf_field_mapping:
                self.proposal_GDF['__max_conf_class'] = [conf_field_mapping[item] for item in self.proposal_GDF['__max_conf_class'].values]

            self.proposal_GDF = self.proposal_GDF.sort_values(by='__total_conf', ascending=False)
        else:


            self.proposal_GDF = gpd.GeoDataFrame(geometry=[])

        return 0

    def eval(self, type='iou'):

        pass
