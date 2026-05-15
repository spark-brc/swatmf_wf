import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
# from hydroeval import evaluator, nse, rmse, pbias
import numpy as np
import math
import matplotlib.dates as mdates

from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec
from swatmf import handler, objfns
import pyemu


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_tseries_ensemble(
    pst,
    obgnam,
    *,
    pr_oe=None,
    pt_oe=None,
    width=10,
    height=3,
    dot=False,
    bstcd=None,
    pt_fill=None,
    ymin=None,
    ymax=None,
    savefig=False,
    filename=None,
    dpi=300,
    show=False,
):
    """
    Plot observed time-series data with optional prior and posterior output ensembles.

    This function supports four cases:

    1. Observed data only
    2. Observed data + prior ensemble
    3. Observed data + posterior ensemble
    4. Observed data + prior and posterior ensembles

    Parameters
    ----------
    pst : pyemu.Pst
        PEST control file object. The function uses pst.observation_data
        and pst.nnz_obs_groups.

    obgnam : str
        Observation group name to plot.

    pr_oe : pandas.DataFrame or pyemu.ObservationEnsemble, optional
        Prior output ensemble. Rows should be realization names and columns
        should be observation names.

    pt_oe : pandas.DataFrame or pyemu.ObservationEnsemble, optional
        Posterior output ensemble. Rows should be realization names and columns
        should be observation names.

    width, height : float, optional
        Figure size in inches.

    dot : bool, optional
        If True, plot ensemble realizations as scatter points.
        If False, plot ensemble realizations as lines.

    bstcd : str, optional
        Name of the best-estimate realization to plot from pt_oe.
        This requires pt_oe to be provided.

    pt_fill : pandas.DataFrame, optional
        DataFrame containing posterior uncertainty range.
        Expected columns are: "obgnme", "pt_min", and "pt_max".
        The index should be datetime-like or compatible with the x-axis.

    ymin, ymax : float, optional
        Optional y-axis limits.

    savefig : bool, optional
        If True, save the figure as a PNG file.

    filename : str, optional
        Output filename. If None, the filename is automatically generated.

    dpi : int, optional
        Resolution for saved figure.

    show : bool, optional
        If True, display the figure.

    Returns
    -------
    fig, ax
        Matplotlib figure and axis objects.
    """

    # ------------------------------------------------------------------
    # Convert pyemu ensemble-like objects to pandas DataFrames.
    # This allows pr_oe and pt_oe to come directly from:
    #
    # pyemu.ObservationEnsemble.from_csv(...)
    #
    # If either ensemble is None, it remains None.
    # ------------------------------------------------------------------
    pr_oe = _ensemble_to_dataframe(pr_oe, name="pr_oe")
    pt_oe = _ensemble_to_dataframe(pt_oe, name="pt_oe")

    has_prior = pr_oe is not None
    has_posterior = pt_oe is not None

    # ------------------------------------------------------------------
    # Get observation data from the PEST control file.
    # Keep only observations from non-zero-weight observation groups.
    # ------------------------------------------------------------------
    obs = pst.observation_data.copy()
    obs = obs.loc[obs.obgnme.isin(pst.nnz_obs_groups)].copy()

    # ------------------------------------------------------------------
    # Extract time information from observation names.
    # This assumes the last 8 characters of obsnme are dates.
    #
    # Example:
    #     something_20010515 -> 20010515
    #
    # If your observation-name date format is different, modify this line.
    # ------------------------------------------------------------------
    obs["time"] = pd.to_datetime(obs.obsnme.str[-8:], errors="coerce")

    # ------------------------------------------------------------------
    # Select the observation group requested by the user.
    # ------------------------------------------------------------------
    oobs = obs.loc[obs.obgnme == obgnam].copy()

    if oobs.empty:
        raise ValueError(f"No observations found for observation group: {obgnam}")

    # ------------------------------------------------------------------
    # Remove observations where the date could not be parsed.
    # ------------------------------------------------------------------
    oobs = oobs.dropna(subset=["time"]).copy()

    if oobs.empty:
        raise ValueError(
            f"Observations were found for {obgnam}, but no valid dates could be parsed "
            "from the last 8 characters of obsnme."
        )

    # ------------------------------------------------------------------
    # Sort observations by time so the line plot follows chronological order.
    # ------------------------------------------------------------------
    oobs.sort_values("time", inplace=True)

    tvals = oobs.time.to_numpy()
    onames = oobs.obsnme.to_numpy()

    # ------------------------------------------------------------------
    # Prepare prior ensemble.
    # Values <= -999 are treated as missing values.
    # ------------------------------------------------------------------
    if has_prior:
        pr_oe = pr_oe.where(pr_oe > -999)

        missing_prior_cols = [name for name in onames if name not in pr_oe.columns]

        if missing_prior_cols:
            raise KeyError(
                f"{len(missing_prior_cols)} observation names are missing from pr_oe. "
                f"Example missing name: {missing_prior_cols[0]}"
            )

    # ------------------------------------------------------------------
    # Prepare posterior ensemble.
    # Values <= -999 are treated as missing values.
    # ------------------------------------------------------------------
    if has_posterior:
        pt_oe = pt_oe.where(pt_oe > -999)

        missing_post_cols = [name for name in onames if name not in pt_oe.columns]

        if missing_post_cols:
            raise KeyError(
                f"{len(missing_post_cols)} observation names are missing from pt_oe. "
                f"Example missing name: {missing_post_cols[0]}"
            )

    # ------------------------------------------------------------------
    # Prepare posterior fill range if provided.
    # This plots posterior uncertainty as a band instead of plotting all
    # posterior realizations.
    # ------------------------------------------------------------------
    if pt_fill is not None:
        required_cols = {"obgnme", "pt_min", "pt_max"}
        missing_cols = required_cols.difference(pt_fill.columns)

        if missing_cols:
            raise KeyError(
                f"pt_fill is missing required columns: {sorted(missing_cols)}"
            )

        df_fill = pt_fill.loc[pt_fill["obgnme"] == obgnam].copy()

        if df_fill.empty:
            raise ValueError(f"No pt_fill records found for observation group: {obgnam}")
    else:
        df_fill = None

    # ------------------------------------------------------------------
    # Create figure.
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(width, height))

    # ------------------------------------------------------------------
    # Plot ensemble realizations as scatter points.
    # ------------------------------------------------------------------
    if dot:
        # Plot prior ensemble, if available.
        if has_prior:
            for idx, realization in enumerate(pr_oe.index):
                ax.scatter(
                    tvals,
                    pr_oe.loc[realization, onames].to_numpy(),
                    color="gray",
                    s=30,
                    alpha=0.5,
                    label="Prior ensemble" if idx == 0 else None,
                )

        # Plot posterior ensemble, if available.
        if has_posterior:
            for idx, realization in enumerate(pt_oe.index):
                ax.scatter(
                    tvals,
                    pt_oe.loc[realization, onames].to_numpy(),
                    color="b",
                    s=30,
                    alpha=0.2,
                    label="Posterior ensemble" if idx == 0 else None,
                )

        # Plot observed values with non-zero weight.
        oobs_nonzero = oobs.loc[oobs.weight > 0].copy()

        ax.scatter(
            oobs_nonzero.time,
            oobs_nonzero.obsval,
            color="red",
            s=30,
            label="Observed",
            zorder=5,
        ).set_facecolor("none")

    # ------------------------------------------------------------------
    # Plot ensemble realizations as lines.
    # ------------------------------------------------------------------
    else:
        # Plot prior ensemble, if available.
        if has_prior:
            for idx, realization in enumerate(pr_oe.index):
                ax.plot(
                    tvals,
                    pr_oe.loc[realization, onames].to_numpy(),
                    color="0.5",
                    lw=0.5,
                    alpha=0.6,
                    label="Prior ensemble" if idx == 0 else None,
                )

        # Plot posterior ensemble, if available.
        if has_posterior:
            if df_fill is not None:
                ax.fill_between(
                    df_fill.index,
                    df_fill.pt_min,
                    df_fill.pt_max,
                    interpolate=False,
                    facecolor="b",
                    alpha=0.6,
                    label="Posterior ensemble",
                    zorder=2,
                )
            else:
                for idx, realization in enumerate(pt_oe.index):
                    ax.plot(
                        tvals,
                        pt_oe.loc[realization, onames].to_numpy(),
                        color="b",
                        lw=0.5,
                        alpha=0.7,
                        label="Posterior ensemble" if idx == 0 else None,
                    )

        # Plot observed values with non-zero weight.
        oobs_nonzero = oobs.loc[oobs.weight > 0].copy()

        ax.scatter(
            oobs_nonzero.time,
            oobs_nonzero.obsval,
            color="red",
            s=5,
            zorder=5,
            alpha=0.5,
            label="Observed",
        ).set_facecolor("none")

    # ------------------------------------------------------------------
    # Plot best-estimate posterior realization, if requested.
    # This requires pt_oe because bstcd is selected from posterior ensemble.
    # ------------------------------------------------------------------
    if bstcd is not None:
        if not has_posterior:
            raise ValueError("bstcd was provided, but pt_oe is None.")

        if bstcd not in pt_oe.index:
            raise KeyError(
                f"Best-estimate realization '{bstcd}' was not found in pt_oe.index."
            )

        ax.plot(
            tvals,
            pt_oe.loc[bstcd, onames].to_numpy(),
            color="b",
            lw=1.2,
            zorder=6,
            label="Best estimation",
        )

    # ------------------------------------------------------------------
    # Format x-axis.
    # Major ticks are years.
    # Minor ticks are months.
    # ------------------------------------------------------------------
    years = mdates.YearLocator()
    years_fmt = mdates.DateFormatter("%Y")

    months = mdates.MonthLocator()
    months_fmt = mdates.DateFormatter("%b")

    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)

    ax.xaxis.set_minor_locator(months)
    ax.xaxis.set_minor_formatter(months_fmt)

    plt.setp(ax.xaxis.get_minorticklabels(), fontsize=6, rotation=90)

    ax.tick_params(axis="both", labelsize=8, rotation=0)
    ax.tick_params(axis="x", pad=15)

    # ------------------------------------------------------------------
    # Optional y-axis limits.
    # This supports ymin only, ymax only, or both.
    # ------------------------------------------------------------------
    if ymin is not None or ymax is not None:
        ax.set_ylim(ymin, ymax)

    # Add small x-axis margin so edge points are not clipped.
    ax.margins(x=0.01)

    # ------------------------------------------------------------------
    # Add legend only if there are labeled plot elements.
    # ------------------------------------------------------------------
    handles, labels = ax.get_legend_handles_labels()

    if labels:
        ax.legend(fontsize=8, ncol=3)

    plt.tight_layout()

    # ------------------------------------------------------------------
    # Save figure.
    # ------------------------------------------------------------------
    if savefig:
        if filename is None:
            filename = f"tensemble_{obgnam}.png"

        fig.savefig(filename, bbox_inches="tight", dpi=dpi)
    
    if show:
        plt.show()

    return fig, ax


