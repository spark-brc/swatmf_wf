import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
from tqdm import tqdm
from swatmf import swatmf_pst_utils, gumu_pst_utils, hg
# from swatmf.hg.hg_handler import h




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



# def plot_tot():
if __name__ == '__main__':
    # wd01 = "d:\\Projects\\Watersheds\\Gumu\\Analysis\\SWAT-MODFLOWs\\dataset_220720\\dataset" # same as dataset_20240625_v01
    # wd02 = "D:\\Projects\\Models\\swatmf-Hg_temp\\Hg_bailey (1)\\dataset" # same as dataset_20240625_v01
    # wd01 = "D:\\Projects\\Models\\swatmf-Hg_temp\\dataset_w_rch" # same as dataset_20240625_v01
    # wd01 = "D:\\Projects\\Models\\swatmf-Hg_temp\\dataset_w_rch" # same as dataset_20240625_v01
    
    wd = "d:\\Projects\\Watersheds\\Gumu\\Analysis\\SWAT-MODFLOWs\\dataset_20240625_v01"
    os.chdir(wd)
    mod1 = hg.Hg(wd)
    sim_start = '1/1/2010'
    cal_start = '1/1/2015'
    cal_end = '12/31/2021'

    # observation info
    # stream
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

    # groundwater
    grids = [3685, 5001, 5617, 5687]
    obd_cols = ['gw1', 'mw03', 'mw02', 'mw01']
    elevs = [34.81, 22.63, 31.61, 34.57]
    gw_df = mod1.gw_levels(grids, obd_cols, elevs=elevs)
    # gw_df = gw_df[cal_start:cal_end]
    print(gw_df)


    plot_()
    gw_hyd()
    gw_hyd_sep()

    # hg_balance()
    # hg_sub_contrb()
    # hg_yield()
    # hg_rch()


    # # sub interaction: convert kg to g
    # df1 = mod1.hg_sub_gw_sw_inter2
    # df1 = df1[cal_start:cal_end].sum(axis=1)
    # dfm = df1.resample('ME').sum()
    # dfm = dfm.groupby(dfm.index.month).mean()
    # print( '- '*10+ "GW/SW Interaction (m3/month)" + '- '*10)
    # print(dfm)
    # dft = dfm.sum()
    # print('{:.2f}m3/year'.format(dft))



