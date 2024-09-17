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





def export_avg_mgwsw_MF(wd, startDate, scdate, ecdate, nrivs):
    filename = "swatmf_out_MF_gwsw_monthly"

    # Open "swatmf_out_MF_gwsw" file
    # y = ("Monthly", "month:", "Layer,")  # Remove unnecssary lines
    
    # with open(os.path.join(wd, filename), "r") as f:
    #     data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)]  

    data = np.loadtxt(
                    os.path.join(wd, filename),
                    skiprows=2,
                    comments=["Monthly", "month:", "Layer,"])
    df = np.reshape(data[:, 3], (int(len(data)/nrivs), nrivs))
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
    # print(mdf)



def export_avg_mgwsw(self):
    
    import scipy.stats as ss
    import operator
    import numpy as np

    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period()
    wd = QSWATMOD_path_dict['SMfolder']
    outfolder = QSWATMOD_path_dict['exported_files']
    startDate = stdate.strftime("%m-%d-%Y")
    msgBox = QMessageBox()
    msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))

    # Open "swatmf_out_MF_gwsw" file
    y = ("for", "Positive:", "Negative:", "Daily", "Monthly", "Annual", "Layer,")  # Remove unnecssary lines
    
    
    
    
    selectedDate = self.dlg.comboBox_gwsw_dates.currentText()

    filename = "swatmf_out_MF_gwsw_monthly"
    with open(os.path.join(wd, filename), "r") as f:
        data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)]  
    date = [x.strip().split() for x in data if x.strip().startswith("month:")]
    data1 = [x.split() for x in data]
    onlyDate = [x[1] for x in date] 
    #dateList = [(sdate + datetime.timedelta(months = int(i)-1)).strftime("%m-%Y") for i in onlyDate]
    dateList = pd.date_range(startDate, periods = len(onlyDate), freq = 'M').strftime("%b-%Y").tolist()
    
    
    # Reverse step
    dateIdx = dateList.index(selectedDate)
    # Find year 
    dt = datetime.datetime.strptime(selectedDate, "%b-%Y")
    year = dt.year
    #only
    onlyDate_lookup = onlyDate[dateIdx]
    for num, line in enumerate(data1, 1):
        if ((line[0] == "month:" in line) and (line[1] == onlyDate_lookup in line) and (line[3] == str(year) in line)):
            ii = num # Starting line

    #### Layer
    orgGIS = QSWATMOD_path_dict['org_shps']
    smGIS = QSWATMOD_path_dict['SMshps']
    river = shapefile_sm.Reader(os.path.join(orgGIS, "riv_SM.shp" )) # River
    sub = shapefile_sm.Reader(os.path.join(orgGIS, "mf_boundary.shp" )) # dissolved sub
    sm_riv = shapefile_sm.Reader(os.path.join(smGIS, "sm_riv.shp"))
    # ------------------------------------------------------------------------------
    sr = sm_riv.shapes() # property of sm_river
    coords = [sr[i].bbox for i in range(len(sr))] # get coordinates for each river cell
    width = abs(coords[0][2] - coords[0][0]) # get width for bar plot
    nSM_riv = len(sr) # Get number of river cells
    mf_gwsws = [data1[i][3] for i in range(ii, ii + nSM_riv)] # get gwsw data ranging from ii to 

    # Sort coordinates by row
    c_sorted = sorted(coords, key=operator.itemgetter(0))
    c_sorted = sorted(c_sorted, key=operator.itemgetter(1), reverse=True)

    # Put coordinates and gwsw data in Dataframe together
    f_c = pd.DataFrame(c_sorted, columns=['x_coord', 'y_coord', 'x_max', 'y_max'])
    f_c['gwsw'] = mf_gwsws
    df = f_c.drop(['x_max', 'y_max'], axis=1)

    # Add info
    version = "version 2.8."
    time = datetime.datetime.now().strftime('- %m/%d/%y %H:%M:%S -')

    # msgBox = QMessageBox()
    # msgBox.setWindowIcon(QtGui.QIcon(':/QSWATMOD2/pics/sm_icon.png'))   
    if self.dlg.radioButton_gwsw_day.isChecked():
        with open(os.path.join(outfolder, "GWSW(" + str(selectedDate) + ")_daily.txt"), 'w') as f:
            f.write("# GWSW(" + str(selectedDate) + ")_daily - QSWATMOD2 Plugin " + version + time + "\n")
            df.to_csv(
                f,
                # index_label="Date",
                index=False,
                sep='\t', float_format='%.2f', lineterminator='\n', encoding='utf-8')
        msgBox.setWindowTitle("Exported!") 
        msgBox.setText(
            "'GWSW"+"(" + str(selectedDate) + 
            ")_daily.txt' file is exported to your 'exported_files' folder!")
        msgBox.exec_()
    elif self.dlg.radioButton_gwsw_month.isChecked():
        with open(os.path.join(outfolder, "GWSW(" + str(selectedDate) + ")_monthly.txt"), 'w') as f:
            f.write("# GWSW(" + str(selectedDate) + ")_monthly - QSWATMOD2 Plugin " + version + time + "\n")
            df.to_csv(
                f,
                # index_label="Date",
                index=False,
                sep='\t', float_format='%.2f', lineterminator='\n', encoding='utf-8')
        msgBox.setWindowTitle("Exported!") 
        msgBox.setText(
            "'GWSW"+"(" + str(selectedDate) + 
            ")_monthly.txt' file is exported to your 'exported_files' folder!")
        msgBox.exec_()
    elif self.dlg.radioButton_gwsw_year.isChecked():
        with open(os.path.join(outfolder, "GWSW(" + str(selectedDate) + ")_annual.txt"), 'w') as f:
            f.write("# GWSW(" + str(selectedDate) + ")_annual - QSWATMOD2 Plugin " + version + time + "\n")
            df.to_csv(
                f,
                # index_label="Date",
                index=False,
                sep='\t', float_format='%.2f', lineterminator='\n', encoding='utf-8')
        msgBox.setWindowTitle("Exported!") 
        msgBox.setText(
            "'GWSW"+"(" + str(selectedDate) + 
            ")_annual.txt' file is exported to your 'exported_files' folder!")
        msgBox.exec_()




if __name__ == '__main__':
    # wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_swatmf\\m05-base_manual01"
    wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\calibration\\7th\\koki_ies"
    startDate = '1/1/2010'
    scdate = '1/1/2013'
    ecdate = '12/31/2022'
    nrivs = 724

    export_avg_mgwsw_MF(wd, startDate, scdate, ecdate, nrivs)