import os
import numpy as np
import matplotlib.pyplot as plt
import sys
# sys.path.insert(0,os.path.join("..", "..", "dependencies"))
# import pyemu
# import flopy
# assert "dependencies" in flopy.__file__
# assert "dependencies" in pyemu.__file__
import matplotlib as mpl

#--modify default matplotlib settings
mpl.rcParams['pdf.compression']          = 0
mpl.rcParams['pdf.fonttype']             = 42
#--figure text sizes
mpl.rcParams['legend.fontsize']  = 12
mpl.rcParams['axes.labelsize']   = 12
mpl.rcParams['xtick.labelsize']  = 12
mpl.rcParams['ytick.labelsize']  = 12

def gaussian_multiply(mu1,std1,mu2,std2):
    var1,var2 = std1**2,std2**2
    mean = (var1*mu2 + var2*mu1) / (var1 + var2)
    variance = (var1 * var2) / (var1 + var2)
    return mean, np.sqrt(variance)


def plot_posterior(prior_mean, prior_std, likeli_mean, likeli_std, legend=True, savefigure=False):
    plt.figure()

    post_mean, post_std = gaussian_multiply(prior_mean, prior_std, likeli_mean, likeli_std)

    xs, ys = gaussian_distribution(prior_mean, prior_std)
    plt.plot(xs, ys, color='k', ls='--', lw=3.0, label='prior')

    xs, ys = gaussian_distribution(likeli_mean, likeli_std)
    plt.plot(xs, ys, color='g', ls='--', lw=3.0, label='likelihood')

    xs, ys = gaussian_distribution(post_mean, post_std)
    plt.fill_between(xs, 0, ys, label='posterior', color='b', alpha=0.25)
    if legend:
        plt.legend();
    ax = plt.gca()
    ax.set_xlabel("Parameter")
    ax.set_yticks([])


    if savefigure:
        plt.savefig('probs.pdf')
    plt.show()


def gaussian_distribution(mean, stdev, num_pts=50):
    """get an x and y numpy.ndarray that spans the +/- 4
    standard deviation range of a gaussian distribution with
    a given mean and standard deviation. useful for plotting

    Args:
        mean (`float`): the mean of the distribution
        stdev (`float`): the standard deviation of the distribution
        num_pts (`int`): the number of points in the returned ndarrays.
            Default is 50

    Returns:
        tuple containing:

        - **numpy.ndarray**: the x-values of the distribution
        - **numpy.ndarray**: the y-values of the distribution

    Example::

        mean,std = 1.0, 2.0
        x,y = pyemu.plot.gaussian_distribution(mean,std)
        plt.fill_between(x,0,y)
        plt.show()


    """
    xstart = mean - (4.0 * stdev)
    xend = mean + (4.0 * stdev)
    x = np.linspace(xstart, xend, num_pts)
    y = (1.0 / np.sqrt(2.0 * np.pi * stdev * stdev)) * np.exp(
        -1.0 * ((x - mean) ** 2) / (2.0 * stdev * stdev)
    )
    return x, y
