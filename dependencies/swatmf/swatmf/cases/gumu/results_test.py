import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
from swatmf import analyzer
from swatmf import handler
from tqdm import tqdm
from swatmf import swatmf_pst_utils, gumu_pst_utils, hg
# from swatmf.hg.hg_handler import h

# user custimized plot
def temp_plot(stf_obd_df, obd_col, wb_df, viz_ts, gw_df, grid_id, gw_obd_df, gw_obd_col):
    """_summary_

    :param stf_obd_df: handler.get_stf_sim_obd
    :type stf_obd_df: dataframe
    :param obd_col: obd name
    :type obd_col: stf
    :param wb_df: handler.get_std_data
    :type wb_df: dataframe
    :param viz_ts: time step
    :type viz_ts: stf
    :param gw_df: handler.get_gw_sim
    :type gw_df: dataframe
    :param grid_id: grid_id name
    :type grid_id: str
    :param gw_obd_df: handler.get_gw_obd
    :type gw_obd_df: dataframe
    :param gw_obd_col: column name
    :type gw_obd_col: str
    """
    fig = plt.figure(figsize=(10,10))
    subplots = fig.subfigures(
                                4, 1, height_ratios=[0.2, 0.2, 0.2, 0.4],
                            #   hspace=-0.05
                            )

    ax0 = subplots[0].subplots(1,1)
    ax1 = subplots[1].subplots(1,2, sharey=False, 
                    gridspec_kw={
                    # 'height_ratios': [0.2, 0.2, 0.4, 0.2],
                    'wspace': 0.0
                    })
    ax2 = subplots[2].subplots(1,2, sharey=False, 
                    gridspec_kw={
                    # 'height_ratios': [0.2, 0.2, 0.4, 0.2],
                    'wspace': 0.0
                    })
    ax3 = subplots[3].subplots(4,1, sharex=True, height_ratios=[0.2, 0.2, 0.4, 0.2])
    # ax3 = subplots[1][1].subplots(2,5)

    # streamflow
    ax0.set_ylabel(r'Stream Discharge $[m^3/s]$', fontsize=8)
    ax0.tick_params(axis='both', labelsize=8)
    analyzer.plot_stf_sim_obd(ax0, stf_obd_df, obd_col)
    # '''
    analyzer.plot_gw_sim_obd(ax1[0], gw_df, "sim_g3685lyr1", gw_obd_df, "obd3685")
    analyzer.plot_gw_sim_obd(ax1[1], gw_df, "sim_g5687lyr1", gw_obd_df, "obd5687")
    # plot_gw_sim_obd(ax2[0], gw_df, "sim_g1203lyr2", gw_obd_df, "g1203lyr2")
    # plot_gw_sim_obd(ax2[1], gw_df, "sim_g1205lyr2", gw_obd_df, "g1205lyr2")
    analyzer.plot_gw_sim_obd(ax2[0], gw_df, "sim_g5617lyr1",gw_obd_df, "obd5617")
    analyzer.plot_gw_sim_obd(ax2[1], gw_df, "sim_g5001lyr1", gw_obd_df, "obd5001")
    # '''
    analyzer.std_plot(ax3, wb_df, viz_ts)
    plt.show()


def hg_balance():
    # sub interaction: convert kg to g
    df1 = mod1.hg_sub_inter2*1000
    df1 = df1[cal_start:cal_end].sum(axis=1)
    dfm = df1.resample('ME').sum()
    dfm = dfm.groupby(dfm.index.month).mean()
    print( '- '*10+ "Hg contribution from GW" + '- '*10)
    print(dfm)
    dft = dfm.sum()
    print('{:.2f}g/year'.format(dft))


def hg_sub_contrb():
    # sub interaction: convert mg to g
    df2 = mod1.hg_sub_contr*0.001
    df2 = df2[cal_start:cal_end]
    dfm2 = df2.resample('ME').sum()
    dfm2 = dfm2.groupby(dfm2.index.month).mean()
    print( "\n"+'- '*10+ "Hg contribution from Surface" + '- '*10)
    print(dfm2)
    print(dfm2.sum(axis=0))
    dft2 = dfm2.iloc[:, :-1].sum().sum()
    print('- '*10)
    print('{:.2f}g/year'.format(dft2))

def hg_yield():
    # yield
    hg_yld = mod1.hg_yield(1)[cal_start:cal_end].sum(axis=1)*0.001 # mg to g
    hg_yldm = hg_yld.resample('ME').sum()
    hg_yldm = hg_yldm.groupby(hg_yldm.index.month).mean()
    print( "\n"+'- '*10+ "Hg Yield" + '- '*10)
    print(hg_yldm)
    print('- '*10)
    hg_yldmtot = hg_yldm.sum()
    print('{:.2f}g/year'.format(hg_yldmtot))

