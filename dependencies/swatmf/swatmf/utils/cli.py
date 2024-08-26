import os
import glob
import shutil
import pandas as pd
import numpy as np
# from .. import gcm_analysis
from tqdm import tqdm
import datetime


class Cl(object):
    
    def __init__(self, wd):
        """weather dataset

        Args:
            wd (path): weather dataset path
        """
        
        os.chdir(wd)
    
    def get_weather_folder_lists(self):
        """return weather folder names and full paths

        Returns:
            str: return weather folder names and full paths
        """
        wt_fds = [name for name in os.listdir(".") if os.path.isdir(name)]
        full_paths = [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name)]
        return wt_fds, full_paths
        
    @property
    def cvt_gcm_pcp(self):
        full_paths = self.fullpaths
        for p in full_paths:
            os.chdir(p)
            print("Folder changed to {}".format(p))
            inf = [f for f in glob.glob("*.csv")][0]
            print("{} file found ...".format(inf))
            df =  pd.read_csv(os.path.join(p, inf), index_col=0, parse_dates=True)
            tot_pts = len(df.columns)
            print("  Converting {} to 'pcp1.pcp' file ... processing".format(inf))

            for i in tqdm(range(tot_pts)):
                df.iloc[:, i] = df.iloc[:, i].map(lambda x: '{:05.1f}'.format(x))
            df.insert(loc=0, column='year', value=df.index.year)
            df.insert(loc=1, column='jday', value=df.index.dayofyear.map(lambda x: '{:03d}'.format(x)))
            dff = df.T.astype(str).apply(''.join)
            with open(os.path.join(p, 'pcp1.pcp'), 'w') as f:
                for i in range(4):
                    f.write('\n')
                dff.to_csv(f, line_terminator='\n', index=False, header=None)
            print("  Converting GCM format file to 'pcp1.pcp' file ... passed")

    def read_gcm(self, file_path, subs):
        df = pd.read_csv(
            file_path, index_col=0, parse_dates=True)
        df.columns = ['sub_{}'.format(i+1) for i in range(len(df.columns))]
        cols = ['sub_{}'.format(i) for i in subs]
        df = df[cols]
        return df

    # def read_gcm_avg(file)
    def read_pcp(self, pcp_path, nloc):
        with open(pcp_path, 'r') as f:
            content = f.readlines()
        doy = [int(i[:7]) for i in content[4:]]
        date = pd.to_datetime(doy, format='%Y%j')
        df = pd.DataFrame(index=date)
        start_num = 7
        for i in tqdm(range(nloc)):
            pp = [float(i[start_num:start_num+5]) for i in content[4:]]
            start_num += 5
            new_columns = pd.DataFrame({f"sub_{i+1}":pp}, index=date)
            df = pd.concat([df, new_columns], axis=1)
        return df

    def read_tmp(self, tmp_path, nloc):
        with open(tmp_path, 'r') as f:
            content = f.readlines()
        doy = [int(i[:7]) for i in content[4:]]
        date = pd.to_datetime(doy, format='%Y%j')
        df_max = pd.DataFrame(index=date)
        df_min = pd.DataFrame(index=date)
        max_start_num = 7
        min_start_num = 12
        for i in tqdm(range(nloc)):
            max_tmp = [float(i[max_start_num:max_start_num+5]) for i in content[4:]]
            max_start_num += 10
            new_max = pd.DataFrame({f"max_sub{i+1}":max_tmp}, index=date)
            df_max = pd.concat([df_max, new_max], axis=1)
            min_tmp = [float(i[min_start_num:min_start_num+5]) for i in content[4:]]
            min_start_num += 10
            new_min = pd.DataFrame({f"min_sub{i+1}":min_tmp}, index=date)
            df_min = pd.concat([df_min, new_min], axis=1)
        return df_max, df_min

    def modify_tmp(self, weather_wd, weather_modified_wd, copy_files_fr_org=None):
        os.chdir(weather_wd)
        model_nams = [name for name in os.listdir(".") if os.path.isdir(name)]
        model_paths = [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name)]
        for i, mp in tqdm(zip(model_nams, model_paths), total=len(model_nams)):
            new_weather_dir = os.path.join(weather_modified_wd, "{}".format(i))
            if not os.path.exists(new_weather_dir):
                os.mkdir(new_weather_dir)
            with open(os.path.join(mp, 'Tmp1.Tmp'), "r") as f:
                lines = f.readlines()
            with open(os.path.join(new_weather_dir, 'Tmp1.Tmp'), "w") as f:
                count = 0
                for line in lines[:4]:
                    f.write(line.strip()+'\n')
                for line in lines[4:]:
                    if int(line[:4]) < 2020:
                        f.write((line[:7]+('-99.0-99.0')*154).strip()+'\n')
                    else:
                        f.write(line.strip()+'\n')
            if copy_files_fr_org is not None:
                try:
                    os.chdir(mp)
                    for f in copy_files_fr_org:
                        shutil.copyfile(f, os.path.join(new_weather_dir,f))
                except Exception as e:
                    raise Exception("unable to copy {0} from model dir: " + \
                                    "{1} to new model dir: {2}\n{3}".format(f, mp, new_weather_dir,str(e)))               
        print('Done!')

    def cvt_pcp_each(self, output_wd, pcp_nloc, pcp_file=None):
        if pcp_file is None:
            pcp_file = 'pcp1.pcp'
        nms, fps = self.get_weather_folder_lists()
        for nm, fp in zip(nms, fps):
            print(f'reading model {fp} ... processing')
            df = self.read_pcp(os.path.join(fp, pcp_file), pcp_nloc)
            stdate = [df.index[0].strftime('%Y%m%d')]
            if os.path.exists(os.path.join(output_wd, nm, 'PCP')):
                shutil.rmtree(os.path.join(output_wd, nm, 'PCP'), ignore_errors=True)
            print(f'writing model {nm} to indivisual file ... processing')      
            for i in tqdm(range(len(df.columns))):
                wd_df = stdate + df.iloc[:, i].map(lambda x: '{:.3f}'.format(x)).tolist()
                os.makedirs(os.path.join(output_wd, nm, 'PCP'), exist_ok=True)
                os.chdir(os.path.join(output_wd, nm, 'PCP'))
                with open(f'PCP_{i+1:03d}.txt', 'w') as fp:
                    for l in wd_df:
                        fp.write(l+"\n")

    def cvt_tmp_each(self, output_wd, tmp_nloc, tmp_file=None):
        if tmp_file is None:
            tmp_file = 'Tmp1.Tmp'
        nms, fps = self.get_weather_folder_lists()
        for nm, fp in zip(nms, fps):
            print(f'reading model {fp} ... processing')
            max_df, min_df = self.read_tmp(os.path.join(fp, tmp_file), tmp_nloc)
            stdate = [max_df.index[0].strftime('%Y%m%d')]
            if os.path.exists(os.path.join(output_wd, nm, 'TMP')):
                shutil.rmtree(os.path.join(output_wd, nm, 'TMP'), ignore_errors=True)
            print(f'writing model {nm} to indivisual file ... processing')      
            for i in tqdm(range(len(max_df.columns))):
                maxs_ = max_df.iloc[:, i].map(lambda x: '{:.2f}'.format(x)).tolist()
                mins_ = min_df.iloc[:, i].map(lambda x: '{:.2f}'.format(x)).tolist()
                ab = [f'{mx},{mi}' for mx, mi in zip(maxs_, mins_)]
                abf = stdate + ab

                os.makedirs(os.path.join(output_wd, nm, 'TMP'), exist_ok=True)
                os.chdir(os.path.join(output_wd, nm, 'TMP'))
                with open(f'TMP_{i+1:03d}.txt', 'w') as fp:
                    for l in abf:
                        fp.write(l+"\n")

    def cvt_tmp_each2(self, output_wd, tmp_nloc, tmp_file=None):
        if tmp_file is None:
            tmp_file = 'Tmp1.Tmp'
        nms, fps = self.get_weather_folder_lists()
        for nm, fp in zip(nms[1:], fps[1:]):
            print(f'reading model {fp} ... processing')
            max_df, min_df = self.read_tmp(os.path.join(fp, tmp_file), tmp_nloc)
            
            max_mean = max_df.mean(axis=1)
            min_mean = min_df.mean(axis=1)
            print(f'inserting additional reaches in dataframe ... processing')   
            for j in tqdm(range(155, 258)):
                max_mean.name = f'max_sub{j}'
                min_mean.name = f'min_sub{j}'
                max_df = pd.concat([max_df, max_mean], axis=1)
                min_df = pd.concat([min_df, min_mean], axis=1)
            stdate = [max_df.index[0].strftime('%Y%m%d')]
            if os.path.exists(os.path.join(output_wd, nm, 'TMP')):
                shutil.rmtree(os.path.join(output_wd, nm, 'TMP'), ignore_errors=True)

            print(f'writing model {nm} to indivisual file ... processing')      
            
            for i in tqdm(range(len(max_df.columns))):
                maxs_ = max_df.iloc[:, i].map(lambda x: '{:.2f}'.format(x)).tolist()
                mins_ = min_df.iloc[:, i].map(lambda x: '{:.2f}'.format(x)).tolist()
                ab = [f'{mx},{mi}' for mx, mi in zip(maxs_, mins_)]
                abf = stdate + ab

                os.makedirs(os.path.join(output_wd, nm, 'TMP'), exist_ok=True)
                os.chdir(os.path.join(output_wd, nm, 'TMP'))
                with open(f'TMP_{i+1:03d}.txt', 'w') as fp:
                    for l in abf:
                        fp.write(l+"\n")

    def check_coordinates(self, weatherdb, lats, lons):
        df = pd.read_csv(weatherdb)
        df.query(
            f'LAT > {lats[0]} & LAT < {lats[1]} &' +
            f'LONG > {lons[0]} & LONG < {lons[1]}', 
            inplace=True)
        return df


