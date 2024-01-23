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


# NOTE: swat output handler
class SWATMFout(object):

    def __init__(self, wd):
        os.chdir(wd)
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
            self.stdate_warmup = dt.datetime(styear_warmup, 1, 1) + dt.timedelta(FCbeginday - 1)
            self.eddate_warmup = dt.datetime(edyear_warmup, 1, 1) + dt.timedelta(FCendday - 1)
            print(self.stdate_warmup.strftime("%m/%d/%Y"))



    # def define_sim_period(self):
        

    #     if os.path.isfile("file.cio"):
    #         cio = open("file.cio", "r")
    #         lines = cio.readlines()
    #         skipyear = int(lines[59][12:16])
    #         iprint = int(lines[58][12:16]) #read iprint (month, day, year)
    #         styear = int(lines[8][12:16]) #begining year
    #         styear_warmup = int(lines[8][12:16]) + skipyear #begining year with warmup
    #         edyear = styear + int(lines[7][12:16])-1 # ending year
    #         edyear_warmup = styear_warmup + int(lines[7][12:16])-1 - int(lines[59][12:16])#ending year with warmup
    #         if skipyear == 0:
    #             FCbeginday = int(lines[9][12:16])  #begining julian day
    #         else:
    #             FCbeginday = 1  #begining julian day
    #         FCendday = int(lines[10][12:16])  #ending julian day
    #         cio.close()

    #         stdate = dt.datetime(styear, 1, 1) + dt.timedelta(FCbeginday - 1)
    #         eddate = dt.datetime(edyear, 1, 1) + dt.timedelta(FCendday - 1)
    #         stdate_warmup = dt.datetime(styear_warmup, 1, 1) + dt.timedelta(FCbeginday - 1)
    #         eddate_warmup = dt.datetime(edyear_warmup, 1, 1) + dt.timedelta(FCendday - 1)
    #         startDate_warmup = stdate_warmup.strftime("%m/%d/%Y")
    #         endDate_warmup = eddate_warmup.strftime("%m/%d/%Y")
    #         startDate = stdate.strftime("%m/%d/%Y")
    #         endDate = eddate.strftime("%m/%d/%Y")
    #         duration = (eddate - stdate).days

    #         self.startwm = stdate_warmup.strftime("%b")
    #         self.startwd = stdate_warmup.strftime("%d")
    #         self.startwy = stdate_warmup.strftime("%Y")
    #         endw_month = eddate_warmup.strftime("%b")
    #         endw_day = eddate_warmup.strftime("%d")
    #         endw_year = eddate_warmup.strftime("%Y")



    #         ##### 
    #         start_month = stdate.strftime("%b")
    #         start_day = stdate.strftime("%d")
    #         start_year = stdate.strftime("%Y")
    #         end_month = eddate.strftime("%b")
    #         end_day = eddate.strftime("%d")
    #         end_year = eddate.strftime("%Y")

    #         # Put dates into the gui
    #         self.dlg.lineEdit_start_m.setText(start_month)
    #         self.dlg.lineEdit_start_d.setText(start_day)
    #         self.dlg.lineEdit_start_y.setText(start_year)
    #         self.dlg.lineEdit_end_m.setText(end_month)
    #         self.dlg.lineEdit_end_d.setText(end_day)
    #         self.dlg.lineEdit_end_y.setText(end_year)
    #         self.dlg.lineEdit_duration.setText(str(duration))

    #         self.dlg.lineEdit_nyskip.setText(str(skipyear))

    #         # Check IPRINT option
    #         if iprint == 0:  # month
    #             self.dlg.comboBox_SD_timeStep.clear()
    #             self.dlg.comboBox_SD_timeStep.addItems(['Monthly', 'Annual'])
    #             self.dlg.radioButton_month.setChecked(1)
    #             self.dlg.radioButton_month.setEnabled(True)
    #             self.dlg.radioButton_day.setEnabled(False)
    #             self.dlg.radioButton_year.setEnabled(False)
    #         elif iprint == 1:
    #             self.dlg.comboBox_SD_timeStep.clear()
    #             self.dlg.comboBox_SD_timeStep.addItems(['Daily', 'Monthly', 'Annual'])
    #             self.dlg.radioButton_day.setChecked(1)
    #             self.dlg.radioButton_day.setEnabled(True)
    #             self.dlg.radioButton_month.setEnabled(False)
    #             self.dlg.radioButton_year.setEnabled(False)
    #         else:
    #             self.dlg.comboBox_SD_timeStep.clear()
    #             self.dlg.comboBox_SD_timeStep.addItems(['Annual'])
    #             self.dlg.radioButton_year.setChecked(1)
    #             self.dlg.radioButton_year.setEnabled(True)
    #             self.dlg.radioButton_day.setEnabled(False)
    #             self.dlg.radioButton_month.setEnabled(False)
    #         return stdate, eddate, stdate_warmup, eddate_warmup









    # scratches for QSWATMOD
    # read data first
    def read_stf_obd(self, obd_file):
        return pd.read_csv(obd_file,
            index_col=0,
            header=0,
            parse_dates=True,
            na_values=[-999, ""]
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

    def update_index(self, df, startDate, ts):
        if ts.lower() == "day":
            df.index = pd.date_range(startDate, periods=len(df.stf_sim))
        elif ts.lower() == "month":
            df = df[df['filter'] < 13]
            df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="M")
        else:
            df.index = pd.date_range(startDate, periods=len(df.stf_sim), freq="A")
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

    def get_stf_sim_obd(self, obd_file, obd_col, subnum, startDate, ts):
        strObd = self.read_stf_obd(obd_file)
        output_rch = self.read_output_rch_data()
        df = output_rch.loc[subnum]
        df = self.update_index(df, startDate, ts)
        df2 = pd.concat([df, strObd[obd_col]], axis=1)
        df3 = df2.dropna()
        return df3


    def read_std_dates(self, startDate, ts):
        dt = dt.strptime(startDate, "%m/%")

        if ts.lower() == "day":
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
            date_f = []
            for i in range(len(dates)):  # 3rd filter and obtain necessary data
                if (int(dates[i].split()[0]) == 1) and (int(dates[i].split()[0]) - int(dates[i - 1].split()[0]) == -30):
                    continue
                elif (int(dates[i].split()[0]) < int(dates[i-1].split()[0])) and (int(dates[i].split()[0]) != 1):
                    continue
                else:
                    date_f.append(int(dates[i].split()[0]))
            if self.dlg.radioButton_std_day.isChecked():
                self.dlg.doubleSpinBox_std_w_exag.setEnabled(False)
                dateList = pd.date_range(startDate, periods=len(date_f)).strftime("%m-%d-%Y").tolist()
                self.dlg.comboBox_std_sdate.clear()
                self.dlg.comboBox_std_sdate.addItems(dateList)
                self.dlg.comboBox_std_edate.clear()
                self.dlg.comboBox_std_edate.addItems(dateList)
                self.dlg.comboBox_std_edate.setCurrentIndex(len(dateList)-1)
            elif self.dlg.radioButton_std_month.isChecked():
                self.dlg.doubleSpinBox_std_w_exag.setEnabled(True)
                data = pd.DataFrame(date_f)
                data.index = pd.date_range(startDate, periods=len(date_f))
                dfm = data.resample('M').mean()
                dfmList = dfm.index.strftime("%b-%Y").tolist()
                self.dlg.comboBox_std_sdate.clear()
                self.dlg.comboBox_std_sdate.addItems(dfmList)
                self.dlg.comboBox_std_edate.clear()
                self.dlg.comboBox_std_edate.addItems(dfmList)
                self.dlg.comboBox_std_edate.setCurrentIndex(len(dfmList)-1)
            elif self.dlg.radioButton_std_year.isChecked():
                self.dlg.doubleSpinBox_std_w_exag.setEnabled(True)
                data = pd.DataFrame(date_f)
                data.index = pd.date_range(startDate, periods=len(date_f))
                dfa = data.resample('A').mean()
                dfaList = dfa.index.strftime("%Y").tolist()
                self.dlg.comboBox_std_sdate.clear()
                self.dlg.comboBox_std_sdate.addItems(dfaList)
                self.dlg.comboBox_std_edate.clear()
                self.dlg.comboBox_std_edate.addItems(dfaList)
                self.dlg.comboBox_std_edate.setCurrentIndex(len(dfaList)-1)
        elif self.dlg.radioButton_month.isChecked():
            self.dlg.doubleSpinBox_std_w_exag.setEnabled(True)
            lines = []
            y = ("TIME", "UNIT", "SWAT", "(mm)")
            with open(os.path.join(wd, "output.std"), "r") as infile:
                for line in infile:
                    data = line.strip()
                    if len(data) > 100 and not data.startswith(y):
                        lines.append(line)
            dates = []
            for line in lines:
                try:
                    date = line.split()[0]
                    if (date == str(eYear)):  # Stop looping
                        break
                    elif(len(str(date)) == 4):  # filter years
                        continue
                    else:
                        dates.append(date)
                except:
                    pass
            if self.dlg.radioButton_std_month.isChecked():
                dateList = pd.date_range(startDate, periods=len(dates), freq='M').strftime("%b-%Y").tolist()
                self.dlg.comboBox_std_sdate.clear()
                self.dlg.comboBox_std_sdate.addItems(dateList)
                self.dlg.comboBox_std_edate.clear()
                self.dlg.comboBox_std_edate.addItems(dateList)
                self.dlg.comboBox_std_edate.setCurrentIndex(len(dateList)-1)
            elif self.dlg.radioButton_std_year.isChecked():
                data = pd.DataFrame(dates)
                data.index = pd.date_range(startDate, periods=len(dates), freq='M')
                dfa = data.resample('A').sum()  # .mean() doesn't work!
                dfaList = dfa.index.strftime("%Y").tolist()
                self.dlg.comboBox_std_sdate.clear()
                self.dlg.comboBox_std_sdate.addItems(dfaList)
                self.dlg.comboBox_std_edate.clear()
                self.dlg.comboBox_std_edate.addItems(dfaList)
                self.dlg.comboBox_std_edate.setCurrentIndex(len(dfaList)-1)
        elif self.dlg.radioButton_year.isChecked():
            self.dlg.doubleSpinBox_std_w_exag.setEnabled(True)
            lines = []
            y = ("TIME", "UNIT", "SWAT", "(mm)")
            with open(os.path.join(wd, "output.std"), "r") as infile:
                for line in infile:
                    data = line.strip()
                    if len(data) > 100 and not data.startswith(y):
                        lines.append(line)
            dates = []
            bword = "HRU"
            for line in lines:
                try:
                    date = line.split()[0]
                    if (date == bword):  # Stop looping
                        break
                    else:
                        dates.append(date)
                except:
                    pass
            dateList = pd.date_range(startDate, periods=len(dates), freq='A').strftime("%Y").tolist()
            self.dlg.comboBox_std_sdate.clear()
            self.dlg.comboBox_std_sdate.addItems(dateList)
            self.dlg.comboBox_std_edate.clear()
            self.dlg.comboBox_std_edate.addItems(dateList)
            self.dlg.comboBox_std_edate.setCurrentIndex(len(dateList)-1)