def hg_rch():

    hg_yld = mod1.hg_rch([1])[cal_start:cal_end].sum(axis=1)*0.001 # mg to g
    hg_yldm = hg_yld.resample('ME').sum()
    hg_yldm = hg_yldm.groupby(hg_yldm.index.month).mean()
    print( "\n"+'- '*10+ "Hg rch " + '- '*10)
    print(hg_yldm)
    print('- '*10)
    hg_yldmtot = hg_yldm.sum()
    print('{:.2f}g/year'.format(hg_yldmtot))


def plot_():
    # stf
    hg.Viz().barToOne(
        dates_wt_df, hg_wt_obds,
        [0, 10], [0, 10], 
        dates=hg_wt_dates,
        xlabel='Observed Hg in Stream $(ppb)$', ylabel='Simulated Hg in Stream $(ppb)$',
        output='hgInStr.jpg')
    # sed
    hg.Viz().barToOne(
        hg_sed_dff, sed_obds,
        [0, 120], [0, 120], 
        width=5, xlabel='Observed Hg in Sediment $(ppm)$', ylabel='Simulated Hg in Sediment $(ppm)$',
        output='hgInSed.jpg')
    # groundwater
    hg.Viz().gwlv(
        gw_df, 'sim_wt', 'obd_wt', [17, 35],[17, 35],
        xlabel='Simulated', ylabel='Observed',
    )


def gw_hyd():
    fig, ax= plt.subplots(figsize=(12,4))
    for g in grids:
        gw01 = gw_df.loc[gw_df['grid'] == "g{}".format(g)]
        ax.plot(gw01.index, gw01.sim_wt, c='k')
        ax.scatter(
                gw01.index, gw01.obd_wt,
                s=60,
                lw=1.5,
                alpha=0.3,
    #             zorder=10,
                marker='o',
                label='g{}'.format(g)
        )
    ax.tick_params(axis='both', labelsize=14)
    ax.legend(fontsize=18, loc='lower left',
    #           bbox_to_anchor=(1.35, 0)
            )
    # ax.set_xlabel('Simulated Groundwater Head $(m)$', fontsize=16)
    ax.set_ylabel('Groundwater Head $(m)$', fontsize=16)
    plt.savefig('gumu_gw2.jpg', dpi=300, bbox_inches="tight")
    plt.show()

def gw_hyd_sep():
    gw01 = gw_df.loc[gw_df['grid'] == "g3685"]
    gw02 = gw_df.loc[gw_df['grid'] == "g5001"]
    gw03 = gw_df.loc[gw_df['grid'] == "g5617"]
    gw04 = gw_df.loc[gw_df['grid'] == "g5687"]
    fig, axes= plt.subplots(figsize=(12,6), nrows=2, ncols=2)
    axes[0, 0].plot(gw01.index, gw01.sim_wt)
    axes[0, 0].scatter(
            gw01.index, gw01.obd_wt,
            s=60, lw=1.5, alpha=0.5, zorder=10, marker='o',
    )
    axes[0, 0].set_ylim(29, 36)
    axes[0, 1].plot(gw02.index, gw02.sim_wt, c='orange', alpha=.5)
    axes[0, 1].scatter(
            gw02.index, gw02.obd_wt,
            s=60, lw=1.5, alpha=0.5, zorder=10, marker='o', c='orange'
    )
    axes[0, 1].set_ylim(18, 19)
    axes[1, 0].plot(gw03.index, gw03.sim_wt, c='g', alpha=.5)
    axes[1, 0].scatter(
            gw03.index, gw03.obd_wt,
            s=60, lw=1.5, alpha=0.5, zorder=10, marker='o', c='g',
    )
    axes[1, 0].set_ylim(26, 27)
    axes[1, 1].plot(gw04.index, gw04.sim_wt, c='r', alpha=.5)
    axes[1, 1].scatter(
            gw04.index, gw04.obd_wt,
            s=60, lw=1.5, alpha=0.5, zorder=10, marker='o',c='r'
    )
    # axes[1, 1].set_ylim(32.5, 33.5)
    date_form = DateFormatter("%Y\n%b%d")
    for ax in axes.flat:
        ax.margins(y=0.5, x=0.5)
        ax.xaxis.set_major_formatter(date_form)
        
    plt.tight_layout()
    plt.show()


def temp():
    hg_sub_df = pd.read_csv("output-mercury.sub",
                        sep=r'\s+',
                        skiprows=2,
                        usecols=[
                            "SUB", "AREAkm2",
                            "Hg0SurfqDs", "Hg2SurfqDs", "MHgSurfqDs",
                            "Hg0LatlqDs", "Hg2LatlqDs", "MHgLatlqDs",
                            "Hg0PercqDs", "Hg2PercqDs", "MHgPercqDs",
                            "Hg0SedYlPt", "Hg2SedYlPt", "MHgSedYlPt",
                            ],
                        index_col=0
                    )
    hg_sub_dff = pd.DataFrame()
    for s in [i for i in range(1, 16)]:
        hg_str_sed_df = hg_sub_df.loc[hg_sub_df["SUB"] == int(s)]
        hg_str_sed_df.index = pd.date_range("1/1/2010", periods=len(hg_str_sed_df))
        hg_str_sed_df = hg_str_sed_df.drop('SUB', axis=1)
        hg_sub_dff = hg_sub_dff.add(hg_str_sed_df, fill_value=0)
    
    hg_sub_dff["Hg0SurfqDs_"] = hg_sub_dff["Hg2SedYlPt"] / hg_sub_dff["AREAkm2"] * 0.01
    
    print(hg_sub_dff["Hg2SedYlPt"].sum())





