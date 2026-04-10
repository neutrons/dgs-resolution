# to run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
#
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100

import warnings

import dash.dependencies as dd
import dash.html as html
from dash import dcc
import numpy as np
import plotly.graph_objs as go


from dgs_resolution.arcs.exp import fc1_highres_data, fc1data, fc2data
from dgs_resolution.arcs import model as arcsmodel

min_flux = 10000

unique_nominal_Eis = set(list(fc1data.Ei_list) + list(fc2data.Ei_list) + list(fc1_highres_data.Ei_list))
unique_nominal_Eis = sorted(list(unique_nominal_Eis))
choppers = ["ARCS-700-1.5-AST", "ARCS-100-1.5-AST", "ARCS-700-0.5-AST"]
chopper_freqs = np.arange(60, 601, 60)
extra_info = dict(
    chopper_freqs=("nu", "%sHz"), RunNumber=("Run no.", "%d"), FWHM_percentages=("Resolution percentage", "%.1f%%")
)

# interface
def build_interface(app):
    # static figures
    ch11 = fc1data.createPlotXY_on_condition(condition=fc1data.intensity > min_flux, x="Ei", y="intensity", extra_info=extra_info)
    ch11.name = "Experimental: ARCS-700-1.5"
    ch21 = fc2data.createPlotXY_on_condition(condition=fc2data.intensity > min_flux, x="Ei", y="intensity", extra_info=extra_info)
    ch21.name = "Experimental: ARCS-100-1.5"
    ch31 = fc1_highres_data.createPlotXY_on_condition(condition=fc1_highres_data.intensity > min_flux, x="Ei", y="intensity", extra_info=extra_info)
    ch31.name = "Experimental: ARCS-700-0.5"
    fig1 = go.Figure(data=[ch11, ch21, ch31])
    fig1.update_xaxes(title_text='Ei (meV)', type='log')
    fig1.update_yaxes(title_text='Flux (counts/s/cm^2/MW)', type='log')
    fig1.update_layout(showlegend=True)

    ch12 = fc1data.createPlotXY_on_condition(condition=fc1data.intensity > min_flux, x="Ei", y="FWHM", extra_info=extra_info)
    ch12.name = "Experimental: ARCS-700-1.5"
    ch22 = fc2data.createPlotXY_on_condition(condition=fc2data.intensity > min_flux, x="Ei", y="FWHM", extra_info=extra_info)
    ch22.name = "Experimental: ARCS-100-1.5"
    ch32 = fc1_highres_data.createPlotXY_on_condition(condition=fc1_highres_data.intensity > min_flux, x="Ei", y="FWHM")
    ch32.name = "Experimental: ARCS-700-0.5"
    fig2 = go.Figure(data=[ch12, ch22, ch32])
    fig2.update_xaxes(title_text='Ei (meV)', type='log')
    fig2.update_yaxes(title_text='FWHM (meV)', type='log')
    fig2.update_layout(showlegend=True)

    # select Ei
    Ei_select = dcc.Dropdown(
        id="Ei_select",
        value=100.0,
        options=[dict(label=str(_), value=_) for _ in unique_nominal_Eis],
    )
    Ei_widget_elements = [
        html.Label("Select incident energy (meV)"),
        Ei_select,
    ]
    #
    return html.Div(
        children=[
            html.H4("Flux(Intensity) vs Resolution"),
            html.Div([
                    dcc.Graph(figure=fig1), 
                    ], style=dict(width="50em"),
                ),
            html.Div([
                    dcc.Graph(figure=fig2), 
                    ], style=dict(width="50em"),
                ),
            html.Div(Ei_widget_elements, style=dict(width="15em")),
            html.Div(
                [
                    dcc.Graph(
                        id="arcs-flux_vs_fwhm",
                    ),  # Flux(intensity) vs FWHM
                    dcc.Graph(
                        id="arcs-fwhm_vs_freq",
                    ),  # FWHM vs chopper frequency
                    dcc.Graph(
                        id="arcs-flux_vs_freq",
                    ),  # Flux(intensity) vs chopper frequency
                ],
                style=dict(width="50em"),
            ),
        ]
    )


