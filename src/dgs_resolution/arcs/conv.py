# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import dash
import dash.dependencies as dd
import dash.html as html
import flask
import numpy as np
from dash import dcc

from dgs_resolution import convolution
from dgs_resolution import widget_utils as wu
from dgs_resolution.arcs import exp
from dgs_resolution.arcs import model as arcsmodel
from dgs_resolution.arcs.configuration_widget import chopper_freq_opts, chopper_freqs, create
from dgs_resolution.arcs.inelastic import get_data

# use common util to create interface and callbacks
conv_interface, conv_callback = convolution.create(
    "arcs",
    instrument_params=[
        dd.State(component_id="conv-arcs_Ei_input", component_property="value"),
        dd.State(component_id="conv-arcs_chopper_select", component_property="value"),
        dd.State(component_id="conv-arcs_chopper_freq", component_property="value"),
    ],
    res_function_calculator=get_data,  # args for get_data method must match the sequence in instrument_params
)


def build_interface(app):
    config_widget = create("conv-")
    return html.Div(
        children=[
            config_widget,
            conv_interface(app),
        ]
    )


def build_callbacks(app):
    conv_callback(app)
    return
