import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests
import dash

from app import app

agg_request_url = "http://localhost:8081/bazel-stats/agg"
aggregationSize = 2
aggregationType = [
    "sum", "avg", "max", "min"
]
body = {
    "aggregationSize": aggregationSize,
    "aggregations": aggregationType
}
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

df = pd.DataFrame({
    "country": ["2011", "2012", "2013", "2014", "2015", "2016"],

})

body2 = {
    "listOfBuildNames": []
}

comparator_graph = {
    'Jean': {'total_launch_phase_time': 0.0146, 'total_init_phase_time': 0.155, 'total_loading_phase_time': 0.301,
             'total_analysis_phase_time': 0.011, 'total_preparation_phase_time': 0.001,
             'total_execution_phase_time': 0.025,
             'total_finish_phase_time': 0.001, 'total_run_time': 0.142}}


def fetch_data_aggregation(request):
    aggregation_request = requests.post(request, json=body, headers=headers)
    json_data = aggregation_request.json()
    return json_data


def fetch_data_last_n_bazel_stats(request):
    aggregation_request = requests.get(request)
    json_data = aggregation_request.json()
    return json_data


def fetch_latest_build_names():
    build_names_json = requests.get("http://localhost:8081/bazel-stats/build-names/10").json()
    print(build_names_json)
    build_names_list = []
    for build in build_names_json:
        build_names_list.insert(0, build['buildName'])

    return pd.DataFrame(build_names_list, columns=['name']).name.unique()


def parse_data(json_data):
    res = dict()
    for key in json_data.keys():
        res[key] = dict()
    for key in json_data.keys():
        for obj in json_data[key]["payload"]:
            res[key][obj["name"]] = obj["time"]
    return res


def compare_data(value):
    print(value)
    json = requests.post("http://localhost:8081/bazel-stats/build", json=body2, headers=headers).json()

    res = dict()

    for select_value in value:
        res[select_value] = dict()

    for build_stats in json:
        for type_of_stats in build_stats['payload']:
            res[build_stats['build_name']][type_of_stats['name']] = type_of_stats['time']
    print("--------------------------")
    print(res)
    return px.bar(pd.DataFrame.from_dict(res), barmode="group")


fig = px.bar(pd.DataFrame.from_dict(parse_data(fetch_data_aggregation(agg_request_url))), barmode="group")

dropdown = fetch_latest_build_names()
fig2 = px.bar(pd.DataFrame.from_dict(comparator_graph), barmode="group")

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
            options=[{'label': i, 'value': i} for i in fetch_latest_build_names()],
            multi=True

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
    body2['listOfBuildNames'] = value;
    return compare_data(value)
