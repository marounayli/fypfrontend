import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests
from dash.dependencies import Input, Output
from app import app

base_url = "http://localhost:8081/bazel-stats/"


# Method that receives the shape of a given request and returns a json object from the specified stats service.
def request_generator(request_type, path, request_body):
    if request_type == "post":
        response = requests.post(base_url + path, json=request_body).json()
    else:
        response = requests.get(base_url + path).json()

    return response


def fetch_data_aggregation(size):
    aggregation_data = request_generator(request_type="post", path="/agg", request_body={
        "aggregationSize": size,
        "aggregations": [
            "sum", "avg", "max", "min"
        ]
    })
    return aggregation_data


# fetch a list of the latest 10 bazel-builds objects for the dropdown list to be selected for stats comparison.
# TODO: you might need to make a button for fetch the latest N builds and limit them from the UI
def fetch_latest_build_names(size):
    build_names_json = request_generator("get", "/build-names/{}".format(size), None)
    build_names_list = []
    for build in reversed(build_names_json):
        build_names_list.insert(0, build['buildName'])

    data = pd.DataFrame(build_names_list, columns=['name']).name.unique()
    return data


def parse_data_for_aggregation(json_data):
    res = dict()
    for key in json_data.keys():
        res[key] = dict()
    for key in json_data.keys():
        for obj in json_data[key]["payload"]:
            res[key][obj["name"]] = obj["time"]
    return res


def parse_data_for_comparison(value):
    if value is None or len(value) == 0:
        return {}

    # build request to fetch data.
    comparison_data = request_generator(request_type="post", path="/build", request_body={"listOfBuildNames": value})
    res = dict()

    for select_value in value:
        res[select_value] = dict()

    for build_stats in comparison_data:
        for type_of_stats in build_stats['payload']:
            res[build_stats['build_name']][type_of_stats['name']] = type_of_stats['time']

    return px.bar(pd.DataFrame.from_dict(res), barmode="group")


bazel_stats_layout = html.Div(children=[

    html.H1(children='Bazel Stats'),

    html.Div(children='''
        A Graph That Represents The Aggregation Of The Last N Bazel Builds.
    '''),

    dcc.Input(id="bazel-stats-agg-input", value=2, type="number", placeholder="Enter Bazel Stats Aggregation Size",
              min=2),
    dcc.Graph(
        id='Bazel-Stats-Aggregation-Graph',
        figure={}
    ),

    html.Div(
        id='my-dropdown-div-parent-bazel-stats',
        children=[
            dcc.Store(id='bazel-stats-data-store'),
            dcc.Interval(interval=120 * 1000, id='bazel-stats-interval'),
            dcc.Dropdown(
                id='bazel-stats-dropdown',
                value=fetch_latest_build_names(2),
                options=[],
                multi=True,

            )
        ]

    ),

    html.Div(id='dd-output-bazel-build-names-container'),
    dcc.Graph(
        id='Comparator-Graph',
        figure={},
    )
])


# Callback that listen to the dropdown list. On each Selection of a bazel build that is provided within this dropdown
# The Graph will be updated based on this Selection
@app.callback(
    dash.dependencies.Output('Comparator-Graph', 'figure'),
    [dash.dependencies.Input('bazel-stats-dropdown', 'value')])
def update_graph(value):
    return parse_data_for_comparison(value)


# Update the aggregation graph based on the size provided by the input box
@app.callback(
    dash.dependencies.Output("Bazel-Stats-Aggregation-Graph", "figure"),
    dash.dependencies.Input("bazel-stats-agg-input", "value")
)
def bazel_stats_aggregation_graph_update(number):
    if number is None:
        number = 2
    aggregation_data = fetch_data_aggregation(number)
    return px.bar(pd.DataFrame.from_dict(parse_data_for_aggregation(aggregation_data)), barmode="group")


@app.callback(
    Output('bazel-stats-data-store', 'data'),
    Input('bazel-stats-interval', 'n_intervals'))
def update_time(n_intervals):
    print('fetching from api', fetch_latest_build_names(20))
    return fetch_latest_build_names(10)


@app.callback(
        Output('bazel-stats-dropdown', 'options'),
    [
        Input('bazel-stats-data-store', 'data'),
        Input('my-dropdown-div-parent-bazel-stats', 'n_clicks')
    ])
def update_comp_graph(data, n_clicks):
    print('fetching from store', data)
    if data:
        return [{'label': i, 'value': i} for i in data]
