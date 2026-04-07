import dash.dependencies as dd
import dash.html as html
import numpy as np
from dash import dcc

from dgs_resolution.hyspec import exp

operation_modes = [
    "HU",
    "PG",
]


# interface
def build_interface(app):
    # select chopper mode
    operation_mode = dcc.Dropdown(
        id="hyspec_operation_mode",
        value="HU",
        options=[dict(label=str(_), value=_) for _ in operation_modes],
    )
    return html.Div(
        children=[
            html.Div(
                [
                    operation_mode,
                    dcc.Graph(
                        id="hyspec-fwhm_vs_Ei",
                    ),
                    dcc.Graph(
                        id="hyspec-flux_vs_Ei",
                    ),
                ],
                style=dict(width="50em"),
            ),
        ]
    )


# plot
def sorted_xy_byx(x, y):
    s = np.argsort(x)
    return np.array(x)[s], np.array(y)[s]


extra_info = {
    "Run": ("Run number", "%s"),
    "FWHM_percentages": ("Resolution percentage", "%.1f%%"),
    "Fermi": ("Fermi chopper frequency", "%.0f"),
}


def getFWHM_vs_Ei(operation_mode):
    data = exp.data[operation_mode]
    expplot = data.createPlotXY_on_condition(None, "energy_plus_freq", "FWHM", extra_info=extra_info)
    expplot.name = "Experimental"
    return [
        expplot,
    ]


def getFlux_vs_Ei(operation_mode):
    data = exp.data[operation_mode]
    expplot = data.createPlotXY_on_condition(None, "energy_plus_freq", "flux", extra_info=extra_info)
    expplot.name = "Experimental"
    return [expplot]


def build_callbacks(app):
    @app.callback(
        [
            dd.Output(component_id="hyspec-fwhm_vs_Ei", component_property="figure"),
            dd.Output(component_id="hyspec-flux_vs_Ei", component_property="figure"),
        ],
        [
            dd.Input("hyspec_operation_mode", "value"),
        ],
    )
    def update_figures(mode):
        fwhm_data = getFWHM_vs_Ei(mode)
        flux_data = getFlux_vs_Ei(mode)
        return [
            {
                "data": fwhm_data,
                "layout": dict(
                    title={"text": "Resolution vs incident energy"},
                    showlegend=True,
                    xaxis=dict(
                        title={"text": "Ei (meV)"},
                        type="log",
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title={"text": "FWHM (meV)"},
                        type="log",
                        showspikes=True,
                    ),
                ),
            },
            {
                "data": flux_data,
                "layout": dict(
                    title={"text": "Flux vs incident energy"},
                    showlegend=True,
                    xaxis=dict(
                        title={"text": "Ei (meV)"},
                        type="log",
                        showspikes=True,
                    ),
                    yaxis=dict(
                        # title={'text': 'Flux (counts/s/cm^2/MW)'},
                        title={"text": "Flux (arb. unit)"},
                        type="log",
                        showspikes=True,
                    ),
                ),
            },
        ]

    return
