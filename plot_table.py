import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import h5py

import argparse

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

ENGINE = sqlalchemy.create_engine("sqlite:///results_7motes_good.sqlite3", echo=False)
# ENGINE = sqlalchemy.create_engine("sqlite:///results_good_6motes_5discretization.sqlite3", echo=False)

def main():
    parser = argparse.ArgumentParser(
        prog='Plot results for a given experiment.',
        description='Plot results for a given experiment.')

    parser.add_argument("filename", help="Path to sqlite3 file with results.", type=str)
    args = parser.parse_args()

    ENGINE = sqlalchemy.create_engine("sqlite:///{}".format(args.filename), echo=False)

    motes_data_all = pd.read_sql("SELECT experimentType, seed, deltaUsedEnergy, deltaCollisions FROM motes", con=ENGINE)
    reward_data_all = pd.read_sql("SELECT experimentType, rewardTotal, seed FROM rewards", con=ENGINE)

    for r, m in zip(reward_data_all.groupby("experimentType"), motes_data_all.groupby("experimentType")):
        nr, gr = r
        nm, gm = m
        g_reward_summed = gr.groupby("seed")["rewardTotal"].sum()
        g_energy_summed = gm.groupby("seed")["deltaUsedEnergy"].sum()
        g_collisions_summed = gm.groupby("seed")["deltaCollisions"].sum()

        print("{} & {:.1f} & {:.1f} & {:.1f} & {:.1f} & {:.1f} & {:.1f}\\\\".format(nr,
              g_reward_summed.mean(), g_reward_summed.std(),
              g_energy_summed.mean(), g_energy_summed.std(),
              g_collisions_summed.mean(), g_collisions_summed.std()
                                                                  ))


if __name__ == "__main__":
    main()
