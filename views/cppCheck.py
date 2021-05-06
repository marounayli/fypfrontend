import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
from app import app
from dash.dependencies import Input, Output
import pandas as pd

labels = ["error", "performance", "portability", "style", "warning"]
base_url = "http://localhost:8081/cppcheck/"


# Generate request based on request_type, custom endpoint path, and a request body using a base_url
def request_generator(request_type, path, request_body):
    if request_type == "post":
        response = requests.post(base_url + path, json=request_body)
    else:
        response = requests.get(base_url + path)

    return response.json()


# API call to get the last 10 builds names
def fetch_latest_build():
    return request_generator("get", "build-names/last/10", None)


# Create a dictionary representing the data for the bar graph
def parse_data_for_comparison(value):
    # To avoid returning a dic of null
    if value is None or len(value) == 0:
        return {}
    # API call to get build stats for specific build names fetched from the dropdown
    comparison_data = request_generator("post", "build-names", {"buildNames": value})

    res = dict()
    for select_value in value:
        res[select_value] = dict()
    # fetch stats and fill the res dictionary with relevant info
    for data in comparison_data:
        for type_of_data in data:
            if type_of_data != 'buildName':
                res[data['buildName']][type_of_data] = data[type_of_data]
    # return the data to visualize on the graph
    return px.bar(pd.DataFrame.from_dict(res), barmode="group", template="presentation")


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
                              html.Div(
                                  id='my-dropdown-parent',
                                  children=[dcc.Store(id='data-store'),
                                            dcc.Interval(interval=120 * 1000, id='interval'),
                                            dcc.Dropdown(
                                                id='my-dropdown',
                                                options=[],
                                                value=fetch_latest_build(),
                                                multi=True
                                            )
                                            ]
                              ),
                              html.Div(id='my-container'),
                              dcc.Graph(
                                  id='ComparatorGraph',
                                  figure={}
                              ),
                              ])]


@app.callback(
    Output('ComparatorGraph', 'figure'),
    Input('my-dropdown', 'value')
)
def update_graph(value):
    # print("test")
    return parse_data_for_comparison(value)


@app.callback(
    Output("Aggregation-Graph", "figure"),
    Input("bar-input", "value")
)
def bar_render(number):
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
    fig1 = px.bar(pd.DataFrame.from_dict(parse_data(request_generator("post", "agg", body))),
                  barmode="group", template="presentation")
    return fig1


@app.callback(
    Output("graph", "figure"),
    Input("input", "value"),
)
def graph_render(number):
    if number:
        request_url = "last/{n}?n=" + str(number)
    else:
        request_url = ""
    df = parse_response(request_generator("get", request_url, None))
    fig = px.line(df, x="Builds", y=labels, height=800, title="CppCheck Data", template="presentation")
    fig.update_traces(mode='markers+lines')
    return fig


# @app.callback(
#     Output('my-dropdown', 'options'),
#     Input('my-dropdown-parent', 'n_clicks'))
# def update_comp_graph(n_clicks):
#     return [{'label': i, 'value': i} for i in fetch_latest_build()]
#

@app.callback(
    Output('data-store', 'data'),
    Input('interval', 'n_intervals'))
def update_time(n_intervals):
    # print('fetching from api', fetch_latest_build())
    return fetch_latest_build()


@app.callback(
    Output('my-dropdown', 'options'),
    [Input('data-store', 'data'),
     Input('my-dropdown-parent', 'n_clicks')])
def update_comp_graph(data, n_clicks):
    # print('fetching from store', data)
    if data:
        return [{'label': i, 'value': i} for i in data]
