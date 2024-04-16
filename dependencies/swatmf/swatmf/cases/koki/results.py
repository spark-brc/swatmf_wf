import os
import pyemu
from swatmf import analyzer




def koki_ensemble_plot():
    wd = "d:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_git\\koki_zon_rw_ies"
    os.chdir(wd)
    pst_file = "koki_zon_rw_ies.pst"
    post_iter_num = 3
    pst = pyemu.Pst(pst_file) # load control file
    # load prior simulation
    pr_oe = pyemu.ObservationEnsemble.from_csv(
        pst=pst,filename=f'{pst_file[:-4]}.0.obs.csv'
        )
    # load posterior simulation
    pt_oe = pyemu.ObservationEnsemble.from_csv(
        pst=pst,filename=f'{pst_file[:-4]}.{post_iter_num}.obs.csv'
        )
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="glm")
    obgs = df.loc[:, "obgnme"].unique()
    for obg in obgs:
        analyzer.plot_fill_between_ensembles(df.loc[df["obgnme"]==obg], size=3)

def koki_objs():
    wd = "d:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_git\\koki_zon_rw_ies"
    os.chdir(wd)
    pst_file = "koki_zon_rw_ies.pst"
    post_iter_num = 3
    pst = pyemu.Pst(pst_file) # load control file
    # load prior simulation
    pr_oe = pyemu.ObservationEnsemble.from_csv(
        pst=pst,filename=f'{pst_file[:-4]}.0.obs.csv'
        )
    # load posterior simulation
    pt_oe = pyemu.ObservationEnsemble.from_csv(
        pst=pst,filename=f'{pst_file[:-4]}.{post_iter_num}.obs.csv'
        )
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="glm")
    obgs = df.loc[:, "obgnme"].unique()
    for obg in obgs:
        print(analyzer.get_rels_objs(df, obgnme=obg))


# def plot_tot():
if __name__ == '__main__':
    # wd = "/Users/seonggyu.park/Documents/projects/kokshila/swatmf_results"

    koki_ensemble_plot()