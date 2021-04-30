import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
from app import app
from dash.dependencies import Input, Output
import pandas as pd

labels = ["error", "performance", "portability", "style", "warning"]


def fetch_latest_build():
    request = "http://localhost:8081/cppcheck/build-names/last/10"
    build_names_json = requests.get(request).json()
    return build_names_json


def parse_data_for_comparison(value):
    if value is None or len(value) == 0:
        return {}
    request = "http://localhost:8081/cppcheck/build-names"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    data = requests.post(request, json={"buildNames": value}, headers=headers)
    comparison_data = data.json()
    res = dict()

    for select_value in value:
        res[select_value] = dict()

    for data in comparison_data:
        print(data)
        for type_of_data in data:
            if type_of_data != 'buildName':
                res[data['buildName']][type_of_data] = data[type_of_data]
    return px.bar(pd.DataFrame.from_dict(res), barmode="group")


def fetch_data_aggregation(request, body, headers):
    aggregation_request = requests.post(request, json=body, headers=headers)
    json_data = aggregation_request.json()
    return json_data


def fetch_data(request):
    check_request = requests.get(request)
    json_data = check_request.json()
    return json_data


def parse_data(json_data):
    res = dict()
    for key in json_data.keys():
        res[key] = dict()
        # print(key)
    for key in json_data.keys():
        for obj in json_data[key]:
            if obj != "build-name":
                res[key][obj] = json_data[key][obj]
    # print(res)
    return res


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
                              dcc.Dropdown(
                                  id='dd-output-cpp-build-names-container-dropdown',
                                  options=[],
                                  value=fetch_latest_build(),
                                  multi=True
                              ),
                              dbc.Button(
                                  "Refresh",
                                  id="button",
                                  className="mb-3 order-button",
                                  color="primary",
                              ),
                              html.Div(id='dd-output-cpp-build-names-container'),
                              dcc.Graph(
                                  id='ComparatorGraph',
                                  figure={}
                              ),
                              ])]


@app.callback(
    Output('ComparatorGraph', 'figure'),
    Input('dd-output-cpp-build-names-container-dropdown', 'value')
)
def update_graph(value):
    return parse_data_for_comparison(value)


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
    fig1 = px.bar(pd.DataFrame.from_dict(parse_data(fetch_data_aggregation(agg_request_url, body, headers))),
                  barmode="group")
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


@app.callback(
    Output('dd-output-cpp-build-names-container-dropdown', 'options'),
    Input('button', 'n_clicks'))
def update_comp_graph(n_clicks):
    return [{'label': i, 'value': i} for i in fetch_latest_build()]
