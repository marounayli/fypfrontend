import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_table
import requests
from app import app
from dash.dependencies import Input, Output
import pandas as pd


def parse_data(json_data):
    res = dict()
    for key in json_data.keys():
        res[key] = dict()
        # print(key)
    for key in json_data.keys():
        for obj in json_data[key]:
            if obj != "build-name":
                # print(type(json_data[key][obj]))
                res[key][obj] = json_data[key][obj]
    # print(res)
    return res


# parse_data(fetch_data_aggregation(agg_request_url))


labels = ["error", "performance", "portability", "style", "warning"]


def fetch_data(request):
    check_request = requests.get(request)
    json_data = check_request.json()
    return json_data


def parse_response(payload):
    res = dict()
    res["Builds"] = list()
    for key in labels:
        res[key] = list()
    for elt in payload:
        for key in elt:
            if key in labels:
                res[key].append(elt[key])
            elif key == "buildName":
                res["Builds"].append(elt[key])
    # print(res)
    return res


cpp_check_layout = [html.Div([html.H3("Statistics on the latest cppChecks"),
                              dcc.Input(id="input", type="number", placeholder="Enter Limit"),
                              html.Div(id="number-out"),
                              dbc.Button(
                                  "Refresh",
                                  id="button",
                                  className="mb-3 order-button",
                                  color="primary",
                              ),
                              dcc.Graph(
                                  figure={},
                                  id='graph'
                              ),
                              html.H3("Aggregation of the last cppChecks"),
                              dcc.Input(id="bar-input", value=2, type="number", placeholder="Enter Aggregation Size"),
                              html.Div(id="bar-number-out"),
                              dcc.Graph(
                                  id='Aggregation-Graph',
                                  figure={}
                              ),
                              ])]


@app.callback(
    Output("Aggregation-Graph", "figure"),
    Input("bar-input", "value")
)
def bar_render(number):
    agg_request_url = "http://localhost:8081/cppcheck/agg"
    if number is None:
        number = 2
    aggregation_size = int(number)
    # print(type(number))
    aggregation_type = [
        "sum", "avg", "max", "min"
    ]
    body = {
        "aggregationSize": int(aggregation_size),
        "aggregations": aggregation_type
    }
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    aggregation_request = requests.post(agg_request_url, json=body, headers=headers)
    json_data = aggregation_request.json()
    fig1 = px.bar(pd.DataFrame.from_dict(parse_data(json_data)), barmode="group")
    return fig1


@app.callback(
    Output("number-out", "children"),
    Input("input", "value")
)
def number_render(number):
    return "input: {}".format(number)


@app.callback(
    Output("graph", "figure"),
    Input("input", "value"),
    Input('button', 'n_clicks')
)
def graph_render(number, n_clicks):
    if number:
        request_url = "http://localhost:8081/cppcheck/last/{n}?n=" + str(number)
    else:
        request_url = "http://localhost:8081/cppcheck"
    df = parse_response(fetch_data(request_url))
    fig = px.line(df, x="Builds", y=labels, height=800, title="CppCheck Data")
    fig.update_traces(mode='markers+lines')
    fig.update_layout(
        paper_bgcolor="LightSteelBlue",
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True,
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
    )
    return fig
