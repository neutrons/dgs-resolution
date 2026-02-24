import os

import numpy as np
import pandas as pd

from dgs_resolution import resolution_plot

here = os.path.abspath(os.path.dirname(__file__))

# data
# exp_int_to_flux = 0.00980989028558523 # https://jupyter.sns.gov/user/lj7/notebooks/dv/sns-chops/resolution/CNCS/PyChop/pychop%20-%20Intensity%20and%20VRes_vs_Ei.ipynb


class ExpData(resolution_plot.ExpData):
    def __init__(self, datafile):
        # read data
        print("Reading data. please wait...")
        vdata = self.vdata = pd.read_csv(datafile, delimiter=",")
        print("\tDone")
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.0 * np.pi)
        # self.flux = vdata.counts * exp_int_to_flux
        self.flux = self.intensity  # hack
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.FWHM_percentages = self.FWHM / vdata.Ei * 100.0
        self.Ei_list = list(vdata.Ei.unique())
        self.energy_plus_freq = vdata.Ei + vdata.Fermi / 10000
        return


expdata_HU = ExpData(os.path.join(here, "./hyspec_HU_res_Flux.dat.csv"))
expdata_PG = ExpData(os.path.join(here, "./hyspec_PG_res_Flux.dat.csv"))

data = {
    "HU": expdata_HU,
    "PG": expdata_PG,
}