class SwatEdit(object):

    def read_swatcal(self):
        swatcalfile = "swatcalparms.cal"
        y = ("#") # Remove unnecssary lines
        with open(swatcalfile, "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines     
        rowsnum = data[0]
        df = pd.read_csv(swatcalfile, sep=r'\s+',  comment="#", header=1)
        df = df.iloc[:int(rowsnum)]
        df['real_val'] = df['VAL'] + df['OFFSET']

        # create model.in
        with open("model.in", 'w') as f:
            # f.write("{0:10d} #NP\n".format(mod_df.shape[0]))
            SFMT_LONG = lambda x: "{0:<50s} ".format(str(x))
            f.write(df.loc[:, ["NAME", "real_val"]].to_string(
                                                        col_space=0,
                                                        formatters=[SFMT_LONG, SFMT_LONG],
                                                        index=False,
                                                        header=False,
                                                        justify="left"))

def modify_sol(back_dir, output_dir):

    ext = "sol"
    dir_list = os.listdir(back_dir)
    files_all = [
                x for x in dir_list if (x.endswith('.{}'.format(ext)) and 
                not x.startswith('output'))
                ]
    
    var_list = ['SNAM', 'HYDGRP', 'SOL_ZMX', 'ANION_EXCL', 'SOL_CRK', 'TEXTURE',
                'SOL_Z', 'SOL_BD', 'SOL_AWC', 'SOL_K', 'SOL_CBN', 'SOL_CLAY', 'SOL_SILT',
                'SOL_SAND', 'SOL_ROCK', 'SOL_ALB', 'USLE_K', 'SOL_EC', 'SOL_CAL', 'SOL_PH']
    n_line = 9
    txtformat = '12.2f'
                    
    for fl in tqdm(files_all):
        with open(os.path.join(back_dir, fl), 'r', encoding='ISO-8859-1') as f:
            data = f.readlines()
        line = data[n_line]
        parts = line.split(':')
        num = parts[1].strip()
        nums = num.split()
        # change percentage to ratio
        nums2 = []
        for nm in nums:
            if float(nm) > 1:
                nm = float(nm)/100
                nums2.append(nm)
            else:
                nums2.append(nm)



        part1 = ''.join(['{:{}}'.format(float(x), txtformat) for x in nums2])
        new_line = '{part1}:{part2}\n'.format(part1=parts[0], part2=part1)
        data[n_line] = new_line
        with open(os.path.abspath(output_dir + '/' + fl), "w") as f:
            f.writelines(data)
    

def define_sim_period():
    if os.path.isfile("file.cio"):
        cio = open("file.cio", "r")
        lines = cio.readlines()
        skipyear = int(lines[59][12:16])
        iprint = int(lines[58][12:16]) #read iprint (month, day, year)
        styear = int(lines[8][12:16]) #begining year
        styear_warmup = int(lines[8][12:16]) + skipyear #begining year with warmup
        edyear = styear + int(lines[7][12:16])-1 # ending year
        edyear_warmup = styear_warmup + int(lines[7][12:16])-1 - int(lines[59][12:16])#ending year with warmup
        if skipyear == 0:
            FCbeginday = int(lines[9][12:16])  #begining julian day
        else:
            FCbeginday = 1  #begining julian day
        FCendday = int(lines[10][12:16])  #ending julian day
        cio.close()
        stdate = datetime.datetime(styear, 1, 1) + datetime.timedelta(FCbeginday - 1)
        eddate = datetime.datetime(edyear, 1, 1) + datetime.timedelta(FCendday - 1)
        stdate_warmup = datetime.datetime(styear_warmup, 1, 1) + datetime.timedelta(FCbeginday - 1)
        eddate_warmup = datetime.datetime(edyear_warmup, 1, 1) + datetime.timedelta(FCendday - 1)

        startDate = stdate.strftime("%m/%d/%Y")
        endDate = eddate.strftime("%m/%d/%Y")
        startDate_warmup = stdate_warmup.strftime("%m/%d/%Y")
        endDate_warmup = eddate_warmup.strftime("%m/%d/%Y")
        # duration = (eddate - stdate).days

        # ##### 
        # start_month = stdate.strftime("%b")
        # start_day = stdate.strftime("%d")
        # start_year = stdate.strftime("%Y")
        # end_month = eddate.strftime("%b")
        # end_day = eddate.strftime("%d")
        # end_year = eddate.strftime("%Y")
        return startDate, endDate, startDate_warmup, endDate_warmup


def delete_duplicate_river_grids(wd, riv_fname):
    with open(os.path.join(wd, riv_fname), "r") as fp:
        lines = fp.readlines()
        new_lines = []
        for line in lines:
            #- Strip white spaces
            line = line.strip()
            if line not in new_lines:
                new_lines.append(line)

    output_file = "{}_fixed".format(riv_fname)
    with open(os.path.join(wd, output_file), "w") as fp:
        fp.write("\n".join(new_lines))
    print('done!')


def get_all_scenario_lists(wd):
    os.chdir(wd)
    scn_nams = [name for name in os.listdir(".") if os.path.isdir(name)]
    full_paths = [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name)]
    return scn_nams, full_paths    


