# To run, add parent directory of PyChop to PYTHONPATH
# then $ python {thisfile}
# By default, the server will run in production mode (waitress) and will not shut down when the browser window is closed
# To enable single-user mode (server shuts down when browser window is closed), run with the `--single` flag:
# $ python app.py --single
# To run in debug mode (Flask development server with hot reloading), use the `debug` flag:
# $ python app.py debug
# Main app: http://localhost:8050/
# Download: http://localhost:8050/download?chopper_select=ARCS-100-1.5-AST&chopper_freq=600&Ei=100


import os
import signal

import dash
import dash.html as html
from dash import dcc

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

single_user_mode = False

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "DGS resolution"

# no official support from dash for mathjax
# the following only works for static html
# mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
# app.scripts.append_script({ 'external_url' : mathjax })


def set_headers(response):
    headers = response.headers
    value = "max-age=31556926; includeSubDomains; preload"
    headers["Strict-Transport-Security"] = value
    return response


from dgs_resolution import arcs
from dgs_resolution import cncs
from dgs_resolution import hyspec
from dgs_resolution import sequoia

tab_style = dict(margin="0em 2em")
instruments = ["arcs", "sequoia", "cncs", " hyspec"]
tabs = []
for instr in instruments:
    interface = eval(instr).build_interface(app)
    tab = dcc.Tab(label=instr.upper(), value=instr, children=html.Div([interface], style=tab_style))
    tabs.append(tab)

app.layout = html.Div(
    [
        dcc.Tabs(tabs, vertical=True),
    ]
)
app.server.after_request(set_headers)


for instr in instruments:
    mod = eval(instr)
    mod.build_callbacks(app)


# Add the shutdown/cleanup route
@app.server.route("/browser-closed", methods=["POST"])
def browser_closed():
    global single_user_mode
    if single_user_mode:
        print("Browser window or tab was closed! Server shutting down ...")
        # Add your server-side cleanup logic here, e.g., deleting temporary files, updating a database, etc.
        # Note: Do not use this method to shut down the *entire* server in a multi-user environment.

        # If you're running a single-user app and truly want to stop the server process:
        os.kill(os.getpid(), signal.SIGINT)

    return "OK", 200


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the DGS resolution app.", usage="python app.py [--mode single|server] [--debug]"
    )
    parser.add_argument(
        "-m",
        "--mode",
        help="Mode to run the app in: `single` for single-user mode, or `production`",
        default="single",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Run the app in debug mode (Flask development server with hot reloading).",
    )
    args = parser.parse_args()

    if args.mode == "single":
        global single_user_mode
        single_user_mode = True
        import webbrowser

        webbrowser.open_new("http://localhost:8050/")

    if args.debug:
        app.run(debug=True, threaded=True)
    else:
        from waitress import serve

        serve(app.server, host="0.0.0.0", port=8050, threads=12, url_scheme="https")


if __name__ == "__main__":
    main()
