import os
import matplotlib.pyplot as plt
import pyemu
from swatmf import analyzer
import pandas as pd
from swatmf import handler
from swatmf.utils import mf_configs



if __name__ == '__main__':
    # wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_swatmf\\m05-base_manual01"
    wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_swatmf\\m05-base_rel269"
    m1 = handler.SWATMFout(wd)
    
    '''
    # streamflow
    stf_obd_file = "stf_day.obd.csv"
    obd_col = "sub68"
    subnum = 68
    stf_sim_obd = m1.get_stf_sim_obd(stf_obd_file, obd_col, subnum)
    prep = m1.temp_sup(subnum)
    dff = pd.concat([stf_sim_obd, prep], axis=1).dropna()
    # print(dff.dropna())

    # caldf = dff['1/1/2016':'12/31/2022']
    # analyzer.str_plot_test(dff, cal_period=cal_st)
    analyzer.str_plot(dff, prep=True)
    analyzer.single_fdc(dff)
    analyzer.str_plot(dff.resample('M').mean(), prep=True)
    # analyzer.single_fdc(dff.resample('M').mean())
    '''
    # for groundwater levels
    gw_df = m1.get_gw_sim()
    print(gw_df)