def all_strs(wd, sub_number, start_date, obd_nam, time_step=None):
    scn_nams, full_paths = get_all_scenario_lists(wd)
    if time_step is None:
        time_step = "D"
        strobd_file = "swat_rch_day.obd"
    else:
        time_step = "M"
        strobd_file = "swat_rch_mon.obd"
    tot_df = pd.DataFrame()
    for scn_nam, p in zip(scn_nams, full_paths):
        os.chdir(p)
        print("Folder changed to {}".format(p))
        df = pd.read_csv(
                    os.path.join("output.rch"),
                    delim_whitespace=True,
                    skiprows=9,
                    usecols=[1, 3, 6],
                    names=["date", "filter", "str_sim"],
                    index_col=0)
        df = df.loc[sub_number]
        if time_step == 'M':
            df = df[df["filter"] < 13]
        df.index = pd.date_range(start_date, periods=len(df.str_sim), freq=time_step)

        df.rename(columns = {'str_sim':'{}_sub_{}'.format(scn_nam, sub_number)}, inplace = True)
        tot_df = pd.concat(
            [tot_df, df['{}_sub_{}'.format(scn_nam, sub_number)]], axis=1,
            sort=False
            )
    print('Finished!')
    return tot_df


def all_seds(wd, sub_number, start_date, obd_nam, time_step=None):
    scn_nams, full_paths = get_all_scenario_lists(wd)
    if time_step is None:
        time_step = "D"
        strobd_file = "swat_rch_day.obd"
    else:
        time_step = "M"
        strobd_file = "swat_rch_mon.obd"
    tot_df = pd.DataFrame()
    for scn_nam, p in zip(scn_nams, full_paths):
        os.chdir(p)
        print("Folder changed to {}".format(p))
        df = pd.read_csv(
                    os.path.join("output.rch"),
                    delim_whitespace=True,
                    skiprows=9,
                    usecols=[1, 3, 10],
                    names=["date", "filter", "str_sim"],
                    index_col=0)
        df = df.loc[sub_number]
        if time_step == 'M':
            df = df[df["filter"] < 13]
        df.index = pd.date_range(start_date, periods=len(df.str_sim), freq=time_step)

        df.rename(columns = {'str_sim':'{}_sub_{}'.format(scn_nam, sub_number)}, inplace = True)
        tot_df = pd.concat(
            [tot_df, df['{}_sub_{}'.format(scn_nam, sub_number)]], axis=1,
            sort=False
            )
    print('Finished!')
    return tot_df