def plot_parameter_ensemble(
    pst,
    *,
    pr_pe=None,
    pt_pe=None,
    sel_pars=None,
    width=7,
    height=5,
    ncols=3,
    nbins=20,
    bestcand=None,
    parobj_file=None,
    wd=None,
    savefig=False,
    filename=None,
    dpi=300,
    show=False,
):
    """
    Plot histograms of prior and/or posterior parameter ensembles.

    This function supports:

    1. Prior only
    2. Posterior only
    3. Prior + posterior

    The function also accepts pyemu.ParameterEnsemble objects directly,
    as long as `_ensemble_to_dataframe()` is available in the same module.

    Parameters
    ----------
    pst : pyemu.Pst
        PEST control file object. Used to access pst.parameter_data.

    pr_pe : pandas.DataFrame or pyemu.ParameterEnsemble, optional
        Prior parameter ensemble. Rows are realizations and columns are parameter names.

    pt_pe : pandas.DataFrame or pyemu.ParameterEnsemble, optional
        Posterior parameter ensemble. Rows are realizations and columns are parameter names.

    sel_pars : pandas.DataFrame, list-like, or None, optional
        Selected parameters to plot.

        If DataFrame, it should contain at least:
        - parnme

        Recommended columns:
        - parnme
        - parlbnd
        - parubnd
        - offset

        If sel_pars is None, parameters are selected from the available ensemble columns
        and merged with pst.parameter_data.

    width, height : float, optional
        Figure size in inches.

    ncols : int, optional
        Number of subplot columns.

    nbins : int, optional
        Number of histogram bins.

    bestcand : str, optional
        Best candidate realization name. Used only with parobj_file.

    parobj_file : str or path-like, optional
        CSV file containing parameter values for candidate realizations.
        It should contain a "real_name" column and parameter-name columns.

    wd : str or path-like, optional
        Working directory for parobj_file if parobj_file is a relative path.

    savefig : bool, optional
        If True, save the figure.

    filename : str, optional
        Output filename. If None, "parameter_ensemble.png" is used.

    dpi : int, optional
        Resolution for saved figure.

    show : bool, optional
        If True, call plt.show() inside the function.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Matplotlib figure object.

    axes : numpy.ndarray
        Array of matplotlib axes.
    """

    # ------------------------------------------------------------------
    # Convert pyemu ensemble-like objects to pandas DataFrames.
    # This allows direct use of:
    #
    # pyemu.ParameterEnsemble.from_csv(...)
    # ------------------------------------------------------------------
    pr_pe = _ensemble_to_dataframe(pr_pe, name="pr_pe")
    pt_pe = _ensemble_to_dataframe(pt_pe, name="pt_pe")

    has_prior = pr_pe is not None
    has_posterior = pt_pe is not None

    if not has_prior and not has_posterior:
        raise ValueError("At least one of pr_pe or pt_pe must be provided.")

    # ------------------------------------------------------------------
    # Prepare pst.parameter_data.
    # Some PEST/pyEMU objects store parameter names in the index, so we
    # make sure a 'parnme' column exists.
    # ------------------------------------------------------------------
    par_data = pst.parameter_data.copy()

    if "parnme" not in par_data.columns:
        par_data["parnme"] = par_data.index

    # These columns are needed to create histogram bins.
    required_cols = ["parnme", "parlbnd", "parubnd"]
    missing_cols = [col for col in required_cols if col not in par_data.columns]

    if missing_cols:
        raise KeyError(
            f"pst.parameter_data is missing required columns: {missing_cols}"
        )

    # Keep useful metadata columns if they exist.
    meta_cols = ["parnme", "parlbnd", "parubnd"]

    for optional_col in ["partrans", "parchglim", "pargp", "scale", "offset"]:
        if optional_col in par_data.columns:
            meta_cols.append(optional_col)

    par_meta = par_data[meta_cols].copy()

    # ------------------------------------------------------------------
    # Identify parameter columns available in the provided ensembles.
    # ------------------------------------------------------------------
    available_pars = set()

    if has_prior:
        available_pars.update(pr_pe.columns)

    if has_posterior:
        available_pars.update(pt_pe.columns)

    # ------------------------------------------------------------------
    # Build selected parameter dataframe.
    #
    # sel_pars can be:
    # - None
    # - list of parameter names
    # - DataFrame such as your df_pars filtered by partrans == "log"
    # ------------------------------------------------------------------
    if sel_pars is None:
        sel_pars_df = par_meta.loc[
            par_meta["parnme"].isin(available_pars)
        ].copy()

    elif isinstance(sel_pars, pd.DataFrame):
        sel_pars_df = sel_pars.copy()

        if "parnme" not in sel_pars_df.columns:
            raise KeyError("sel_pars DataFrame must contain a 'parnme' column.")

        # Add missing metadata from pst.parameter_data.
        missing_from_sel = [
            col for col in ["parlbnd", "parubnd", "offset"]
            if col not in sel_pars_df.columns
        ]

        if missing_from_sel:
            sel_pars_df = sel_pars_df.merge(
                par_meta,
                on="parnme",
                how="left",
                suffixes=("", "_pst"),
            )

            for col in missing_from_sel:
                pst_col = f"{col}_pst"
                if pst_col in sel_pars_df.columns:
                    sel_pars_df[col] = sel_pars_df[pst_col]

            drop_cols = [
                col for col in sel_pars_df.columns
                if col.endswith("_pst")
            ]
            sel_pars_df.drop(columns=drop_cols, inplace=True)

    else:
        # Assume sel_pars is list-like.
        sel_pars_df = pd.DataFrame({"parnme": list(sel_pars)})
        sel_pars_df = sel_pars_df.merge(
            par_meta,
            on="parnme",
            how="left",
        )

    # ------------------------------------------------------------------
    # Keep only parameters that exist in at least one provided ensemble.
    # ------------------------------------------------------------------
    sel_pars_df = sel_pars_df.loc[
        sel_pars_df["parnme"].isin(available_pars)
    ].copy()

    if sel_pars_df.empty:
        raise ValueError(
            "No selected parameters were found in the provided ensemble(s)."
        )

    # ------------------------------------------------------------------
    # Make sure parameter bounds exist.
    # ------------------------------------------------------------------
    if sel_pars_df["parlbnd"].isna().any() or sel_pars_df["parubnd"].isna().any():
        missing_bound_pars = sel_pars_df.loc[
            sel_pars_df["parlbnd"].isna() | sel_pars_df["parubnd"].isna(),
            "parnme",
        ].tolist()

        raise ValueError(
            "Some selected parameters are missing bounds. "
            f"Example(s): {missing_bound_pars[:5]}"
        )

    # ------------------------------------------------------------------
    # Use parameter offsets if available.
    # If not available, assume zero offset.
    #
    # In your sel_pars table, offset already exists, so the function
    # will use it directly.
    # ------------------------------------------------------------------
    if "offset" not in sel_pars_df.columns:
        sel_pars_df["offset"] = 0.0

    sel_pars_df["offset"] = sel_pars_df["offset"].fillna(0.0)

    # ------------------------------------------------------------------
    # Read best-candidate parameter object file once, if requested.
    # Do not read this inside the loop.
    # ------------------------------------------------------------------
    bestcand_df = None

    if parobj_file is not None:
        parobj_path = Path(parobj_file)

        if not parobj_path.is_absolute() and wd is not None:
            parobj_path = Path(wd) / parobj_path

        bestcand_df = pd.read_csv(parobj_path)

        if "real_name" not in bestcand_df.columns:
            raise KeyError(
                "parobj_file must contain a 'real_name' column."
            )

        if bestcand is None:
            raise ValueError(
                "parobj_file was provided, but bestcand is None."
            )

    # ------------------------------------------------------------------
    # Create subplot layout.
    # squeeze=False makes axes always a 2D array, even with one row.
    # ------------------------------------------------------------------
    npars = len(sel_pars_df)
    nrows = math.ceil(npars / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(width, height),
        squeeze=False,
    )

    # ------------------------------------------------------------------
    # Plot histograms.
    # ------------------------------------------------------------------
    first_legend_axis = True

    for i, ax in enumerate(axes.flat):
        if i >= npars:
            ax.axis("off")
            continue

        parnme = sel_pars_df.iloc[i]["parnme"]
        parlbnd = float(sel_pars_df.iloc[i]["parlbnd"])
        parubnd = float(sel_pars_df.iloc[i]["parubnd"])
        offset = float(sel_pars_df.iloc[i]["offset"])

        # Histogram bins are based on parameter bounds plus offset.
        bin_edges = np.linspace(
            parlbnd + offset,
            parubnd + offset,
            nbins + 1,
        )

        # --------------------------------------------------------------
        # Prior histogram
        # --------------------------------------------------------------
        if has_prior and parnme in pr_pe.columns:
            prior_vals = pr_pe[parnme].dropna().to_numpy(dtype=float) + offset

            ax.hist(
                prior_vals,
                bins=bin_edges,
                color="gray",
                alpha=0.5,
                density=False,
                label="Prior" if first_legend_axis else None,
            )

        # --------------------------------------------------------------
        # Posterior histogram
        # --------------------------------------------------------------
        if has_posterior and parnme in pt_pe.columns:
            post_vals = pt_pe[parnme].dropna().to_numpy(dtype=float) + offset

            ax.hist(
                post_vals,
                bins=bin_edges,
                alpha=0.5,
                density=False,
                label="Posterior" if first_legend_axis else None,
            )

        # --------------------------------------------------------------
        # Best-candidate vertical line
        # --------------------------------------------------------------
        if bestcand_df is not None:
            if parnme in bestcand_df.columns:
                match = bestcand_df.loc[
                    bestcand_df["real_name"] == bestcand,
                    parnme,
                ]

                if not match.empty:
                    x_best = float(match.iloc[0]) + offset

                    ax.axvline(
                        x=x_best,
                        color="red",
                        linestyle="--",
                        alpha=0.7,
                        label="Best candidate" if first_legend_axis else None,
                    )

        # --------------------------------------------------------------
        # Subplot formatting
        # --------------------------------------------------------------
        ax.set_title(
            parnme,
            fontsize=9,
            loc="left",
            x=0.05,
            y=0.92,
        )

        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8)

        if first_legend_axis:
            handles, labels = ax.get_legend_handles_labels()
            if labels:
                ax.legend(fontsize=8)
            first_legend_axis = False

    # ------------------------------------------------------------------
    # Shared figure labels.
    # ------------------------------------------------------------------
    fig.supxlabel("Parameter relative change (%)", fontsize=10)
    fig.supylabel("Frequency", fontsize=10)

    plt.tight_layout()

    # ------------------------------------------------------------------
    # Save figure only when requested.
    # ------------------------------------------------------------------
    if savefig:
        if filename is None:
            filename = "parameter_ensemble.png"

        fig.savefig(filename, bbox_inches="tight", dpi=dpi)

    # ------------------------------------------------------------------
    # Show figure only when requested.
    # In notebooks, using display(fig); plt.close(fig) outside the function
    # is often cleaner.
    # ------------------------------------------------------------------
    if show:
        plt.show()

    return fig, axes


def _ensemble_to_dataframe(ensemble, name="ensemble"):
    """
    Convert a pyemu ensemble-like object or pandas DataFrame to a pandas DataFrame.

    This helper makes the plotting function safer because pyemu objects such as
    pyemu.ObservationEnsemble may behave like a dataframe but may not pass a strict
    isinstance(..., pd.DataFrame) check.
    """

    if ensemble is None:
        return None

    if isinstance(ensemble, pd.DataFrame):
        return ensemble.copy()

    if hasattr(ensemble, "_df"):
        return ensemble._df.copy()

    if hasattr(ensemble, "to_dataframe"):
        return ensemble.to_dataframe().copy()

    try:
        return pd.DataFrame(
            ensemble,
            index=ensemble.index,
            columns=ensemble.columns,
        ).copy()
    except Exception as err:
        raise TypeError(
            f"{name} must be a pandas DataFrame, pyemu ensemble-like object, or None. "
            f"Could not convert object of type {type(ensemble)} to DataFrame."
        ) from err