# def plot_tot():
if __name__ == '__main__':

    wd = "D:\\Projects\\Watersheds\\Gumu\\Analysis\\SWAT-MODFLOWs\\calibrations\\gumu_pp_glm"
    os.chdir(wd)
    # temp()
    mod1 = hg.Hg(wd)
    sim_start = '1/1/2010'
    cal_start = '1/1/2011'
    cal_end = '5/5/2022'

    # observation info
    stf_obd_file = "stf_day.obd.csv"
    subnums = [1, 3, 4, 5, 11, 13]
    obd_cols = [f'sub{i:03d}' for i in subnums]
    m1 = handler.SWATMFout(wd)

    df = pd.DataFrame()

    for subnum, obd_col in zip(subnums, obd_cols):
        so = m1.get_stf_sim_obd(stf_obd_file, obd_col, subnum)
        so.columns = ['stf_sim', 'obd']
        so['sub'] = obd_col
        df = pd.concat([df, so], axis=0)

    # print(df)
    # # groundwater
    # grids = [3685, 5687, 5617, 5001]
    
    # obd_cols = ['obd3685', 'obd5687', 'obd5617', 'obd5001']
    # # obd_cols = ['gw1', 'mw03', 'mw02', 'mw01']
    # elevs = [34.81, 34.57, 31.61,  22.63]
    # gw_df = mod1.gw_levels(grids, obd_cols, elevs=elevs)
    # # gw_df = gw_df[cal_start:cal_end]
    # print(gw_df)
    # for i in [f'g{i}' for i in grids]:
    #     analyzer.dtw_1to1_plot(gw_df.loc[gw_df['grid']==i])

    wb_df = m1.get_std_data()
    viz_ts = "month"
    gw_df = m1.get_gw_sim()
    grid_id = "a"
    gw_obd = m1.get_gw_obd()
    gw_obd_col = "b"
    temp_plot(df, 'obd', wb_df, viz_ts, gw_df, grid_id, gw_obd, gw_obd_col)
    print(gw_obd)

    # HG in stream
    hg_wt_subs = [3,4,9,11]
    hg_wt_dates = [
        '6/3/2020', '9/21/2020', '12/7/2020', '3/3/2021', '8/30/2021',
    #     '2/7/2022', '3/17/2022', '3/18/2022', '3/19/2022'
    ]
    hg_wt_obds = [4.58, 5.96, 8.32, 4.22] # till 2022
    # hg_wt_obds = [6.56, 3.60, 6.26 , 2.91]

    hg_wt_df = mod1.hg_rch(hg_wt_subs)
    dates_wt_df = hg_wt_df.loc[hg_wt_dates]

    # Sediment1
    hg_sed_subs = [2,3,4,5,9,11]
    hg_sed_cols = ['hg_sed{:03d}'.format(i) for i in hg_sed_subs]
    hg_sed_dates = ['6/30/2020', '12/31/2020', '11/30/2021', '2/28/2022'] # monthly average
    # sed_obds = [13.5, 13.3, 20.4, 32.9, 75.6, 113.9]
    sed_obds = [20.3, 23.3, 23.5, 32.1, 68.5, 95.1] # till 2022 feb
    sed_df = mod1.hg_sed(hg_sed_subs)
    sed_df = sed_df[cal_start:cal_end]
    jun_df = sed_df[(sed_df.index.month == 6)]
    dec_df = sed_df[(sed_df.index.month == 12)]
    nov_df = sed_df[(sed_df.index.month == 11)]
    hg_sed_dff = pd.concat([jun_df, dec_df, nov_df], axis=0)



    # plot_()
    # gw_hyd()
    # gw_hyd_sep()

    hg_balance()
    hg_sub_contrb()
    hg_yield()
    hg_rch()


    # # sub interaction: convert kg to g
    # df1 = mod1.hg_sub_gw_sw_inter2
    # df1 = df1[cal_start:cal_end].sum(axis=1)
    # dfm = df1.resample('ME').sum()
    # dfm = dfm.groupby(dfm.index.month).mean()
    # print( '- '*10+ "GW/SW Interaction (m3/month)" + '- '*10)
    # print(dfm)
    # dft = dfm.sum()
    # print('{:.2f}m3/year'.format(dft))
    '''
    '''

