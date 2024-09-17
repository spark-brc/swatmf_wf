import os
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob


class QGIS(object):
    def __init__(self, wd):
        os.chdir(wd)    

    def name_k_zone(self):
        from qgis.core import (QgsVectorLayer, QgsField, QgsFeatureIterator,
                                QgsFeatureRequest, QgsProject, QgsLayerTreeLayer)
                                
        from qgis.PyQt.QtCore import QVariant

        layer = QgsProject.instance().mapLayersByName("4th")[0]
        provider = layer.dataProvider()
        if provider.fields().indexFromName("h_zon_lyr4") == -1:
            field = QgsField("h_zon_lyr4", QVariant.String)
            provider.addAttributes([field])
            layer.updateFields()
        layer.startEditing()
        for idx in [185, 186, 188, 197, 198, 199, 201, 202][::-1]:
            for f in layer.getFeatures():
                if f[f'HK_A{idx}_L4'] == 1:
                    f['h_zon_lyr4'] = f'A{idx}'
                # elif f['HK_A185_L1'] == 1:
                #     f['h_zon_lyr4'] = 'A185'
                if f[f'HK_LYR04L4'] == 1:
                    f['h_zon_lyr4'] = 'zlyr04'
                layer.updateFeature(f)
        '''
        layer.startEditing()
        for f in layer.getFeatures():
            if f['KXL1'] == 0.000864:
                f['h_zone'] = 'HK_sed'
            elif f['KXL1'] == 0.006912:
                f['h_zone'] = 'HK_AS01'
            elif f['KXL1'] == 0.0864:
                f['h_zone'] = 'HK_AS02'
            elif f['KXL1'] == 0.273024:
                f['h_zone'] = 'HK_AS03'
            elif f['KXL1'] == 0.991872:
                f['h_zone'] = 'HK_ORG'
            elif f['KXL1'] == 1.36944:
                f['h_zone'] = 'HK_AF01'
            else:
                f['h_zone'] = 'HK_AF02'
        #    print (f.id())
        #    layer.changeAttributeValue(f.id(), attrIdx, i+1)
        '''
        layer.commitChanges()
        print('done')

    def change_vals(self):
        from qgis.core import (QgsVectorLayer, QgsField, QgsFeatureIterator,
                                QgsFeatureRequest, QgsProject, QgsLayerTreeLayer)
                                
        from qgis.PyQt.QtCore import QVariant

        mons = ["mar", "jun", "aug", "sep", "dec"]
        
        for m in mons:
            indexnam = f"dtw_{m}_f"
            basenam = f"dtw_{m}"

            layer = QgsProject.instance().mapLayersByName("dtw")[0]
            provider = layer.dataProvider()
            if provider.fields().indexFromName(indexnam) == -1:
                field = QgsField(indexnam, QVariant.Double, 'double', 20, 5)
                provider.addAttributes([field])
                layer.updateFields()
            layer.startEditing()
            for f in layer.getFeatures():
                if f[basenam] <= -1:
                    f[indexnam] = 0
                else:
                    f[indexnam] = f[basenam]
                layer.updateFeature(f)
            layer.commitChanges()
            print(' >>> done')
        print(" > complete")





def rename_files(src_dir, dst_dir):
    # find all files
    src_list = os.listdir(src_dir)
    for src in tqdm(src_list):
        os.rename(
            os.path.join(src_dir, src), 
            os.path.join(dst_dir, f'ppwb03_{int(src[5:-4]):03d}.jpg'))


def getdap_pd(wd):
    os.chdir(wd)
    df = pd.read_excel(
        "Data AWD Patricia.xlsx", 
        sheet_name="Botanga Paddy depth",
        skiprows=2
        )
    df = df.iloc[:, :22]
    df.index = df.iloc[:, 0]
    df.dropna(inplace=True)
    df.rename(columns={
        df.columns[0]: "treatment", 
        df.columns[1]: "variety", 
        }, inplace=True)
    df = df.loc[(df["treatment"]=="CF") & (df["variety"]=="AGRA")]
    # df.mean()
    

    # print(df.iloc[:, 3:].mean())
    return df

def plot_pd(wd, df):
    df = getdap_pd(wd)
    fig, ax = plt.subplots()
    avg_df = df.iloc[:, 3:].mean()
    avg = df.iloc[:, 3:].mean().values
    min_df = df.iloc[:, 3:].min().values
    max_df = df.iloc[:, 3:].max().values

    y_err = np.stack([avg - min_df, max_df - avg])

    ax.bar(avg_df.index, avg_df.values,yerr=y_err, linestyle='-', ecolor='orange',capsize=3)
    ax.tick_params(axis='x', labelrotation=90)
    ax.set_ylabel("Paddy water depth $(cm)$",fontsize=12)
    ax.set_xlabel("Days after transplanting $(DAP)$",fontsize=12)
    # ax.grid('True')
    # ax.set
    fig.tight_layout()
    plt.savefig('pdepth.png', dpi=300, bbox_inches="tight")
    plt.show()

class MapSPAM(object):

    def __init__(self, wd):
        os.chdir(wd)
    
    # def read_file(self):


    def get_uniq_grid_ids(self):
        infs = [f for f in glob.glob("*.csv")]
        # print(infs)
        dff = pd.DataFrame()
        for i in infs:
            df = pd.read_csv(i, usecols=["grid_code", "x", "y"])
            dff = pd.concat([dff, df], axis=0)
        dff.drop_duplicates(subset=['grid_code'], keep='first', inplace=True)
        dff.sort_values(by=["grid_code"], inplace=True)
        dff.to_csv('base_pts.csv')
        print("done")

    def get_uniq_grid_ids(self):
        infs = [f for f in glob.glob("*.csv")]    







if __name__ == '__main__':
    # src_dir = "E:/Study/PEST/2022_The Maths Behind PEST and PEST++/day03/uncertainty_analysis_spark"
    # dst_dir = "E:/Study/PEST/2022_The Maths Behind PEST and PEST++/day03/temp"
    # rename_files(src_dir, dst_dir)
    # wd = "D:\\Projects\\Watersheds\\Ghana\\Data"
    # df = getdap_pd(wd)
    # plot_pd(wd, df)

    wd = "/Users/seonggyu.park/Library/CloudStorage/GoogleDrive-seonggyu.park@tamu.edu/Other computers/TR2950X/spam2020V1r0_global_physical_area.csv/spam2020V1r0_global_physical_area"
    # wd = "D:\\Projects\\rice_maps\\data\\spam2020V1r0_global_physical_area.csv\\spam2020V1r0_global_physical_area"
    m1 = MapSPAM(wd)
    m1.get_uniq_grid_ids()
