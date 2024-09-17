import os
import matplotlib.pyplot as plt
import pyemu
from swatmf import analyzer
import pandas as pd
from swatmf import handler
from swatmf.utils import mf_configs



if __name__ == '__main__':
    # wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_swatmf\\m05-base_manual01"
    wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\calibration\\7th\\koki_ies"
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
    # subnum = [195, 195, 3, 3]
    # sims = ["sim_g249lyr2", "sim_g249lyr3", "sim_g1203lyr3", "sim_g1205lyr3"]
    # obds = ["obd249lyr2", "obd249lyr3", "obd1203lyr3", "obd1205lyr3"]

    # gw_df = m1.get_gw_sim()
    # gw_obd = m1.get_gw_obd()
    # analyzer.plot_gw_sim_obd(ax1[0], gw_df, "sim_g249lyr2", gw_obd_df, "obd249lyr2")



    # for s, o, p in zip(sims, obds, subnum):
    #     sdf = gw_df.loc[:, s]
    #     obd = gw_obd.loc[:, o]
    #     prep = m1.temp_sup(p)
    #     analyzer.dtw_plot(sdf, obd, prep)


    # # static waterlevels
    # static_dtw = pd.read_csv('dtw_sim_static.txt', comment="#", sep=r'\s+')
    # static_dtw = static_dtw.loc[static_dtw['sim'] < 0]
    # print(static_dtw)
    # static_dtw = static_dtw.drop(13)
    # static_dtw = static_dtw.drop(4)
    # print(static_dtw)
    # analyzer.dtw_1to1_plot_(static_dtw)


    # outputstd
    # fig = plt.figure(figsize=(10,10))
    wb_df = m1.get_std_data()
    viz_ts = "month"
    fig, ax = plt.subplots()
    subplots = fig.subfigures(
                            4, 1, height_ratios=[0.2, 0.2, 0.2, 0.4],
                        #   hspace=-0.05
                        )
    ax3 = subplots[3].subplots(4,1, sharex=True, height_ratios=[0.2, 0.2, 0.4, 0.2])
    analyzer.output_std_plot(ax3, wb_df, viz_ts)
    plt.show()





