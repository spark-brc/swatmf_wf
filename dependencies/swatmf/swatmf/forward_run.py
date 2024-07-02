import os
from datetime import datetime
import pyemu
import pandas as pd
import sys
import subprocess

# path = "D:/spark/gits/swatmf"
# sys.path.insert(1, path)

from swatmf import swatmf_pst_par, utils
from swatmf import swatmf_pst_utils
from swatmf.handler import SWATMFout
from swatmf.utils import swat_configs
from swatmf.utils import mf_configs
from swatmf.hg import hg_handler


wd = os.getcwd()
os.chdir(wd)

def time_stamp(des):
    time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
    print('\n' + 35*'+ ')
    print(time + ' |  {} ...'.format(des))
    print(35*'+ ' + '\n')

def modify_riv_pars():
    des = "updating river parameters"
    time_stamp(des)
    swatmf_pst_par.riv_par(wd)

def modify_hk_sy_pars_pp(pp_included):
    des = "modifying MODFLOW HK, VHK, and SY parameters"
    time_stamp(des)
    data_fac = pp_included
    for i in data_fac:
        outfile = i + '.ref'
        pyemu.utils.geostats.fac2real(i, factors_file=i+'.fac', out_file=outfile)

# def execute_swat_edit():
#     des = "modifying SWAT parameters"
#     # time_stamp(des)
#     # pyemu.os_utils.run('Swat_Edit.exe', cwd='.')
#     p = subprocess.Popen('Swat_Edit.exe' , cwd = '.')
#     p.wait()

def execute_swatmf():
    des = "running model"
    time_stamp(des)
    # pyemu.os_utils.run('APEX-MODFLOW3.exe >_s+m.stdout', cwd='.')
    # pyemu.os_utils.run('swatmf_rel230922.exe', cwd='.')
    pyemu.os_utils.run('smrt-hg.exe', cwd='.')

def extract_stf_results(subs, sim_start, warmup, cal_start, cal_end):
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

if __name__ == '__main__':
    # wd = "D:\\Projects\\Watersheds\\Gumu\\Analysis\\SWAT-MODFLOWs\\dataset_20240625_v02"
    # wd = "D:\\Projects\\Watersheds\\Gumu\\Analysis\\SWAT-MODFLOWs\\calibrations\\m01-base\\main_opt"
    os.chdir(wd)
    swatmf_con = pd.read_csv(
        'swatmf.con', sep='\t', names=['names', 'vals'], index_col=0, comment="#"
        )
    # get default vals
    # wd = swatmf_con.loc['wd', 'vals']
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

    modify_hk_sy_pars_pp(['hk0pp.dat', 'sy0pp.dat', 'ss0pp.dat'])

    # update SWAT parameters
    m1 = swat_configs.SwatEdit(wd)
    subbasins = m1.read_subs()
    new_parms = m1.read_new_parms()
    m1.param = [new_parms]
    m1.subbasins = [subbasins]
    m1.update_swat_parms()

    # update River parameters
    # modifying river pars
    if swatmf_con.loc['riv_parm', 'vals'] != 'n':
        rivmf = mf_configs.mfEdit(wd)
        mf_configs.write_new_riv()



    # execute model
    execute_swatmf()
    # extract sims
    # if swatmf_con.loc['cha_file', 'vals'] != 'n' and swatmf_con.loc['fdc', 'vals'] != 'n':
    if swatmf_con.loc['subs', 'vals'] != 'n':
        subs = swatmf_con.loc['subs','vals'].strip('][').split(', ')
        subs = [int(i) for i in subs]
        extract_stf_results(subs, sim_start, warmup, cal_start, cal_end)
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

    '''
    '''
    # NOTE: for Hg
    
    # this port is gumu
    hg_wt_subs = [3, 4, 9, 11]
    hg_wt_dates = ['6/3/2020', '9/21/2020', '12/7/2020', '3/3/2021', '8/30/2021']
    hg_handler.extract_hg_wt_mean(hg_wt_subs, sim_start, warmup, cal_start, cal_end, hg_wt_dates)
    
    hg_sed_subs = [2, 3, 4, 5, 9, 11]
    hg_sed_dates = ['6/30/2020', '12/31/2020', '11/30/2021']
    hg_handler.extract_hg_sed_mean(hg_sed_subs, sim_start, warmup, cal_start, cal_end, hg_sed_dates)

    # # NOTE: this is a temporary function
    # if swatmf_con.loc['avg_grids', 'vals'] != 'n':
    #     avg_grids = swatmf_con.loc['avg_grids','vals'].strip('][').split(', ')
    #     avg_grids = [int(i) for i in avg_grids]    
    #     avg_stdate = swatmf_con.loc['avg_dtw_stdate', 'vals']
    #     avg_eddate = swatmf_con.loc['avg_dtw_eddate', 'vals']
    #     extract_avg_depth_to_water(avg_grids, sim_start, avg_stdate, avg_eddate)

    # extract mf static depth to waterlevels
    # mfout = SWATMFout(wd)
    # mfout.get_static_gw()
    print(wd)
