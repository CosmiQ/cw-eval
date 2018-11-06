# CosmiQ-Works-Eval Tools

This package is purpose built to support evaluation of Machine Learning DataSets in GeoSpatial settings.  The geoTools packages is intended to assist in the preprocessing of [SpaceNet](https://spacenetchallenge.github.io/) satellite imagery data corpus hosted on [SpaceNet on AWS](https://aws.amazon.com/public-datasets/spacenet/) to a format that is consumable by machine learning algorithms. 
The evalTools package is used to evaluate the effectiveness of object detection algorithms using ground truth.
The labelTools package assists in transfering geoJson labels into common label schemes for machine learning frameworks
This is version 3.0 and has been updated with more capabilities to allow for computer vision applications using remote sensing data

## Download Instructions
Further download instructions for the [SpaceNet Dataset](https://github.com/SpaceNetChallenge/utilities/tree/master/content/download_instructions) can be found [here](https://github.com/SpaceNetChallenge/utilities/tree/master/content/download_instructions)



## Installation Instructions
Several packages require binaries to be installed before pip installing the other packages.  Conda is a simple way to install everything and their dependencies

Rtree is required as a dependency  
* Install [Rtree](http://toblerity.org/rtree/install.html) 
```commandline 
conda install -c conda-forge rtree
```

* Pip Install from github 
```commandline
    git clone https://github.com/CosmiQ/cw-eval.git
    cd cw-eval
    pip install -e .
    
```

or 
```commandline
    pip install --upgrade git+https://github.com/CosmiQ/cw-eval.git
```

## To run the metric you can use the following command.
```
spacenet_eval --help

spacenet_eval --proposalcsv ./TestCases_SpaceNet4/AOI_6_Atlanta_Test_v3_prop_1extra.csv \
              --truthcsv ./TestCases_SpaceNet4/AOI_6_Atlanta_Test_v3.csv \
              --challenge off-nadir \
              --output_file test.csv
```


## Use our Docker Container
```
docker pull cosmiqworks/cw-eval

```


## Evaluation Metric
The evaluation metric for this competition is an F1 score with the matching algorithm inspired by Algorithm 2 in the [ILSVRC paper applied to the detection of building footprints](https://arxiv.org/pdf/1409.0575v3.pdf). For each building there is a geospatially defined polygon label to represent the footprint of the building. A SpaceNet entry will generate polygons to represent proposed building footprints.  Each proposed building footprint is either a “true positive” or a “false positive”.

* The proposed footprint is a “true positive” if the proposal is the closest (measured by the IoU) proposal to a labeled polygon AND the IoU between the proposal and the label is about the prescribed threshold of 0.5.
* Otherwise, the proposed footprint is a “false positive”.

There is at most one “true positive” per labeled polygon.
The measure of proximity between labeled polygons and proposed polygons is the Jaccard similarity or the “Intersection over Union (IoU)”, defined as:

![alt text](https://github.com/SpaceNetChallenge/utilities/blob/master/content/IoU.jpg "IoU")

The value of IoU is between 0 and 1, where closer polygons have higher IoU values.

The F1 score is the harmonic mean of precision and recall, combining the accuracy in the precision measure and the completeness in the recall measure. For this competition, the number of true positives and false positives are aggregated over all of the test imagery and the F1 score is computed from the aggregated counts.

For example, suppose there are N polygon labels for building footprints that are considered ground truth and suppose there are M proposed polygons by an entry in the SpaceNet competition.  Let tp denote the number of true positives of the M proposed polygons.  The F1 score is calculated as follows:

![alt text](https://github.com/SpaceNetChallenge/utilities/blob/master/content/F1.jpg "IoU")

The F1 score is between 0 and 1, where larger numbers are better scores.

Hints:
* The images provided could contain anywhere from zero to multiple buildings.
* All proposed polygons should be legitimate (they should have an area, they should have points that at least make a triangle instead of a point or a line, etc).
* Use the [metric implementation code](https://github.com/SpaceNetChallenge/utilities/blob/master/python/evaluateScene.py) to self evaluate.
To run the metric you can use the following command.
```
spacenet_eval --help

spacenet_eval --proposalcsv /Users/dlindenbaum/Downloads/TestCases_SpaceNet4/AOI_6_Atlanta_Test_v3_prop_1extra.csv \
              --truthcsv /Users/dlindenbaum/Downloads/TestCases_SpaceNet4/AOI_6_Atlanta_Test_v3.csv \
              --challenge off-nadir \
              --output_file test.csv
```


## Use our Docker Container
```
docker pull cosmiqworks/cw-eval

```


## Dependencies
All dependencies can be found in the docker file [Dockerfile](./Dockerfile)

## License
See [LICENSE](./LICENSE).
