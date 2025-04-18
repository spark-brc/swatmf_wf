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
import datetime as dt
from tqdm import tqdm
from swatmf import analyzer
import sys
from shutil import copyfile
import glob


# NOTE: swat output handler
class SWATMFout(object):

    def __init__(self, wd):
        os.chdir(wd)
        if os.path.isfile("file.cio"):
            cio = open("file.cio", "r")
            lines = cio.readlines()
            skipyear = int(lines[59][12:16])
            self.iprint = int(lines[58][12:16]) #read iprint (month, day, year)
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
            self.stdate = dt.datetime(styear, 1, 1) + dt.timedelta(FCbeginday - 1)
            self.eddate = dt.datetime(edyear, 1, 1) + dt.timedelta(FCendday - 1)
            self.stdate_warmup = dt.datetime(styear_warmup, 1, 1) + dt.timedelta(FCbeginday - 1)
            self.eddate_warmup = dt.datetime(edyear_warmup, 1, 1) + dt.timedelta(FCendday - 1)



    # scratches for QSWATMOD
    # read data first
    # stream discharge output.rch
    def read_stf_obd(self, obd_file):
        return pd.read_csv(obd_file,
            index_col=0,
            header=0,
            parse_dates=True,
            na_values=[-999, ""]
        )
    
    def read_dtw_static_obd(self):
        return pd.read_csv(
                    "dtw_static.obd.csv",
                    parse_dates=['date'],
                    na_values=[-999, ""],
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

    def update_index(self, df):
        startDate = self.stdate_warmup
        if self.iprint == 1:
            df.index = pd.date_range(startDate, periods=len(df))
        elif self.iprint == 0:
            df = df[df['filter'] < 13]
            df.index = pd.date_range(startDate, periods=len(df), freq="M")
        else:
            df.index = pd.date_range(startDate, periods=len(df), freq="A")
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

    def get_stf_sim_obd(self, obd_file, obd_col, subnum):
        strObd = self.read_stf_obd(obd_file)
        output_rch = self.read_output_rch_data()
        df = output_rch.loc[subnum]
        df = self.update_index(df)
        df2 = pd.concat([df, strObd[obd_col]], axis=1)
        df3 = df2.dropna()
        df3.drop('filter', axis=1, inplace=True)
        return df3

    # read groundwater levels from
    # 431, 4011
    # let's give dataframe not series
    def get_gw_sim(self, dtw_format=True):
        mf_obs = pd.read_csv(
                            "modflow.obs",
                            sep=r'\s+',
                            skiprows = 2,
                            usecols = [2, 3, 4],
                            # index_col = 0,
                            names = ["layer", "grid_id", "mf_elev"],)
        mf_obs["grid_layer"] = "sim_g" + mf_obs['grid_id'].astype(str) + "lyr" + mf_obs["layer"].astype(str)
        # need to change grid id info to allow multi-layer outputs
        grid_lyr_lst = mf_obs.loc[:, "grid_layer"].tolist()
        output_wt = pd.read_csv(
                            "swatmf_out_MF_obs",
                            sep=r'\s+',
                            skiprows = 1,
                            names = grid_lyr_lst)
        if dtw_format is True:
            dtw_df = pd.DataFrame()
            for grid_id in grid_lyr_lst:
                dtw_list = output_wt.loc[:, str(grid_id)] - float(mf_obs["mf_elev"].loc[mf_obs["grid_layer"]==grid_id])
                dtw_df = pd.concat(
                    [dtw_df, pd.DataFrame({str(grid_id):dtw_list})], 
                    axis=1, ignore_index=True)
            dtw_df.columns = grid_lyr_lst
            dtw_df.index = pd.date_range(self.stdate, periods=len(dtw_df))
            return dtw_df
        else:
            output_wt.index = pd.date_range(self.stdate, periods=len(output_wt))
            return output_wt
        # '''

    def get_static_gw(self):
        dtw_st_df = self.read_dtw_static_obd()
        dtw_st_df['date'] = pd.to_datetime(dtw_st_df['date']).dt.date
        mask = (
            (dtw_st_df['date'] >= self.stdate_warmup.date()) & 
            (dtw_st_df['date'] <= self.eddate_warmup.date())
            )
        dtw_st_df = dtw_st_df.loc[mask]

        with open("dtw_sim_static.txt", "w") as wf:
            wf.write("# static gw function alpha version ...\n")
            cols = f"{'grid_id':10s}{'layer':7s}{'date':17s}{'obd':14s}{'sim':14s}\n"
            wf.write(cols)
            for i in range(len(dtw_st_df)):
                grid_id = dtw_st_df.iloc[i, 0]
                layer = dtw_st_df.iloc[i, 1]
                st_dtw = dtw_st_df.iloc[i, 2]
                date = str(dtw_st_df.iloc[i, 3])
                dtwst_sim, g, l = self.load_sim_dtw_file(grid_id, layer, date)
                newline = f"{g:7d}{l:5d}{date:>14s}{st_dtw:14.4e}{dtwst_sim:14.4e}\n"
                wf.write(newline)
        print(f" {'>'*3} {'dtw_sim_static.txt'}" + " file file has been created...")    

    def load_sim_dtw_file(self, grid_id, layer, date):
        # print(date)
        df = pd.read_csv(
            f"sim_g{grid_id}lyr{layer}.txt", sep=r"\s+",
            header=None, names=["date", "sim"])
        sim = float(df.loc[df["date"]==date, "sim"].values[0])
        while sim < -999 and layer < 3:
            layer += 1
            if os.path.isfile(f"sim_g{grid_id}lyr{layer}.txt"):
                df = pd.read_csv(
                        f"sim_g{grid_id}lyr{layer}.txt", sep=r"\s+",
                        header=None,  names=["date", "sim"])
                sim = float(df.loc[df["date"]==date, "sim"].values[0])
        return sim, grid_id, layer
    
    def mf_static_to_ins(self):
        mf_sim_f = "dtw_sim_static.txt"
        with open(mf_sim_f, 'r') as f:
            data = f.readlines()
            c = 0
            for i, line in enumerate(data):
                if line.strip().endswith("sim"):
                    start_line = i
        with open(f"{mf_sim_f}.ins", "w") as wf:
            wf.write("pif ~" + "\n")
            for i in range(start_line+1):
                wf.write("l1\n")
            for j in range(start_line+1, len(data)):
                line = data[j].strip()
                date = "".join(line.split()[2].split("-"))
                obdnam = f"g{line.split()[0]}ly{line.split()[1]}d{date}"
                newline = f"l1 w w w w !{obdnam:^20s}!\n"
                wf.write(newline)

    def get_gw_obd(self, ts=None):
        if ts is None:
            mfobd_file = "dtw_day.obd.csv"
        if ts == "month":
            mfobd_file = "dtw_mon.obd.csv"
        return pd.read_csv(
                        mfobd_file,
                        index_col=0,
                        header=0,
                        parse_dates=True,
                        na_values=[-999, ""])
    
    def get_gw_sim_obd(self, grid_id, obd_col, ts=None, dtw_format=True):
        gw_obd = self.get_gw_obd(obd_col, ts=ts)
        gw_sim = self.get_gw_sim(grid_id, dtw_format=dtw_format)
        df =  pd.concat([gw_sim, gw_obd], axis=1).dropna()
        return df


    # read waterbalance data from output.std
    def get_std_data(self):
        startDate = self.stdate_warmup
        eddate = self.eddate_warmup
        eYear = eddate.strftime("%Y")
        with open("output.std", "r") as infile:
            lines = []
            y = ("TIME", "UNIT", "SWAT", "(mm)")
            for line in infile:
                data = line.strip()
                if len(data) > 100 and not data.startswith(y):  # 1st filter
                    lines.append(line)           
        dates = []
        for line in lines:  # 2nd filter
            try:
                date = line.split()[0]
                if (date == eYear):  # Stop looping
                    break
                elif(len(str(date)) == 4):  # filter years
                    continue
                else:
                    dates.append(line)
            except:
                pass
        date_f, prec, surq, latq, gwq, swgw, perco, tile, sw, gw = [], [], [], [], [], [], [], [], [], []
        for i in range(len(dates)): # 3rd filter and obtain necessary data
            if (int(dates[i].split()[0]) == 1) and (int(dates[i].split()[0]) - int(dates[i - 1].split()[0]) == -30):
                continue
            elif (int(dates[i].split()[0]) < int(dates[i-1].split()[0])) and (int(dates[i].split()[0]) != 1):
                continue
            else:
                date_f.append(int(dates[i].split()[0]))
                prec.append(float(dates[i].split()[1]))
                surq.append(float(dates[i].split()[2]))
                latq.append(float(dates[i].split()[3]))
                gwq.append(float(dates[i].split()[4]))
                swgw.append(float(dates[i].split()[5]))
                # perco.append(float(dates[i].split()[6]))
                perco.append(float(dates[i].split()[7]))  # SM3 uses reach !SP
                tile.append(float(dates[i].split()[8]))  # not use it for now
                sw.append(float(dates[i].split()[10]))
                gw.append(float(dates[i].split()[11]))
        names = ["prec", "surq", "latq", "gwq", "swgw", "perco", "tile", "sw", "gw"]
        data = pd.DataFrame(
            np.column_stack([prec, surq, latq, gwq, swgw, perco, tile, sw, gw]),
            columns=names)
        data.index = pd.date_range(startDate, periods=len(data))
        return data
    
    def get_gwsw_sub_df(self):
        stdate = self.stdate 
        tot_feats = 257
        infile = "swatmf_out_SWAT_gwsw_monthly"
        y = ("Monthly", "month:")
        with open(infile, "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)]
        data1 = [x.split()[1] for x in data]
        data_array = np.reshape(
            data1, (int(len(data1)/tot_feats), tot_feats), 
            # order='F'
            )
        # column_names = [i for i in range(1, 258)]
        df_ = pd.DataFrame(
            data_array, 
            # columns=column_names
            )
        df_.index = pd.date_range(stdate, periods=len(df_), freq="ME")
        dff = df_["1/1/2010":"12/31/2019"].astype(float)
        mbig_df = dff.groupby(dff.index.month).mean().T
        mbig_df["subid"] = mbig_df.index+1
        mbig_df.to_csv("swat_gwsw_avg_mon.csv", index=False)
        return mbig_df


    def get_head_avg_m_df(self):
        stdate = self.stdate 
        tot_feats = 74095
        # Open "swatmf_out_MF_head" file
        y = ("Monthly", "Yearly") # Remove unnecssary lines
        filename = "swatmf_out_MF_head_monthly"
        with open(filename, "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines     
        date = [x.strip().split() for x in data if x.strip().startswith("month:")] # Collect only lines with dates  
        onlyDate = [x[1] for x in date] # Only date
        data1 = [x.split() for x in data] # make each line a list
        dateList = pd.date_range(stdate, periods=len(onlyDate), freq ='M').strftime("%b-%Y").tolist()
        selectedSdate = 'Jan-2010'
        selectedEdate = 'Dec-2019'

        # Reverse step
        dateSidx = dateList.index(selectedSdate)
        dateEidx = dateList.index(selectedEdate)
        dateList_f = dateList[dateSidx:dateEidx+1]

        big_df = pd.DataFrame()
        datecount = 0
        for selectedDate in tqdm(dateList_f):
            # Reverse step
            dateIdx = dateList.index(selectedDate)
            #only
            onlyDate_lookup = onlyDate[dateIdx]
            dtt = dt.datetime.strptime(selectedDate, "%b-%Y")
            year = dtt.year
            layerN = "1"
            for num, line in enumerate(data1, 1):
                if ((line[0] == "month:" in line) and (line[1] == onlyDate_lookup in line) and (line[3] == str(year) in line)):
                    ii = num # Starting line
            count = 0
            while not ((data1[count+ii][0] == 'layer:') and (data1[count+ii][1] == layerN)):
                count += 1
            stline =count+ii+1

            mf_rchs = []
            hdcount = 0
            while hdcount < tot_feats:
                for kk in range(len(data1[stline])):
                    mf_rchs.append(float(data1[stline][kk]))
                    hdcount += 1
                stline += 1
            s = pd.Series(mf_rchs, name=dt.datetime.strptime(selectedDate, "%b-%Y").strftime("%Y-%m-%d"))
            big_df = pd.concat([big_df, s], axis=1)
            datecount +=1


        big_df = big_df.T
        big_df.index = pd.to_datetime(big_df.index)
        mbig_df = big_df.groupby(big_df.index.month).mean()
        mbig_df_t = mbig_df.T
        mbig_df_t["grid_id"] = mbig_df_t.index + 1
        mbig_df_t.to_csv("mf_head_avg_mon.csv", index=False)
        print("finished ...")

    def get_recharge_avg_m_df(self):
        stdate = self.stdate 
        tot_feats = 74095

        # Open "swatmf_out_MF_head" file
        y = ("Monthly", "Yearly") # Remove unnecssary lines
        filename = "swatmf_out_MF_recharge_monthly"
        # self.layer = QgsProject.instance().mapLayersByName("mf_nitrate_monthly")[0]
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines     
        date = [x.strip().split() for x in data if x.strip().startswith("month:")] # Collect only lines with dates  
        onlyDate = [x[1] for x in date] # Only date
        data1 = [x.split() for x in data] # make each line a list
        dateList = pd.date_range(stdate, periods=len(onlyDate), freq ='ME').strftime("%b-%Y").tolist()

        selectedSdate = 'Jan-2010'
        selectedEdate = 'Dec-2019'
        # Reverse step
        dateSidx = dateList.index(selectedSdate)
        dateEidx = dateList.index(selectedEdate)
        dateList_f = dateList[dateSidx:dateEidx+1]

        big_df = pd.DataFrame()
        datecount = 0
        for selectedDate in tqdm(dateList_f):
            # Reverse step
            dateIdx = dateList.index(selectedDate)
            #only
            onlyDate_lookup = onlyDate[dateIdx]
            dtt = dt.datetime.strptime(selectedDate, "%b-%Y")
            year = dtt.year
            layerN = "1"
            for num, line in enumerate(data1, 1):
                if ((line[0] == "month:" in line) and (line[1] == onlyDate_lookup in line) and (line[3] == str(year) in line)):
                    ii = num # Starting line
            mf_rchs = []
            hdcount = 0
            while hdcount < tot_feats:
                for kk in range(len(data1[ii])):
                    mf_rchs.append(float(data1[ii][kk]))
                    hdcount += 1
                ii += 1
            s = pd.Series(mf_rchs, name=dt.datetime.strptime(selectedDate, "%b-%Y").strftime("%Y-%m-%d"))
            big_df = pd.concat([big_df, s], axis=1)
            datecount +=1
 
        big_df = big_df.T
        big_df.index = pd.to_datetime(big_df.index)
        mbig_df = big_df.groupby(big_df.index.month).mean()
        mbig_df_t = mbig_df.T
        mbig_df_t["grid_id"] = mbig_df_t.index + 1
        mbig_df_t.to_csv("mf_rch_avg_mon.csv", index=False)
        print("finished ...")

    def temp_sup(self, subid): # to get prep
        with open('output.sub', 'r') as f:
            content = f.readlines()
        subs = [int(i[6:10]) for i in content[9:]]
        preps = [float(i[34:49]) for i in content[9:]]
        sub_df = pd.DataFrame(
            np.column_stack([subs, preps]),
            columns=["subs","prep",])
        sub_df['subs'] = sub_df['subs'].astype(int)
        sub_df = sub_df.loc[sub_df["subs"]==subid]
        sub_df = self.update_index(sub_df)

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

   


def read_output_sub(wd):
    with open(os.path.join(wd, 'output.sub'), 'r') as f:
        content = f.readlines()
    subs = [int(i[6:10]) for i in content[9:]]
    mons = [float(i[19:24]) for i in content[9:]]
    preps = [float(i[34:49]) for i in content[9:]]
    # pets = [float(i[54:64]) for i in content[9:]]
    ets = [float(i[64:74]) for i in content[9:]]
    sws = [float(i[74:84]) for i in content[9:]]
    percs = [float(i[84:94]) for i in content[9:]]
    surqs = [float(i[94:104]) for i in content[9:]]
    gwqs = [float(i[104:114]) for i in content[9:]]
    seds = [float(i[124:134]) for i in content[9:]]
    latq = [float(i[184:194]) for i in content[9:]] 
    sub_df = pd.DataFrame(
        np.column_stack([subs, mons, preps, sws, latq, surqs, ets, percs, gwqs, seds]),
        columns=["subs","mons", "precip", "sw", "latq", "surq", "et", "perco", "gwq", "sed"])

    # conv_types = {'hru':str, 'sub':int, 'mon':float, 'area_km2':float, 'irr_mm':float}
    # hru_df = hru_df.astype(conv_types)
    sub_df = sub_df.loc[sub_df['mons'] < 13]
    sub_df['mons'] = sub_df['mons'].astype(int)
    sub_df['subs'] = sub_df['subs'].astype(int)
    return sub_df


def read_output_sed(wd):
    with open(os.path.join(wd, 'output.sed'), 'r') as f:
        content = f.readlines()
    subs = [int(i[5:10]) for i in content[1:]]
    mons = [float(i[19:25]) for i in content[1:]]
    seds = [float(i[49:61]) for i in content[1:]]

    sed_df = pd.DataFrame(
        np.column_stack([subs, mons, seds]),
        columns=["subs","mons", "sed"])

    # conv_types = {'hru':str, 'sub':int, 'mon':float, 'area_km2':float, 'irr_mm':float}
    # hru_df = hru_df.astype(conv_types)
    sed_df = sed_df.loc[sed_df['mons'] < 13]
    # sed_df['mons'] = sed_df['mons'].astype(int)
    sed_df['subs'] = sed_df['subs'].astype(int)
    return sed_df


def read_output_rsv(wd):
    with open(os.path.join(wd, 'output.rsv'), 'r') as f:
        content = f.readlines()
    subs = [int(i[5:14]) for i in content[9:]]
    mons = [float(i[14:19]) for i in content[9:]]
    flow = [float(i[43:55]) for i in content[9:]]
    seds = [float(i[103:115]) for i in content[9:]]

    sed_df = pd.DataFrame(
        np.column_stack([subs, mons, flow, seds]),
        columns=["subs","mons", "flow", "sed"])

    # conv_types = {'hru':str, 'sub':int, 'mon':float, 'area_km2':float, 'irr_mm':float}
    # hru_df = hru_df.astype(conv_types)
    sed_df = sed_df.loc[sed_df['mons'] < 13]
    # sed_df['mons'] = sed_df['mons'].astype(int)
    sed_df['subs'] = sed_df['subs'].astype(int)
    return sed_df


def read_output_rch(wd):
    with open(os.path.join(wd, 'output.rch'), 'r') as f:
        content = f.readlines()
    subs = [int(i[5:10]) for i in content[9:]]
    mons = [float(i[19:25]) for i in content[9:]]
    flow = [float(i[49:61]) for i in content[9:]]
    seds = [float(i[97:109]) for i in content[9:]]

    sed_df = pd.DataFrame(
        np.column_stack([subs, mons, flow, seds]),
        columns=["subs","mons", "flow", "sed"])

    # conv_types = {'hru':str, 'sub':int, 'mon':float, 'area_km2':float, 'irr_mm':float}
    # hru_df = hru_df.astype(conv_types)
    sed_df = sed_df.loc[sed_df['mons'] < 13]
    # sed_df['mons'] = sed_df['mons'].astype(int)
    sed_df['subs'] = sed_df['subs'].astype(int)
    return sed_df

def filter_candidates(
        wd, pst, par_obj_file, parbds=None,
        nsbds=None, pbiasbds=None,
        rsqbds=None, rmsebds=None,
        savefile=False):
    pst_nam = par_obj_file[:-4]
    pars_info = get_par_offset(pst)
    po_df = pd.read_csv(os.path.join(wd, par_obj_file))
    if parbds is not None:
        for parnam in pars_info.parnme:
            po_df = po_df.query(f"{parnam}>={parbds[0]} & {parnam}<={parbds[1]}")
    if nsbds is not None:
        po_df = po_df.loc[(po_df["ns"]>=nsbds[0]) & (po_df["ns"]<=nsbds[1])]
    if pbiasbds is not None:
        po_df = po_df.query(f"pbias>={pbiasbds[0]} & pbias<={pbiasbds[1]}")
    if rsqbds is not None:
        po_df = po_df.loc[(po_df["rsq"]>=rsqbds[0]) & (po_df["rsq"]<=rsqbds[1])]
    if rmsebds is not None:
        po_df = po_df.loc[(po_df["rmse"]>=rmsebds[0]) & (po_df["rmse"]<=rmsebds[1])]
    if savefile is True:
        po_df.to_csv(os.path.join(wd, "{}.filter.csv".format(pst_nam)), index=False)
    print(po_df)
    return po_df

def get_par_offset(pst):
    pars = pst.parameter_data.copy()
    pars = pars.loc[:, ["parnme", "offset"]]
    return pars


def filter_candidates2(
        wd, pst, obs_file, 
        savefile=False):
    pst_nam = obs_file[:-4]
    pars_info = get_par_offset(pst)
    sims_df = pd.read_csv(os.path.join(wd, obs_file))
    
    sims_df = sims_df.loc[sims_df.iloc[:, 1] < 0] # filter only lower waterlevel realizations
    rel_nams = sims_df["real_name"].values
    sims_df = sims_df.iloc[:, 1:].T
    sims_df.columns = rel_nams
    obs = pst.observation_data.copy()
    time_col = []
    for i in range(len(obs)):
        time_col.append(obs.iloc[i, 0][-8:])
    obs['time'] = time_col
    obs['time'] = pd.to_datetime(obs['time'])
    df = pd.concat([obs, sims_df], axis=1)
    df.dropna(inplace=True)
    return df, rel_nams

def okvg_temp():
    wd = "C:\\Users\\seonggyu.park\\Downloads\\qswatmod_prj\\2nd_cali\\okvg_062320_pest\\SWAT-MODFLOW"
    m1 = SWATMFout(wd)
    df =  m1.get_recharge_avg_m_df()
    print(df)


def read_morris_msn(wd, pst_name):
    df = pd.read_csv(
            os.path.join(wd, pst_name.replace(".pst",".msn")),
            index_col='parameter_name'
            )
    # df.loc[df['sen_std_dev'].str.contains('-nan'), 'sen_std_dev'] = 0
    # df = df.astype(float)
    print(df) 
    return df 


# from cjfx
def file_name(path_, extension=True):
    if extension:
        fn = os.path.basename(path_)
    else:
        fn = os.path.basename(path_).split(".")[0]
    return(fn)

def read_from(filename, decode_codec = None, v=False):
    '''
    a function to read ascii files
    '''
    try:
        if not decode_codec is None: g = open(filename, 'rb')
        else: g = open(filename, 'r')
    except:
        print(
            "\t! error reading {0}, make sure the file exists".format(filename))
        return

    file_text = g.readlines()
    
    if not decode_codec is None: file_text = [line.decode(decode_codec) for line in file_text]

    if v:
        print("\t> read {0}".format(file_name(filename)))
    g.close
    return file_text

def get_file_size(file_path):
    return float(os.path.getsize(file_path))/1012

def error(text_):
    print("\t! {string_}".format(string_=text_))

def create_path(path_name, v=False):
    path_name = os.path.dirname(path_name)
    if path_name == '':
        path_name = './'
    if not os.path.isdir(path_name):
        os.makedirs(path_name)
        if v:
            print(f"\t> created path: {path_name}")
    return path_name

# from cjfx
def copy_file(filename, destination_path, delete_source=False, v = False, replace = True):
    '''
    a function to copy files
    '''
    if not replace:
        if exists(destination_path):
            if v:
                print(f"\t - file exists, skipping")
            return

    if not exists(filename):
        if not v:
            return
        print("\t> The file you want to copy does not exist")
        print(f"\t    - {filename}\n")
        ans = input("\t> Press  E then ENTER to Exit or C then ENTER to continue: ")
        counter = 0
        while (not ans.lower() == "c") and (not ans.lower() == "e"):
            ans = input("\t> Please, press E then ENTER to Exit or C then ENTER to continue: ")
            if counter > 2:
                print("\t! Learn to read instrunctions!!!!")
            counter += 1

        if ans.lower() == 'e': quit()
        if ans.lower() == 'c':
            write_to("log.txt", f"{filename}\n", mode='append')
            return

    if v:
        if delete_source:
            print(f"\t - [{get_file_size(filename)}] moving {filename} to \n\t\t{destination_path}")
        else:
            # print(f"\t - [{get_file_size(filename)}] copying {filename} to \n\t\t{destination_path}")
            sys.stdout.write('\rcopying ' + filename + '                        ')
            sys.stdout.flush()

    if not os.path.isdir(os.path.dirname(destination_path)):
        try:
            os.makedirs(os.path.dirname(destination_path))
        except:
            pass

    copyfile(filename, destination_path)
    if delete_source:
        try:
            os.remove(filename)
        except:
            error('coule not remove {fl}, make sure it is not in use'.format(fl=filename))


def write_to(filename, text_to_write, v=False, mode = "overwrite"):
    '''
    a function to write to file
    modes: overwrite/o; append/a
    '''
    try:
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
            if v:
                print("! the directory {0} has been created".format(
                    os.path.dirname(filename)))
    except:
        pass

    if (mode == "overwrite") or (mode == "o"):
        g = open(filename, 'w', encoding="utf-8")
    elif (mode == "append") or (mode == "a"):
        g = open(filename, 'a', encoding="utf-8")
    try:
        g.write(text_to_write)
        if v:
            print('\n\t> file saved to ' + filename)
    except PermissionError:
        print("\t> error writing to {0}, make sure the file is not open in another program".format(
            filename))
        response = input("\t> continue with the error? (Y/N): ")
        if response == "N" or response == "n":
            sys.exit()
    g.close


def exists(path_):
    if os.path.isdir(path_):
        return True
    if os.path.isfile(path_):
        return True
    return False


def generate_heatunit(wd, inf, cropBHU, month, day):
    df = pd.read_csv(os.path.join(wd, inf), skiprows=1, names=['tmax', 'tmin'], na_values=-999)
    stdate = read_from(os.path.join(wd, inf))[0]
    df.index = pd.date_range(start=stdate, periods=len(df))
    df['tmean'] = (df['tmin'] + df['tmax'])/2
    df["HU"] = df['tmean'] - cropBHU
    df.loc[df['HU'] < 0, 'HU'] = 0
    df[f"PHU{cropBHU}"] = df.groupby(df.index.year)["HU"].cumsum()
    
    phu0 = df.loc[(df.index.month==month) & (df.index.day==day)] 
    tphu0 = df.loc[(df.index.month==12) & (df.index.day==31)] 

    dff = pd.DataFrame(index=df.index.year.unique(), columns=["PHU0", "TPHU0"])
    dff["PHU0"] = phu0.loc[:, "PHU0"].values
    dff["TPHU0"] = tphu0.loc[:, "PHU0"].values
    dff["FPHU0"] = dff["PHU0"] / dff["TPHU0"]

    dff.to_csv(os.path.join(wd, 'test.csv')) 
    return dff



class Paddy(object):
    def __init__(self, wd) -> None:
        os.chdir(wd)
        self.stdate, self.enddate, self.stdate_warmup = self.define_sim_period()
    
    def read_print_prt(self):
        return pd.read_csv(
            "print.prt",
            sep=r'\s+',
            skiprows=1
        )

    def read_time_sim(self):
        return pd.read_csv(
            "time.sim",
            sep=r'\s+',
            skiprows=1,
        )
    
    def define_sim_period(self):
        df_time = self.read_time_sim()
        df_prt = self.read_print_prt()
        skipyear = int(df_prt.loc[0, "nyskip"])
        yrc_start = int(df_time.loc[0, "yrc_start"])
        yrc_st_warmup = yrc_start + skipyear
        yrc_end = int(df_time.loc[0, "yrc_end"])
        start_day = int(df_time.loc[0, "day_start"])
        end_day = int(df_time.loc[0, "day_end"])
        stdate = dt.datetime(yrc_start, 1, 1) + dt.timedelta(start_day - 1)
        eddate = dt.datetime(yrc_end, 1, 1) + dt.timedelta(end_day - 1)
        stdate_warmup = dt.datetime(yrc_st_warmup, 1, 1) + dt.timedelta(start_day - 1)
        # eddate_warmup = dt.datetime(yrc_end_warmup, 1, 1) + dt.timedelta(FCendday - 1)        
        startDate = stdate.strftime("%m/%d/%Y")
        endDate = eddate.strftime("%m/%d/%Y")
        startDate_warmup = stdate_warmup.strftime("%m/%d/%Y")
        # endDate_warmup = eddate_warmup.strftime("%m/%d/%Y")
        return startDate, endDate, startDate_warmup

    def read_paddy_daily(self, hruid=None):
        if hruid is None:
            hruid = 1 
        df = pd.read_csv("paddy_daily.csv", index_col=False)
        df = df.rename(columns=lambda x: x.strip())
        df = df.loc[df["HRU"]==1]
        df.index = pd.date_range(self.stdate_warmup, periods=len(df))
        return df

    def read_basin_pw_day(self, hruid=None):
        if hruid is None:
            hruid =1
        df = pd.read_csv("basin_pw_day.txt", sep=r"\s+", index_col=False, skiprows=[0, 2])
        df = df.rename(columns=lambda x: x.strip())
        df = df.loc[df["gis_id"]==1]
        df.index = pd.date_range(self.stdate_warmup, periods=len(df))
        return df
    
    def read_yield_obd(self):
        inf = "YIELD & PRODUCTION - DISTRICT DATA_csir request.xlsx"
        years, yields = [], []
        for i in range(2013, 2023):
            df = pd.read_excel(inf, sheet_name=str(i), skiprows=1, usecols=[1, 3])
            df.dropna(inplace=True)
            # df = df.loc[df["DISTRICTS"]=="Tolon/Kumbungu"]
            df = df[df["DISTRICTS"].str.contains('Kumbungu')]
            # df['Credit-Rating'].str.contains('Fair')
            years.append(i)
            yields.append(df.loc[:, "RICE"].values[0])
        dff = pd.Series(index=years, data=yields, name='obd_yield')
        dff.index = pd.date_range(f"1/1/{2013}", periods=len(dff), freq="YE")
        return dff

    def read_lsunit_wb_yr(self, hruid=None):
        if hruid is None:
            hruid =1
        df = pd.read_csv("lsunit_wb_yr.txt", sep=r"\s+", index_col=False, skiprows=[0, 2])
        df = df.rename(columns=lambda x: x.strip())
        df = df.loc[df["unit"]==1]
        df.index = pd.date_range(self.stdate_warmup, periods=len(df), freq="YE")
        return df
    

    def read_pcp_obd(self):
        inf = "pcp_year_obd.csv"
        df = pd.read_csv(inf, parse_dates=True, index_col=0)
        return df


# def plot_tot():
if __name__ == '__main__':
    # wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_git\\koki_zon_rw_morris"
    # pst_name = "koki_zon_rw_morris.pst"
    # # read_morris_msn(wd, pst_name)
    # analyzer.plot_sen_morris(read_morris_msn(wd, pst_name))
    # wd = "/Users/seonggyu.park/Documents/projects/tools/swatmf_wf/temp/dawhenya_weather"
    # wd = "D:\\Projects\\Watersheds\\Ghana\\Analysis\\botanaga_weather"
    # os.chdir(wd)
    # # tmp_files = [f for f in glob.glob("*.txt") if f[-7:] == "TMP.txt"]
    # # cropBHU = 0
    # # df = generate_heatunit(wd, "AF_430172_TMP.txt", cropBHU, 4, 15)
    
 
    # # # dff = pd.concat([phu0["PHU0"], tphu0["PHU0"]], axis=1, ignore_index=True)
    # # print(df)
    # inf = "AF_468598_TMP.txt"
    # cropBHU = 0
    # analyzer.plot_violin2(wd, inf, cropBHU, 12)
    
    # # # analyzer.plot_heatunit(df)
    # # generate_heatunit(wd, inf, cropBHU, 4, 15)

    # NOTE: PADDY
    from swatmf import analyzer
    wd =  "d:\\Projects\\Watersheds\\Ghana\\Analysis\\botanga\\prj01\\Scenarios\\Default\\TxtInOut_rice_f"
    m1 = Paddy(wd)

    '''
    '''
    df = m1.read_paddy_daily()
    cols = ["Precip", "Irrig", "Seep", "ET", "PET", 'WeirH', 'Wtrdep', 'WeirQ','LAI']
    df = df.loc[:,  cols]
    df = df["1/1/2019":"12/31/2020"]
    print(df)
    analyzer.Paddy(wd).plot_paddy_daily(df)

    dfs = m1.read_lsunit_wb_yr()
    dfs = dfs.loc[:,  "precip"]
    dfo = m1.read_pcp_obd()
    print(dfs)

    dfs = pd.concat([dfs, dfo], axis=1)
    analyzer.Paddy(wd).plot_prep(dfs)
    # print(analyzer.Paddy(wd).stdate)

    dfy = m1.read_basin_pw_day()
    dfy = dfy.loc[:,  "yield"].resample('YE').sum() * 0.001
    dfyo = m1.read_yield_obd()
    dfy = pd.concat([dfy, dfyo], axis=1)

    print(dfy)
    analyzer.Paddy(wd).plot_yield(dfy)



    