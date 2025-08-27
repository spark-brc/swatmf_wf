import os
import matplotlib.pyplot as plt
from datetime import datetime
import pyemu
import pandas as pd
from swatmf.handler import SWATMFout
from swatmf.utils import swat_configs
from swatmf.utils import mf_configs
from swatmf import swatmf_pst_utils
from swatmf import analyzer

def time_stamp(des):
    time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
    print('\n' + 35*'+ ')
    print(time + ' |  {} ...'.format(des))
    print(35*'+ ' + '\n')

def update_swat_pars(wd):
    des = "updating SWAT parameters"
    time_stamp(des)
    # update SWAT parameters
    m1 = swat_configs.SwatEdit(wd)
    subbasins = m1.read_subs()
    new_parms = m1.read_new_parms()
    m1.param = [new_parms]
    m1.subbasins = [subbasins]
    m1.update_swat_parms()

def execute_swatmf(wd):
    des = "running model"
    time_stamp(des)
    pyemu.os_utils.run('swatmf_rel230922.exe', cwd=wd)

def extract_stf_results(time_step, subs, sim_start, warmup, cal_start, cal_end):
    if time_step == 'day':
        des = "simulation successfully completed | extracting daily simulated streamflow"
        time_stamp(des)
        swatmf_pst_utils.extract_day_stf(subs, sim_start, warmup, cal_start, cal_end)
    elif time_step == 'month':
        des = "simulation successfully completed | extracting monthly simulated streamflow"
        time_stamp(des)
        swatmf_pst_utils.extract_month_stf(subs, sim_start, warmup, cal_start, cal_end)

def extract_gw_level_results(grids, sim_start, cal_end):
    des = "simulation successfully completed | extracting depth to water values"
    time_stamp(des)
    swatmf_pst_utils.extract_depth_to_water(grids, sim_start, cal_end)

def extract_avg_depth_to_water(
                avg_grids, start_day, 
                avg_stdate, avg_eddate,
                ):
    des = "simulation successfully completed | extracting average depth to water values"
    time_stamp(des)
    swatmf_pst_utils.extract_avg_depth_to_water(
                                avg_grids, start_day, 
                                avg_stdate, avg_eddate,
                                time_step="day")

def extract_baseflow_results(subs, sim_start, cal_start, cal_end):
    des = "simulation successfully completed | calculating baseflow ratio"
    time_stamp(des)
    swatmf_pst_utils.extract_month_baseflow(subs, sim_start, cal_start, cal_end)



def update_swatpar(wd):
    os.chdir(wd)
    swatmf_con = pd.read_csv(
        'swatmf.con', sep='\t', names=['names', 'vals'], index_col=0, comment="#"
        )
    # update SWAT parameters
    update_swat_pars(wd)

    # modifying river pars
    if swatmf_con.loc['riv_parm', 'vals'] != 'n':
        rivmf = mf_configs.mfEdit(wd)
        mf_configs.write_new_riv()



def extract_results(wd):
    os.chdir(wd)
    swatmf_con = pd.read_csv(
        'swatmf.con', sep='\t', names=['names', 'vals'], index_col=0, comment="#"
        )
    sim_start = swatmf_con.loc['sim_start', 'vals']
    warmup = swatmf_con.loc['warm-up', 'vals']
    cal_start = swatmf_con.loc['cal_start', 'vals']
    cal_end = swatmf_con.loc['cal_end', 'vals']
    cha_act = swatmf_con.loc['subs','vals']
    grid_act = swatmf_con.loc['grids','vals']
    riv_parm = swatmf_con.loc['riv_parm', 'vals']
    baseflow_act = swatmf_con.loc['baseflow', 'vals']
    time_step = swatmf_con.loc['time_step','vals']
    pp_act = swatmf_con.loc['pp_included', 'vals']

    if swatmf_con.loc['subs', 'vals'] != 'n':
        subs = swatmf_con.loc['subs','vals'].strip('][').split(', ')
        subs = [int(i) for i in subs]
        extract_stf_results(time_step, subs, sim_start, warmup, cal_start, cal_end)
    if swatmf_con.loc['grids', 'vals'] != 'n':
        grids = swatmf_con.loc['grids','vals'].strip('][').split(', ')
        grids = [int(i) for i in grids]        
        extract_gw_level_results(grids, sim_start, cal_end)

    if swatmf_con.loc['grids_lyrs', 'vals'] !='n':
        # grids = swatmf_con.loc['grids_lyrs','vals'].strip('][').split(', ')
        # grids = [int(i) for i in grids] 
        m1 = SWATMFout(wd)
        df =  m1.get_gw_sim()
        for col in df.columns:
            df.loc[:, col].to_csv(
                            '{}.txt'.format(col), sep='\t', encoding='utf-8',
                            index=True, header=False, float_format='%.7e'
                            )
        print("GW sim extraction finished ...")


