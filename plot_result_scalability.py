import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import h5py
import numpy as np

import sqlalchemy

import sys

pgfconfig = {
    "pgf.texsystem":   "pdflatex", # or any other engine you want to use
    "text.usetex":     True,       # use TeX for all texts
    "font.family":     "serif",
    "font.serif":      [],         # empty entries should cause the usage of the document fonts
    "font.sans-serif": [],
    "font.monospace":  [],
    "font.size":       7,         # control font sizes of different elements
    "axes.labelsize":  7,
    "text.latex.preamble" : r'\newcommand{\mathdefault}[1][]{}',
    "legend.fontsize": 5,
    "xtick.labelsize": 5,
    "ytick.labelsize": 5,
    "lines.markersize":5
}

mpl.use("pgf")
mpl.rcParams.update(pgfconfig)

# EXP_NAMES = ["coordinated", "uncoordinated", "random", "noadaptation"]
EXP_NAMES = ["coordinated", "uncoordinated", "random"]
# EXP_NAMES = ["coordinated", "uncoordinated"]
# EXP_NAMES = ["uncoordinated"]
SEEDS = [123456789, 987654321, 12121212, 34343434, 565656, 787878, 909090, 123123, 456456, 789789]
# SEEDS = [123123, 456456, 789789]
# SEEDS = [123123]
SEED = 123456789
MOTES = [3, 4, 5, 6, 7, 8, 9]

# STD_MULTIPLIER = 1.96 # i.e. 95% confidence interval
STD_MULTIPLIER = 2.0
# STD_MULTIPLIER = 1.0


# ENGINE = sqlalchemy.create_engine("sqlite:///results_good_6motes_5discretization.sqlite3", echo=False)

def main():
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(3.3, 3.0), tight_layout=True, gridspec_kw={'height_ratios': [1.4, 1.4, 1, 1]})
    rew_ax = ax[0]
    exectime_ax = ax[1]
    msgsize_ax = ax[2]
    memory_ax = ax[3]

    means = {k: [] for k in EXP_NAMES}
    stds = {k: [] for k in EXP_NAMES}
    idx = []
    for motenumber in MOTES:
        normalization_factor = 0.5 * motenumber * (motenumber - 1) + motenumber # the amount of shared qfuncs + local qfuncs
        rew_sums = {k: None for k in EXP_NAMES}
        for exp_name in EXP_NAMES:
            # key = "{}_{}".format(exp_name, seed)
            ENGINE = sqlalchemy.create_engine("sqlite:///results_{}motes_good.sqlite3".format(motenumber), echo=False)
            # reward_data = pd.read_sql("SELECT * FROM rewards WHERE experimentName='{}'".format(key), con=ENGINE)
            reward_data = pd.read_sql("SELECT * FROM rewards WHERE experimentType='{}'".format(exp_name), con=ENGINE)

            # rewardTotal = reward_data.groupby("seed")["rewardTotal"].sum() / normalization_factor
            # rewardTotal = reward_data.groupby("seed")["rewardTotal"].sum() / motenumber
            rewardTotal = reward_data.groupby("seed")["rewardTotal"].sum()
            # rew_sums[exp_name] = rewardTotal
            # print(rew_sums)
            means[exp_name].append(rewardTotal.mean())
            stds[exp_name].append(rewardTotal.std() * STD_MULTIPLIER)
        idx.append(motenumber)

    print(means, stds, idx)

    for exp_name in EXP_NAMES:
        rew_ax.errorbar(idx, means[exp_name], yerr=stds[exp_name], fmt='-o', markersize=3)

    rew_ax.legend(["{}".format(exp_name) for exp_name in EXP_NAMES], loc="lower left")
    # rew_ax.set_title("Scalability study")
    rew_ax.set_ylabel("(a)\nnormalized\ntotal reward", multialignment='center')
    # rew_ax.set_yscale('symlog')
    # rew_ax.set_xlabel("number of motes")


    means = []
    stds = []
    min_max = []
    idx = []
    for motenumber in MOTES:
        ENGINE = sqlalchemy.create_engine("sqlite:///results_{}motes_good.sqlite3".format(motenumber), echo=False)
        benchmark_data = pd.read_sql("SELECT * FROM benchmarks WHERE experimentType='{}'".format("coordinated"), con=ENGINE)

        seed_data = benchmark_data[benchmark_data["seed"] == SEED]
        mean = seed_data["meanExecTime"][0]
        std = seed_data["stdExecTime"][0] * STD_MULTIPLIER
        means.append(mean)
        stds.append(std)
        idx.append(motenumber)

        max_std = std
        if (mean - std) < 0:
            min_std = mean
        else:
            min_std = std
        min_max.append([min_std, max_std])

    min_max = np.array(min_max)
    print(min_max)
    min_max = np.transpose(min_max)
    print(min_max)
    # sys.exit()
    # exectime_ax.errorbar(idx, means, yerr=stds, fmt='-o', markersize=3)
    exectime_ax.errorbar(idx, means, yerr=min_max, fmt='-o', markersize=3)
    # exectime_ax.plot(idx, means)

    exectime_ax.legend(["coordinated"], loc="upper left")
    # exectime_ax.set_title("Mean execution times")
    exectime_ax.set_ylabel("(b)\nmean exec. \ntime [seconds]", multialignment='center')
    # exectime_ax.set_ylim([-0.25, np.amax(min_max.flatten()) + 0.25])
    # exectime_ax.set_yscale('symlog')
    # exectime_ax.set_xlabel("number of motes")

    sizes = []
    idx = []
    for motenumber in MOTES:
        ENGINE = sqlalchemy.create_engine("sqlite:///results_{}motes_good.sqlite3".format(motenumber), echo=False)
        benchmark_data = pd.read_sql("SELECT * FROM benchmarks WHERE experimentType='{}'".format("coordinated"), con=ENGINE)

        seed_data = benchmark_data[benchmark_data["seed"] == SEED]
        sizes.append(seed_data["coordinationMemory"][0])
        idx.append(motenumber)

    msgsize_ax.plot(idx, sizes)

    msgsize_ax.legend(["coordinated"])
    # msgsize_ax.set_title("Message size")
    msgsize_ax.set_ylabel("(c)\nmsg. size\n[\# elements]", multialignment='center')
    # msgsize_ax.set_xlabel("number of motes")

    sizes = []
    idx = []
    for motenumber in MOTES:
        ENGINE = sqlalchemy.create_engine("sqlite:///results_{}motes_good.sqlite3".format(motenumber), echo=False)
        benchmark_data = pd.read_sql("SELECT * FROM benchmarks WHERE experimentType='{}'".format("coordinated"), con=ENGINE)

        seed_data = benchmark_data[benchmark_data["seed"] == SEED]
        sizes.append(seed_data["qtableMemory"][0])
        idx.append(motenumber)

    memory_ax.plot(idx, sizes)

    memory_ax.legend(["coordinated"])
    # memory_ax.set_title("Total Q-table size")
    memory_ax.set_ylabel("(d)\nQ-table size\n[\# elements]", multialignment='center')
    memory_ax.set_xlabel("number of motes")
    # memory_ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:.0E}"))

    fig.savefig("plots/Plot_Scalability.pgf")
    fig.savefig("plots/Plot_Scalability.pdf")

if __name__ == "__main__":
    main()
