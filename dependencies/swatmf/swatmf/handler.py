""" PEST support visualizations: 02/09/2021 created by Seonggyu Park
    last modified day: 02/21/2021 by Seonggyu Park
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
# from hydroeval import evaluator, nse, rmse, pbias
import numpy as np
import math


# NOTE: swat output handler
class SWATMFout(object):

    def __init__(self, wd):
        os.chdir(wd)

    # scratches for QSWATMOD
    # read data first
    def read_stf_obd(self, obd_file):
        return pd.read_csv(obd_file,
            index_col=0,
            header=0,
            parse_dates=True,
            na_values=[-999, ""]
        )

    def read_output_rch_data(self, colNum=6):
        return pd.read_csv(
            "output.rch",
            sep=r'\s+',
            skiprows=9,
            usecols=[1, 3, colNum],
            names=["date", "filter", "stf_sim"],
            index_col=0
        )

    def update_index(self, df, startDate, ts):
        if ts.lower() == "day":
            df.index = pd.date_range(startDate, periods=len(df.stf_sim))
        elif ts.lower() == "month":
            df = df[df['filter'] < 13]
            df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="M")
        else:
            df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="A")
        return df

    def get_stf_sim(colNum=6):
        return pd.read_csv(
            "output.rch",
            sep=r'\s+',
            skiprows=9,
            usecols=[1, 3, colNum],
            names=["date", "filter", "stf_sim"],
            index_col=0
        )        

    def get_stf_sim_obd(self, obd_file, obd_col, subnum, startDate, ts):
        strObd = self.read_stf_obd(obd_file)
        output_rch = self.read_output_rch_data()
        df = output_rch.loc[subnum]
        df = self.update_index(df, startDate, ts)
        df2 = pd.concat([df, strObd[obd_col]], axis=1)
        df3 = df2.dropna()
        return df3