def get_stf_sim_obd(wd, stf_obd_file, obd_col, subnum):
    m1 = SWATMFout(wd)
    stf_sim_obd = m1.get_stf_sim_obd(stf_obd_file, obd_col, subnum)
    # # stf_sim_obd.drop("filter", axis=1, inplace=True)
    # # analyzer.str_sim_obd(stf_sim_obd)
    return stf_sim_obd


def temp_plot(stf_sim_obd, obd_col, wb_df, viz_ts, gw_df, grid_id, gw_obd, gw_obd_col):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    stf_sim_obd.plot(x='date', y=obd_col, ax=ax[0], color='blue', label='Simulated')
    wb_df.plot(x='date', y=obd_col, ax=ax[0], color='red', label='Observed')
    gw_df.plot(x='date', y=gw_obd_col, ax=ax[1], color='green', label='GW Level')
    ax[0].set_title(f'Subbasin {obd_col} Streamflow')
    ax[1].set_title(f'Grid {grid_id} Groundwater Level')
    plt.legend()
    plt.show()


def plot_temp(wd, subnum, stf_obd, stf_obd_file="stf_day.obd.csv", viz_ts="month"):
    m1 = SWATMFout(wd)
    wb_df = m1.get_std_data()
    gw_df = m1.get_gw_sim()
    gw_obd = m1.get_gw_obd()
    stf_sim_obd = m1.get_stf_sim_obd(stf_obd_file, stf_obd, subnum)


    fig = plt.figure(figsize=(10,10))
    subplots = fig.subfigures(4, 1, height_ratios=[0.2, 0.2, 0.2, 0.4])
    ax0 = subplots[0].subplots(1,1)
    ax1 = subplots[1].subplots(1,2, sharey=False, 
                    gridspec_kw={
                    'wspace': 0.0
                    })
    ax2 = subplots[2].subplots(1,2, sharey=False, 
                    gridspec_kw={
                    'wspace': 0.0
                    })
    ax3 = subplots[3].subplots(4,1, sharex=True, height_ratios=[0.2, 0.2, 0.4, 0.2])

    # streamflow
    ax0.set_ylabel(r'Stream Discharge $[m^3/s]$', fontsize=8)
    ax0.tick_params(axis='both', labelsize=8)
    analyzer.plot_stf_sim_obd(ax0, stf_sim_obd, stf_obd)
    analyzer.plot_gw_sim_obd(ax1[0], gw_df, "sim_g2801lyr1", gw_obd, "gid2801")
    analyzer.output_std_plot(ax3, wb_df, viz_ts)
    plt.show()


def plot_temp_hjc(wd, subnum, stf_obd, stf_obd_file="stf_day.obd.csv", viz_ts="month"):
    m1 = SWATMFout(wd)
    wb_df = m1.get_std_data()
    gw_df = m1.get_gw_sim()
    gw_obd = m1.get_gw_obd()
    stf_sim_obd = m1.get_stf_sim_obd(stf_obd_file, stf_obd, subnum)


    fig = plt.figure(figsize=(10,10))
    subplots = fig.subfigures(3, 1, height_ratios=[0.3, 0.3, 0.4])
    ax0 = subplots[0].subplots(1,1)
    ax1 = subplots[1].subplots(1,1, sharey=False, 
                    gridspec_kw={
                    'wspace': 0.0
                    })
    ax3 = subplots[2].subplots(4,1, sharex=True, height_ratios=[0.2, 0.2, 0.4, 0.2])

    # streamflow
    ax0.set_ylabel(r'Stream Discharge $[m^3/s]$', fontsize=8)
    ax0.tick_params(axis='both', labelsize=8)
    analyzer.plot_stf_sim_obd(ax0, stf_sim_obd, stf_obd)
    analyzer.plot_gw_sim_obd(ax1, gw_df, "sim_g14294lyr1", gw_obd, "dtw14294")
    analyzer.output_std_plot(ax3, wb_df, viz_ts)
    plt.suptitle("max", ha='left', va='top')
    plt.show()





# def plot_tot():
if __name__ == '__main__':
    wd_ub = "D:\\Projects\\Watersheds\\Kangwei\\prac2\\sw\\SWAT-MODFLOW_ub"
    # wd_ub = "D:\\Projects\\Watersheds\\Kangwei\\prac2\\sw\\SWAT-MODFLOW_ub"

    update_swatpar(wd_ub)
    execute_swatmf(wd_ub)
    extract_results(wd_ub)
    # plot
    plot_temp_hjc(wd_ub, 1, "sub001", stf_obd_file="stf_day.obd.csv")




