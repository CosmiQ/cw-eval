import shapely.wkt
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import os
from cw_eval import evalfunctions as eF
from fiona.errors import DriverError
from fiona._err import CPLE_OpenFailedError




class eval_base():

    def __init__(self, ground_truth_vector_file, csvFile=False, truth_geo_value='PolygonWKT_Pix'):

        ## Load Ground Truth : Ground Truth should be in geojson or shape file
        try:
            self.ground_truth_GDF = gpd.read_file(ground_truth_vector_file)
        except CPLE_OpenFailedError:  # handles empty geojson
            self.ground_truth_GDF = gpd.GeoDataFrame({'sindex': [],
                                                      'condition': [],
                                                      'geometry': []})
        # force calculation of spatialindex
        self.ground_truth_sindex = self.ground_truth_GDF.sindex

        ## create deep copy of ground truth file for calculations
        self.ground_truth_GDF_Edit = self.ground_truth_GDF.copy(deep=True)

        self.proposal_GDF = gpd.GeoDataFrame([])



    def eval_iou_spacenet_csv(self,
                          miniou=0.5,
                          iou_field_prefix="iou_score",
                          imageIDField="ImageId",
                              debug=False,
                              minArea=0,
                              ):


        # Get List of all ImageIDs
        imageIDList = []
        imageIDList.extend(list(self.ground_truth_GDF[imageIDField].unique()))
        if not self.proposal_GDF.empty:
            imageIDList.extend(list(self.proposal_GDF[imageIDField].unique()))

        imageIDList = list(set(imageIDList))

        iou_field = iou_field_prefix
        scoring_dict_list=[]



        for imageID in tqdm(imageIDList):


            self.ground_truth_GDF_Edit = self.ground_truth_GDF[self.ground_truth_GDF[imageIDField] == imageID].copy(deep=True)
            self.ground_truth_GDF_Edit = self.ground_truth_GDF_Edit[self.ground_truth_GDF_Edit.area>=minArea]

            proposal_GDF_copy = self.proposal_GDF[self.proposal_GDF[imageIDField] == imageID].copy(deep=True)
            proposal_GDF_copy = proposal_GDF_copy[proposal_GDF_copy.area > minArea]

            if debug:
                print(iou_field)

            for idx, pred_row in proposal_GDF_copy.iterrows():
                #print(pred_row)
                #print(iou_field)
                if debug:
                    print(pred_row.name)
                if pred_row.geometry.area > 0:

                    pred_poly = pred_row.geometry
                    iou_GDF = eF.calculate_iou(pred_poly, self.ground_truth_GDF_Edit)

                    #print(iou_field)

                    # Get max iou
                    if not iou_GDF.empty:
                        max_iou_row = iou_GDF.loc[iou_GDF['iou_score'].idxmax(axis=0, skipna=True)]

                        if max_iou_row['iou_score']>miniou:

                            self.proposal_GDF.loc[pred_row.name, iou_field] = max_iou_row['iou_score']
                            self.ground_truth_GDF_Edit = self.ground_truth_GDF_Edit.drop(max_iou_row.name, axis=0)

                        else:

                            self.proposal_GDF.loc[pred_row.name, iou_field] = 0
                    else:
                        self.proposal_GDF.loc[pred_row.name, iou_field] = 0
                else:
                    self.proposal_GDF.loc[pred_row.name, iou_field] = 0

                if debug:
                    print(self.proposal_GDF.loc[pred_row.name])



            if self.proposal_GDF.empty:
                TruePos = 0
                FalsePos = 0
            else:
                #if True: #try:
                proposal_GDF_copy = self.proposal_GDF[self.proposal_GDF[imageIDField] == imageID].copy(deep=True)
                proposal_GDF_copy = proposal_GDF_copy[proposal_GDF_copy.area>minArea]

                if not proposal_GDF_copy.empty:

                    if iou_field in proposal_GDF_copy.columns:
                        TruePos = proposal_GDF_copy[proposal_GDF_copy[iou_field]>=miniou].shape[0]
                        FalsePos = proposal_GDF_copy[proposal_GDF_copy[iou_field]<miniou].shape[0]
                    else:
                        print("iou field {} missing".format(iou_field))
                        TruePos = 0
                        FalsePos = 0
                else:
                    print("Empty Proposal Id")
                    TruePos = 0
                    FalsePos = 0


            FalseNeg = self.ground_truth_GDF_Edit[self.ground_truth_GDF_Edit.area>0].shape[0]

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

            score_calc = {'imageID': imageID,
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




    def eval_iou(self, miniou=0.5, iou_field_prefix='iou_score',
                 ground_truth_class_field='',
                 calculate_class_scores=True,
                 class_list=['all'],

                 ):



        scoring_dict_list = []
        if calculate_class_scores:
            class_list.extend(list(self.ground_truth_GDF[ground_truth_class_field].unique()))
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




            self.proposal_GDF

            for idx, pred_row in tqdm(self.proposal_GDF.iterrows()):

                if pred_row['__max_conf_class'] == class_id or class_id=='all':
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
                      pred_row_geo_value='PolygonWKT_Pix',
                      conf_field_mapping=[]):

        ## Load Proposal
        if os.path.isfile(proposal_vector_file):
            if proposalCSV:
                pred_data = pd.read_csv(proposal_vector_file)
                self.proposal_GDF = gpd.GeoDataFrame(pred_data,
                                            geometry=[shapely.wkt.loads(pred_row[pred_row_geo_value]) for idx, pred_row in
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

    def load_truth(self, ground_truth_vector_file, truthCSV=False, truth_geo_value='PolygonWKT_Pix'):

        if truthCSV:
            truth_data = pd.read_csv(ground_truth_vector_file)
            self.ground_truth_GDF = gpd.GeoDataFrame(truth_data,
                                                 geometry=[shapely.wkt.loads(truth_row[truth_geo_value]) for idx, truth_row
                                                           in
                                                           truth_data.iterrows()])
        else:
            try:
                self.ground_truth_GDF = gpd.read_file(ground_truth_vector_file)
            except CPLE_OpenFailedError:  # handles empty geojson
                self.ground_truth_GDF = gpd.GeoDataFrame({'sindex': [],
                                                          'condition': [],
                                                          'geometry': []})

        # force calculation of spatialindex
        self.ground_truth_sindex = self.ground_truth_GDF.sindex
        ## create deep copy of ground truth file for calculations

        self.ground_truth_GDF_Edit = self.ground_truth_GDF.copy(deep=True)

        return 0


    def eval(self, type='iou'):

        pass
