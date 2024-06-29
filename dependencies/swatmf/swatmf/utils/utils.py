""" SWATMF support functions: 02/09/2021 created by Seonggyu Park
    last modified day: 03/21/2021 by Seonggyu Park
"""

import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import os
# from hydroeval import evaluator, nse, rmse, pbias
# import numpy as np
import numpy as np
# import h5py as hdf
import os 
import datetime
from tqdm import tqdm

def obds_df(strobd_file, wt_obd_file):
    str_obd = pd.read_csv(
                        strobd_file, sep=r'\s+', index_col=0, header=0,
                        parse_dates=True, delimiter="\t",
                        na_values=[-999, ""]
                        )
    wt_obd = pd.read_csv(
                        'MODFLOW/' + wt_obd_file, sep=r'\s+', index_col=0, header=0,
                        parse_dates=True, delimiter="\t",
                        na_values=[-999, ""]
                        )
    if strobd_file == 'swat_rch_mon.obd':
        str_obd = str_obd.resample('M').mean()
    if wt_obd_file == 'modflow_mon.obd':
        wt_obd = wt_obd.resample('M').mean()

    df = pd.concat([str_obd, wt_obd], axis=1)
    return df
    

# NOTE: let's implement it in QSWATMOD
def export_gwsw_swatToExcel(wd, startDate, scdate, ecdate, nsubs):

    filename = "swatmf_out_SWAT_gwsw_monthly"
    data = np.loadtxt(
                    os.path.join(wd, filename),
                    skiprows=2,
                    comments=["month:", "Layer"])
    df = np.reshape(data[:, 1], (int(len(data)/nsubs), nsubs))
    df2 = pd.DataFrame(df)
    df2.index = pd.date_range(startDate, periods=len(df[:,0]), freq='M')
    df2 = df2[scdate:ecdate]
    mdf = df2.groupby(df2.index.month).mean()
    mdf = mdf.T
    mdf.columns = [
                'Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']

    mdf.insert(0, "rchno", [x+1 for x in mdf.index] , True)
    mdf.to_excel('{}.xlsx'.format(filename), index=False)
    print(mdf)
