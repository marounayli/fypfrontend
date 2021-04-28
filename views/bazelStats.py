import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests

request_url = "http://localhost:8081/bazel-stats/agg"
aggregationSize = 2
aggregationType = [
    "sum", "min"
]
body = {
    "aggregationSize": aggregationSize,
    "aggregations": aggregationType
}
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

def fetch_data():
    aggregation_request = requests.post(request_url, json=body, headers=headers)
    json_data = aggregation_request.json()
    return json_data


def parse_data(json_data):
    res=dict()
    for key in json_data.keys():
        res[key]=dict()
    print(res)
    for key in json_data.keys():
        for obj in json_data[key]["payload"]:
            res[key][obj["name"]]=obj["time"]
    return res

fig = px.bar(pd.DataFrame.from_dict(parse_data(fetch_data())), barmode="group")

bazel_stats_layout= html.Div(children=[

        html.H1(children='Bazel Stats'),

        html.Div(children='''
        Dash: A web application framework for Python.
    '''),

        dcc.Graph(
            id='example-graph',

            figure=fig
        )
    ])