def str_df(rch_file, start_date, rch_num, obd_nam, time_step=None):
    
    if time_step is None:
        time_step = "D"
        strobd_file = "swat_rch_day.obd"
    else:
        time_step = "M"
        strobd_file = "swat_rch_mon.obd."
    output_rch = pd.read_csv(
                        rch_file, delim_whitespace=True, skiprows=9,
                        usecols=[0, 1, 8], names=["idx", "sub", "simulated"], index_col=0
                        )
    df = output_rch.loc["REACH"]
    str_obd = pd.read_csv(
                        strobd_file, sep=r'\s+', index_col=0, header=0,
                        parse_dates=True, delimiter="\t",
                        na_values=[-999, ""]
                        )
    # Get precipitation data from *.DYL
    prep_file = 'sub{}.DLY'.format(rch_num)
    with open(prep_file) as f:
        content = f.readlines()    
    year = content[0][:6].strip()
    mon = content[0][6:10].strip()
    day = content[0][10:14].strip()
    prep = [float(i[32:38].strip()) for i in content]
    prep_stdate = "/".join((mon,day,year))
    prep_df =  pd.DataFrame(prep, columns=['prep'])
    prep_df.index = pd.date_range(prep_stdate, periods=len(prep))
    prep_df = prep_df.replace(9999, np.nan)
    if time_step == "M":
        prep_df = prep_df.resample('M').mean()
    df = df.loc[df['sub'] == int(rch_num)]
    df = df.drop('sub', axis=1)
    df.index = pd.date_range(start_date, periods=len(df), freq=time_step)
    df = pd.concat([df, str_obd[obd_nam], prep_df], axis=1)
    plot_df = df[df['simulated'].notna()]
    return plot_df


