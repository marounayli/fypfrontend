import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests

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


def fetch_data_aggregation(request):
    aggregation_request = requests.post(request, json=body, headers=headers)
    json_data = aggregation_request.json()
    return json_data


def fetch_data_last_n_bazel_stats(request):
    aggregation_request = requests.get(request)
    json_data = aggregation_request.json()
    return json_data


def fetch_latest_build_names():
    build_names_json = requests.get("http://localhost:8081/bazel-stats/build-names/3").json()
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
    # print(res)
    return res


def compare_data(json_data):
    json_data2 = fetch_data_last_n_bazel_stats("http://localhost:8081/bazel-stats/2")

    return parse_data(json_data)


fig = px.bar(pd.DataFrame.from_dict(parse_data(fetch_data_aggregation(agg_request_url))), barmode="group")

fig2 = px.bar(pd.DataFrame.from_dict(compare_data(fetch_data_aggregation(agg_request_url))), barmode="group")

dropdown = fetch_latest_build_names()

bazel_stats_layout = html.Div(children=[

    html.H1(children='Bazel Stats'),

    html.Div(children='''
        A Graph That Represents The Aggregation Of The Last N Bazel Builds.
    '''),

    dcc.Graph(
        id='Aggregation Graph',
        figure=fig
    ),

    html.Div([html.P()
                 , html.H5('Latest Bazel Builds')
                 , dcc.Dropdown(id='country-drop'
                                , options=[
                {'label': i, 'value': i} for i in fetch_latest_build_names()],
                                value=['US'],
                                multi=True
                                )]),

    html.Div(children='''
    A Graph That Compares 2 Chosen Builds.
    '''),

    dcc.Graph(
        id='Comparator Graph',
        figure=fig2
    ),

])
