import os
import matplotlib.pyplot as plt
import pyemu
from swatmf import analyzer
import pandas as pd
from swatmf import handler
from swatmf.utils import mf_configs

# koki info
wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\calibration\\koki_5th_ies_300"
os.chdir(wd)
pst_file = "koki_zon_rw_ies.pst"
iter_idx = 10
post_iter_num = 10
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
obgnam = "obd1205lyr3"

def koki_ensemble_plot():
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="base")
    # df.iloc[:, :-1].astype(float)
    # df = df[(df > -1000).all(axis=1)]
    # filtered_df = df[df['Age'] >= 25]

    df = df[(df["pr_min"]> -999)]


    obgs = df.loc[:, "obgnme"].unique()
    for obg in obgs:
        print(obg)
        analyzer.plot_fill_between_ensembles(df.loc[df["obgnme"]==obg], size=3)

def koki_ensemble_plot2():
    analyzer.plot_tseries_ensembles2(
        pst, pr_oe, pt_oe, obgnam, 
        width=12,
        height=3,
        dot=False)

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
def temp_plot(stf_obd_df, obd_col, wb_df, viz_ts, gw_df, grid_id, gw_obd_df, gw_obd_col):
    """_summary_

    :param stf_obd_df: handler.get_stf_sim_obd
    :type stf_obd_df: dataframe
    :param obd_col: obd name
    :type obd_col: stf
    :param wb_df: handler.get_std_data
    :type wb_df: dataframe
    :param viz_ts: time step
    :type viz_ts: stf
    :param gw_df: handler.get_gw_sim
    :type gw_df: dataframe
    :param grid_id: grid_id name
    :type grid_id: str
    :param gw_obd_df: handler.get_gw_obd
    :type gw_obd_df: dataframe
    :param gw_obd_col: column name
    :type gw_obd_col: str
    """
    fig = plt.figure(figsize=(10,10))
    subplots = fig.subfigures(
                                4, 1, height_ratios=[0.2, 0.2, 0.2, 0.4],
                            #   hspace=-0.05
                            )

    ax0 = subplots[0].subplots(1,1)
    ax1 = subplots[1].subplots(1,2, sharey=False, 
                    gridspec_kw={
                    # 'height_ratios': [0.2, 0.2, 0.4, 0.2],
                    'wspace': 0.0
                    })
    ax2 = subplots[2].subplots(1,2, sharey=False, 
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
    analyzer.plot_gw_sim_obd(ax1[0], gw_df, "sim_g249lyr2", gw_obd_df, "obd249lyr2")
    analyzer.plot_gw_sim_obd(ax1[1], gw_df, "sim_g249lyr3", gw_obd_df, "obd249lyr3")
    # plot_gw_sim_obd(ax2[0], gw_df, "sim_g1203lyr2", gw_obd_df, "g1203lyr2")
    # plot_gw_sim_obd(ax2[1], gw_df, "sim_g1205lyr2", gw_obd_df, "g1205lyr2")
    analyzer.plot_gw_sim_obd(ax2[0], gw_df, "sim_g1203lyr3",gw_obd_df, "obd1203lyr3")
    analyzer.plot_gw_sim_obd(ax2[1], gw_df, "sim_g1205lyr3", gw_obd_df, "obd1205lyr3")
    # '''
    analyzer.std_plot(ax3, wb_df, viz_ts)
    plt.show()


def fdc():
    analyzer.single_plot_fdc_added(pst, pr_oe, pt_oe, dot=False)


def modi_dtw_avg_obd():
    wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\koksilah_swatmf\\m03-base"
    df = pd.read_csv(os.path.join(wd, "dtw_avg.obd.csv"))
    modobs = pd.read_csv(
        os.path.join(wd, "modflow.obs"), sep=r'\s+', skiprows=2,
        header=None)
    modobs.drop_duplicates(3, keep='first', inplace=True)
    grids = df.grid_id.unique()
    new_df = pd.DataFrame()

    with open(os.path.join(wd, "modflow.obs.new"), 'w') as f:
        f.write("# this is customized...\n")
        f.write(f"{len(grids)*3:d}\n")
        for grid in grids:
            sdf =  modobs.loc[modobs[3]==grid].values[0]

            # for 3 layers
            for lyr in range(1, 4):
                # print(sdf)
                line = (
                    f"{sdf[0]:<5d}{sdf[1]:<5d}{lyr:<5d}{sdf[3]:<7d}{sdf[4]:<12.2f}" +
                    "  # Row, Col, Layer, grid_id, elevation\n"
                    )
                f.write(line)




# def plot_tot():
if __name__ == '__main__':
    wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\calibration\\koki_5th_ies_300"
    pst_file = "koki_zon_rw_ies.pst"
    iter_idx = 14
    # df = pd.DataFrame(pr_oe, index=pr_oe.index, columns=pr_oe.columns)
    # print(df.loc[df[pr_oe.columns.values]]<= -1000)
    # print(pr_oe.columns.values)
    # df = df[df < -999].dropna(axis=0, how='all')
    # df = df.dropna(axis=1, how='all')
    # print(df)
    # df = df.iloc[df[:, 10:] <= -1000]
    # print(df.loc[df["g1203ly1d20200304"] < -1000])
    # df2 = df[(df > -1000).all(axis=1)]

    # print(len(df))
    # print(df2)
    # analyzer.create_rels_objs(wd, pst_file, 10)
    df = analyzer.get_pr_pt_df(pst, pr_oe, pt_oe, bestrel_idx="223")
    df = df.loc[df["obgnme"]=="sub03"]
    print(df)
    # print(analyzer.get_rels_objs_new(df, obgnme="sub01"))

    analyzer.single_plot_fdc_added(df, bstc=True)
    '''


    '''

    ''' sen
    wd = "D:\\Projects\\Watersheds\\Koksilah\\analysis\\calibration\\koki_5th_morris"
    pst_file = "koki_zon_rw_morris.pst"
    analyzer.plot_sen_morris(handler.read_morris_msn(wd, pst_file))
    '''