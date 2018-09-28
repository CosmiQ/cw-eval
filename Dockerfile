FROM cosmiqworks/spacenet-utilities-cpu

MAINTAINER Dlindenbaum <dlindenbaum@iqt.org>


## Install General Requirements
RUN pip install pandas && pip install git+https://github.com/CosmiQ/cw_eval.git