# exp Flux vs FWHM
max_res_percentage = 15.0
plot_opts = dict(extra_info=extra_info, max_res_percentage=max_res_percentage)


def getFlux_vs_FWHMdata(data, Ei, name):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition=(data.intensity > min_flux))
    plot = data.createPlotXY(Ei, "FWHM", "intensity", **plot_opts1)
    plot.name = "Experimental: " + name
    return plot

def getFWHM_vs_freq_data(data, Ei, name):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition=(data.intensity > min_flux))
    plot = data.createPlotXY(Ei, "chopper_freqs", "FWHM", **plot_opts1)
    plot.name = "Experimental: " + name

    # model
    x = chopper_freqs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y = [float(arcsmodel.elastic_res_flux(Ei=Ei, chopper=name+"-AST", chopper_freq=xi)[0]) for xi in x]

    modelplot = go.Scatter(x=x, y=y, mode="lines")
    modelplot.name = "PyChop: " + name
    return [plot, modelplot]


def getFlux_vs_freq_data(data, Ei, name):
    plot_opts1 = dict(plot_opts)
    plot_opts1.update(extra_condition=(data.intensity > min_flux))
    plot = data.createPlotXY(Ei, "chopper_freqs", "intensity", **plot_opts1)
    plot.name = "Experimental: " + name

    # model
    x = chopper_freqs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y = [float(arcsmodel.elastic_res_flux(Ei=Ei, chopper=name+"-AST", chopper_freq=xi)[1]) for xi in x]

    if np.sum(np.isfinite(y))>1:

        modelplot = go.Scatter(x=x, y=y, mode="lines")
        modelplot.name = "PyChop: " + name
        return [plot, modelplot]
    else:
        return [plot]

def build_callbacks(app):
    @app.callback(
        [
            dd.Output(component_id="arcs-flux_vs_fwhm", component_property="figure"),
            dd.Output(component_id="arcs-fwhm_vs_freq", component_property="figure"),
            dd.Output(component_id="arcs-flux_vs_freq", component_property="figure"),
        ],
        [
            dd.Input("Ei_select", "value"),
        ],
    )
    def update_figure(Ei):
        Ei = float(Ei)

        data = [
            getFlux_vs_FWHMdata(fc1data, Ei, "ARCS-700-1.5"),
            getFlux_vs_FWHMdata(fc2data, Ei, "ARCS-100-1.5"),
            getFlux_vs_FWHMdata(fc1_highres_data, Ei, "ARCS-700-0.5"),
        ]


        data2 = getFWHM_vs_freq_data(fc1data, Ei, "ARCS-700-1.5") +\
            getFWHM_vs_freq_data(fc2data, Ei, "ARCS-100-1.5") +\
            getFWHM_vs_freq_data(fc1_highres_data, Ei, "ARCS-700-0.5")

        data3 = getFlux_vs_freq_data(fc1data, Ei, "ARCS-700-1.5") +\
            getFlux_vs_freq_data(fc2data, Ei, "ARCS-100-1.5") +\
            getFlux_vs_freq_data(fc1_highres_data, Ei, "ARCS-700-0.5")
    
        return (
            {
                "data": data,
                "layout": dict(
                    title={"text": "Flux vs resolution"},
                    showlegend=True,
                    xaxis=dict(
                        title={"text": "FWHM (meV)"},
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title={"text": "Flux (counts/s/cm^2/MW)"},
                        showspikes=True,
                    ),
                ),
            },
             {
                "data": data2,
                "layout": dict(
                    title={"text": "FWHM vs Chopper Frequency"},
                    showlegend=True,
                    xaxis=dict(
                        title={"text": "Chopper frequency (Hz)"},
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title={"text": "FWHM (meV)"},
                        showspikes=True,
                    ),
                ),
            },
             {
                "data": data3,
                "layout": dict(
                    title={"text": "Flux vs Chopper Frequency"},
                    showlegend=True,
                    xaxis=dict(
                        title={"text": "Chopper frequency (Hz)"},
                        showspikes=True,
                    ),
                    yaxis=dict(
                        title={"text": "Flux (counts/s/cm^2/MW)"},
                        showspikes=True,
                    ),
                ),
            },
        )

    return