def cvt_usgs_stf_obd(wd, fnam, stdate, eddate, colnam):
    df = pd.read_csv(os.path.join(wd, fnam), sep='\t', comment='#', header=0)
    df = df[df['agency_cd']=='USGS']
    df = df.drop(['agency_cd', f'{colnam}_cd'], axis=1)
    sites = df['site_no'].unique()
    dff = pd.DataFrame()
    dff['date'] = pd.date_range(stdate, eddate)
    dff = dff.set_index('date')
    for i in tqdm(sites):
        data = df[df['site_no']==str(i)]
        data.index = data.datetime
        # current data index is not datetimeindex so you need to convert it
        data.index = pd.to_datetime(data.index)
        data = data[~data.index.duplicated(keep='first')]
        data = data.drop(['site_no', 'datetime'], axis=1)
        data = data[str(colnam)]
        data.rename(str(i), inplace=True)
        # print(data)
        # data = data.rename({colnam: i}, axis=1)
        # data = data[str(i)]
        # print(data)
        # data = data.replace({i:['Ice','Ssn', 'Dis']}, np.nan)
        # convert cfs to cms
        data = data.astype('float')*0.0283
        dff = pd.concat([dff, data], axis=1, sort=True)
    dff.index.name = 'date'
    dff = dff.astype('float')
    # dff.dtypes
    dff.to_csv(os.path.join(wd, "stf_day.obd2.csv"), na_rep=-999)

def read_output_sub(wd):
    with open(os.path.join(wd, 'output.sub'), 'r') as f:
        content = f.readlines()
    subs = [int(i[6:10]) for i in content[9:]]
    mons = [float(i[19:24]) for i in content[9:]]
    preps = [float(i[34:44]) for i in content[9:]]
    # pets = [float(i[54:64]) for i in content[9:]]
    ets = [float(i[64:74]) for i in content[9:]]
    sws = [float(i[74:84]) for i in content[9:]]
    percs = [float(i[84:94]) for i in content[9:]]
    surqs = [float(i[94:104]) for i in content[9:]]
    gwqs = [float(i[104:114]) for i in content[9:]]
    latq = [float(i[184:194]) for i in content[9:]] 
    sub_df = pd.DataFrame(
        np.column_stack([subs, mons, preps, sws, latq, surqs, ets, percs, gwqs]),
        columns=["subs","mons", "precip", "sw", "latq", "surq", "et", "perco", "gwq"])

    # conv_types = {'hru':str, 'sub':int, 'mon':float, 'area_km2':float, 'irr_mm':float}
    # hru_df = hru_df.astype(conv_types)
    sub_df = sub_df.loc[sub_df['mons'] < 13]
    sub_df['mons'] = sub_df['mons'].astype(int)
    sub_df['subs'] = sub_df['subs'].astype(int)

    return sub_df

