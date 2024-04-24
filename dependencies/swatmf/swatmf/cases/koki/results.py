import os
import matplotlib.pyplot as plt
import pyemu
from swatmf import analyzer
import pandas as pd


# koki info
wd = "d:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_git\\koki_zon_rw_ies"
os.chdir(wd)
pst_file = "koki_zon_rw_ies.pst"
iter_idx = 2
post_iter_num = 2
pst = pyemu.Pst(pst_file)
pst_nam = pst_file[:-4]
prior_df = pyemu.ParameterEnsemble.from_csv(
        pst=pst,filename=os.path.join(wd,f"{pst_nam}.{0}.par.csv"))
post_df = pyemu.ParameterEnsemble.from_csv(
        pst=pst,filename=os.path.join(wd,f"{pst_nam}.{iter_idx}.par.csv"))
df_pars = pd.read_csv(os.path.join(wd, f"{pst_nam}.par_data.csv"))
sel_pars = df_pars.loc[df_pars["partrans"]=='log']

# load prior simulation
pr_oe = pyemu.ObservationEnsemble.from_csv(
    pst=pst,filename=f'{pst_file[:-4]}.0.obs.csv'
    )
# load posterior simulation
pt_oe = pyemu.ObservationEnsemble.from_csv(
    pst=pst,filename=f'{pst_file[:-4]}.{post_iter_num}.obs.csv'
    )


def koki_ensemble_plot():
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="glm")
    obgs = df.loc[:, "obgnme"].unique()
    for obg in obgs:
        analyzer.plot_fill_between_ensembles(df.loc[df["obgnme"]==obg], size=3)

def koki_objs():
# load control file
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="glm")
    obgs = df.loc[:, "obgnme"].unique()
    for obg in obgs:
        print(analyzer.get_rels_objs(df, obgnme=obg))


def create_rels_objs():
    analyzer.create_rels_objs(wd, pst_file, iter_idx)


def plot_par_hist():
    analyzer.plot_prior_posterior_par_hist(
                        wd, pst, prior_df, post_df, sel_pars,
                        width=10, height=15, ncols=5, 
                        bestcand="293", parobj_file="koki_zon_rw_ies.2.par.objs.csv"
                        )

def plot_progress():
    # plot phi progress
    m_d = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_git\\koki_zon_rw_glm_iter50"
    pst_file = "koki_zon_rw_glm.pst"
    pst = pyemu.Pst(os.path.join(m_d, pst_file))
    pyemu.plot_utils.phi_progress(pst)
    plt.show()

# user custimized plot
def temp_plot(stf_obd_df, obd_col, std_df, viz_ts, gw_df, grid_id, gw_obd_df, gw_obd_col):
    fig = plt.figure(figsize=(10,10))
    subplots = fig.subfigures(4, 1, height_ratios=[0.2, 0.2, 0.2, 0.4], hspace=-0.05)

    ax0 = subplots[0].subplots(1,1)
    ax1 = subplots[1].subplots(1,2, sharey=True, 
                    gridspec_kw={
                    # 'height_ratios': [0.2, 0.2, 0.4, 0.2],
                    'wspace': 0.0
                    })
    ax2 = subplots[2].subplots(1,2, sharey=True, 
                    gridspec_kw={
                    # 'height_ratios': [0.2, 0.2, 0.4, 0.2],
                    'wspace': 0.0
                    })
    ax3 = subplots[3].subplots(4,1, sharex=True, height_ratios=[0.2, 0.2, 0.4, 0.2])
    # ax3 = subplots[1][1].subplots(2,5)

    # streamflow
    ax0.set_ylabel(r'Stream Discharge $[m^3/s]$', fontsize=8)
    ax0.tick_params(axis='both', labelsize=8)
    analyzer.plot_stf_sim_obd(ax0, stf_obd_df, obd_col)
    # '''
    analyzer.plot_gw_sim_obd(ax1[0], gw_df, "sim_g249lyr2", gw_obd_df, "g249lyr2")
    analyzer.plot_gw_sim_obd(ax1[1], gw_df, "sim_g249lyr3", gw_obd_df, "g249lyr3")
    # plot_gw_sim_obd(ax2[0], gw_df, "sim_g1203lyr2", gw_obd_df, "g1203lyr2")
    # plot_gw_sim_obd(ax2[1], gw_df, "sim_g1205lyr2", gw_obd_df, "g1205lyr2")
    analyzer.plot_gw_sim(ax2[0], gw_df, "sim_g1203lyr3")
    analyzer.plot_gw_sim(ax2[1], gw_df, "sim_g1205lyr3")
    # '''
    analyzer.std_plot(ax3, std_df, viz_ts)
    plt.show()


def fdc():
    analyzer.single_plot_fdc_added(pst, pr_oe, pt_oe, dot=False)



# def plot_tot():
if __name__ == '__main__':
    # wd = "/Users/seonggyu.park/Documents/projects/kokshila/swatmf_results"
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="glm")
    analyzer.single_plot_fdc_added(df.loc[df["obgnme"]=="sub68"], bstc=True)