import os
import sys

import numpy as np

from dgs_resolution.pychop import PyChop2

here = os.path.abspath(os.path.dirname(__file__))

yamlpath = os.path.join(here, "arcs-09122018.yaml")

scale_flux = 600


def res_vs_E(E, chopper="ARCS-100-1.5-SMI", chopper_freq=600.0, Ei=100.0):
    instrument = PyChop2(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=E, Ei_in=Ei)
    return res


def elastic_res_flux(chopper="ARCS-100-1.5-SMI", chopper_freq=600.0, Ei=100.0):
    instrument = PyChop2(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=0.0, Ei_in=Ei)
    return res[0], flux[0] * scale_flux


def main():
    E = np.arange(0.0, 100.0, 5.0)
    res = res_vs_E(E)
    print(res)
    return


if __name__ == "__main__":
    main()