def read_output_mgt(wd):
    with open(os.path.join(wd, 'output.mgt'), 'r') as f:
        content = f.readlines()
    subs = [int(i[:5]) for i in content[5:]]
    hrus = [int(i[5:10]) for i in content[5:]]
    yrs = [int(i[10:16]) for i in content[5:]]
    mons = [int(i[16:22]) for i in content[5:]]
    doys = [int(i[22:28]) for i in content[5:]]
    areas = [float(i[28:39]) for i in content[5:]]
    cfp = [str(i[39:55]).strip() for i in content[5:]]
    opt = [str(i[55:70]).strip() for i in content[5:]]
    irr = [-999 if i[150:160].strip() == '' else float(i[150:160]) for i in content[5:]]
    mgt_df = pd.DataFrame(
        np.column_stack([subs, hrus, yrs, mons, doys, areas, cfp, opt, irr]),
        columns=['sub', 'hru', 'yr', 'mon', 'doy', 'area_km2', 'cfp', 'opt', 'irr_mm'])
    mgt_df['irr_mm'] = mgt_df['irr_mm'].astype(float)
    mgt_df['irr_mm'].replace(-999, np.nan, inplace=True)
    return mgt_df


def read_output_hru(wd):
    with open(os.path.join(wd, 'output.hru'), 'r') as f:
        content = f.readlines()
    lulc = [(i[:4]) for i in content[9:]]
    hrus = [str(i[10:19]) for i in content[9:]]
    subs = [int(i[19:24]) for i in content[9:]]
    mons = [(i[29:34]) for i in content[9:]]
    areas = [float(i[34:44]) for i in content[9:]]
    irr = [float(i[74:84]) for i in content[9:]]

    hru_df = pd.DataFrame(
        np.column_stack([lulc, hrus, subs, mons, areas, irr]),
        columns=['lulc', 'hru', 'sub', 'mon', 'area_km2', 'irr_mm'])

    conv_types = {'hru':str, 'sub':int, 'mon':float, 'area_km2':float, 'irr_mm':float}
    hru_df = hru_df.astype(conv_types)
    hru_df = hru_df.loc[hru_df['mon'] < 13]
    hru_df['mon'] = hru_df['mon'].astype(int)
    hru_df['irr_m3'] = (hru_df['area_km2']*1000000) * (hru_df['irr_mm']*0.001)

    return hru_df


def create_model_in(wd, excel_file):
    df = pd.read_excel(os.path.join(wd, excel_file), dtype=str, names=[0,1,2,3])
    df['left_col'] = df.iloc[:, [0,1,2]].fillna('').sum(axis=1)
    df['right_col'] = df.iloc[:, 3].astype(float).map(lambda x: '{:<12.10e}'.format(x))
    SFMT_LONG = lambda x: "{0:<50s} ".format(str(x))
    with open(os.path.join(wd, "model.in"), 'w') as f:
        f.write(df.loc[:, ["left_col", "right_col"]].to_string(
                                                    col_space=0,
                                                    formatters=[SFMT_LONG, SFMT_LONG],
                                                    index=False,
                                                    header=False,
                                                    justify="left"
                                                    )
                )
    print(df)



def create_model_in_tpl(wd, excel_file):
    df = pd.read_excel(os.path.join(wd, excel_file), sheet_name="Sheet2", dtype=str, names=[0,1,2,3])
    df['left_col'] = df.iloc[:, [0,1,2]].fillna('').sum(axis=1)
    df['right_col'] = df.iloc[:, 3].map(lambda x: " ~   {0:15s}   ~".format(x))
    SFMT_LONG = lambda x: "{0:<50s} ".format(str(x))
    with open(os.path.join(wd, "model.in.tpl"), 'w') as f:
        f.write(df.loc[:, ["left_col", "right_col"]].to_string(
                                                    col_space=0,
                                                    formatters=[SFMT_LONG, SFMT_LONG],
                                                    index=False,
                                                    header=False,
                                                    justify="left"
                                                    )
                )
    print(df)




if __name__ == '__main__':

    from swatmf.utils.cli import Cl

    wd = "D:\\Projects\\Africa_data\\AF_CHIRPS_weather"
    infile = "Africa_grids.csv"
    lats = [5.6, 5.9]
    lons = [0.01, 0.1]
    # sites = ['08095300']

    m01 = Cl(wd)
    df_co = m01.check_coordinates(infile, lats, lons)
    df_co.to_csv('cord_filtered.csv')
