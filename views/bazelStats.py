import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests
import dash
import dash_bootstrap_components as dbc

from app import app

base_url = "http://localhost:8081/bazel-stats/"

body2 = {
    "listOfBuildNames": []
}


def request_generator(request_type, path, request_body):
    if request_type == "post":
        response = requests.post(base_url + path, json=request_body).json()
    else:
        response = requests.get(base_url + path).json()

    return response


def fetch_data_aggregation():
    aggregation_data = request_generator(request_type="post", path="/agg", request_body={
        "aggregationSize": 2,
        "aggregations": [
            "sum", "avg", "max", "min"
        ]
    })
    return aggregation_data


def fetch_latest_build_names():
    ## TODO: you might need to make a button for fetch the latest N builds and limit them from the UI
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
    comparison_data = request_generator(request_type="post", path="/build", request_body={"listOfBuildNames": value})
    res = dict()

    for select_value in value:
        res[select_value] = dict()

    for build_stats in comparison_data:
        for type_of_stats in build_stats['payload']:
            res[build_stats['build_name']][type_of_stats['name']] = type_of_stats['time']
    print(res)
    return px.bar(pd.DataFrame.from_dict(res), barmode="group")


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
            id="button",
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


@app.callback(
    dash.dependencies.Output('Comparator-Graph', 'figure'),
    [dash.dependencies.Input('dd-output-bazel-build-names-container-dropdown', 'value')])
def update_graph(value):
    return parse_data_for_comparison(value)


@app.callback(
    dash.dependencies.Output('dd-output-bazel-build-names-container-dropdown', 'options'),
    [dash.dependencies.Input('button', 'n_clicks')])
def update_graph(n_clicks):
    return [{'label': i, 'value': i} for i in fetch_latest_build_names()]
