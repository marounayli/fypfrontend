import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests
import dash
import dash_bootstrap_components as dbc

from app import app

base_url = "http://localhost:8081/bazel-stats/"


# Method that receives the shape of a given request and returns a json object from the specified stats service.
def request_generator(request_type, path, request_body):
    if request_type == "post":
        response = requests.post(base_url + path, json=request_body).json()
    else:
        response = requests.get(base_url + path).json()

    return response


# Return an aggregation of a given number of bazel stats aggregation.
# TODO: Ability for the User to select the Aggregation Size Himself
def fetch_data_aggregation():
    aggregation_data = request_generator(request_type="post", path="/agg", request_body={
        "aggregationSize": 2,
        "aggregations": [
            "sum", "avg", "max", "min"
        ]
    })
    return aggregation_data


# fetch a list of the latest 10 bazel-builds objects for the dropdown list to be selected for stats comparison.
# TODO: you might need to make a button for fetch the latest N builds and limit them from the UI
def fetch_latest_build_names():
    build_names_json = request_generator("get", "/build-names/10", None)
    build_names_list = []
    for build in build_names_json:
        build_names_list.insert(0, build['buildName'])

    return pd.DataFrame(build_names_list, columns=['name']).name.unique()


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

    # update graph with new data.
    return px.bar(pd.DataFrame.from_dict(res), barmode="group")


# fetch data of aggregation
# TODO: Reactive Form Linked with a button that specify the Aggregation Size
fig = px.bar(pd.DataFrame.from_dict(parse_data_for_aggregation(fetch_data_aggregation())), barmode="group")

bazel_stats_layout = html.Div(children=[

    html.H1(children='Bazel Stats'),

    html.Div(children='''
        A Graph That Represents The Aggregation Of The Last N Bazel Builds.
    '''),

    dcc.Graph(
        id='Aggregation Graph',
        figure=fig
    ),

    html.Div([
        dcc.Dropdown(
            id='dd-output-bazel-build-names-container-dropdown',
            options=[],
            multi=True

        ),
        dbc.Button(
            "Refresh",
            id="bazel-stats-refresh-btn",
            className="mb-3 order-button",
            color="primary",
        ),

        html.Div(id='dd-output-bazel-build-names-container'),
        dcc.Graph(
            id='Comparator-Graph',
            figure={}
        ),
    ]),

])


# Callback that listen to the dropdown list. On each Selection of a bazel build that is provided within this dropdown
# The Graph will be updated based on this Selection
@app.callback(
    dash.dependencies.Output('Comparator-Graph', 'figure'),
    [dash.dependencies.Input('dd-output-bazel-build-names-container-dropdown', 'value')])
def update_graph(value):
    return parse_data_for_comparison(value)

# On Refresh, the list will fetch any new bazel builds generated.
@app.callback(
    dash.dependencies.Output('dd-output-bazel-build-names-container-dropdown', 'options'),
    [dash.dependencies.Input('bazel-stats-refresh-btn', 'n_clicks')])
def update_graph(n_clicks):
    return [{'label': i, 'value': i} for i in fetch_latest_build_names()]
