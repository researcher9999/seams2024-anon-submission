import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import h5py

import sqlalchemy
import argparse

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

    # motes_data_all = pd.read_sql("SELECT * FROM motes", con=ENGINE)
    # reward_data_all = pd.read_sql("SELECT experimentType, rewardTotal, seed FROM rewards", con=ENGINE)

    # for n, g in reward_data_all.groupby("experimentType"):
    #     g_summed = g.groupby("seed")["rewardTotal"].sum()
    #     print(n, g_summed.mean(), g_summed.std())
    # sys.exit()

    for seed in SEEDS:
        fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(3.3, 3 * 0.8), tight_layout=True)
        rew_ax = ax[0]
        ener_ax = ax[1]
        col_ax = ax[2]

        sums = {k: dict() for k in EXP_NAMES}
        for exp_name in EXP_NAMES:
            key = "{}_{}".format(exp_name, seed)
            print(key)
            # motes_data = motes_data_all[motes_data_all["experimentName"] == key]
            # reward_data = reward_data_all[reward_data_all["experimentName"] == key]
            motes_data = pd.read_sql("SELECT * FROM motes WHERE experimentName='{}'".format(key), con=ENGINE)
            # reward_data = pd.read_sql("SELECT * FROM rewards WHERE experimentName='{}' AND constraintType='consistency'".format(key), con=ENGINE)
            # reward_data = pd.read_sql("SELECT * FROM rewards WHERE experimentName='{}' AND constraintType='preference'".format(key), con=ENGINE)
            reward_data = pd.read_sql("SELECT * FROM rewards WHERE experimentName='{}'".format(key), con=ENGINE)

            usedEnergy = motes_data.groupby("timestep", as_index=True)["deltaUsedEnergy"].sum()
            # print(usedEnergy)
            # sys.exit()
            org_index = usedEnergy.index
            rename = zip(usedEnergy.index, list(range(len(usedEnergy.index))))
            rename_dict = dict(rename)
            usedEnergy = usedEnergy.rename(index=rename_dict)
            # usedEnergy = usedEnergy.rename(
            # print(usedEnergy, range(len(usedEnergy.index)))

            usedEnergy = usedEnergy.rolling(200).mean()
            usedEnergy.plot(y="deltaUsedEnergy", x="timestep", ax=ener_ax)
            sums[exp_name]["usedEnergy"] = motes_data["deltaUsedEnergy"].sum()
            print(usedEnergy.sum())

            # reward_data["reward"] = reward_data["rewardEnergy"] + reward_data["rewardFailures"] + reward_data["rewardCollisions"]
            reward_data["reward"] = reward_data["rewardTotal"]
            sums[exp_name]["reward"] = reward_data["reward"].sum()
            sums[exp_name]["rewardEnergy"] = reward_data["rewardEnergy"].sum()
            reward_summed = reward_data.groupby("timestepLastObservation", as_index=True)["reward"].sum()
            reward_summed = reward_summed.rename(index=rename_dict)
            reward_summed_rolling = reward_summed.rolling(200).mean()
            reward_summed_rolling.plot(y="reward", ax=rew_ax)

            collisions = motes_data.groupby("timestep", as_index=True)["deltaCollisions"].sum()
            collisions = collisions.rename(index=rename_dict)
            collisions = collisions.rolling(200).mean()
            collisions.plot(y="deltaCollisions", x="timestep", ax=col_ax)
            sums[exp_name]["collisions"] = motes_data["deltaCollisions"].sum()
            print(collisions.sum())

        print(sums)
        # rew_ax.legend(["{}".format(exp_name) for exp_name in EXP_NAMES])
        # ener_ax.legend(["{}".format(exp_name) for exp_name in EXP_NAMES],loc="lower right")
        # col_ax.legend(["{}".format(exp_name) for exp_name in EXP_NAMES])

        # rew_ax.set_title("Received reward")
        # ener_ax.set_title("Variations in energy consumption")
        # col_ax.set_title("Variations in collisions")

        rew_ax.set_ylabel("reward")
        rew_ax.set_xlabel("coordination iteration")

        ener_ax.set_ylabel("$\Delta$ energy")
        ener_ax.set_xlabel("coordination iteration")

        col_ax.set_ylabel("$\Delta$ collisions")
        col_ax.set_xlabel("coordination iteration")

        rew_ax.legend(["{}".format(exp_name) for exp_name in
                       EXP_NAMES], bbox_to_anchor=(0, 1.02, 1, 0.2),
                      loc="lower left", mode="expand",
                      borderaxespad=0, ncol=3)

        fig.savefig("plots/Plot_{}.pgf".format(seed))
        fig.savefig("plots/Plot_{}.pdf".format(seed))

if __name__ == "__main__":
    main()
