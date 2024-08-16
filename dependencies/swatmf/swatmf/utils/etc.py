import os
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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


if __name__ == '__main__':
    # src_dir = "E:/Study/PEST/2022_The Maths Behind PEST and PEST++/day03/uncertainty_analysis_spark"
    # dst_dir = "E:/Study/PEST/2022_The Maths Behind PEST and PEST++/day03/temp"
    # rename_files(src_dir, dst_dir)
    wd = "D:\\Projects\\Watersheds\\Ghana\\Data"
    df = getdap_pd(wd)
    plot_pd(wd, df)

