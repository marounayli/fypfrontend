import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
from app import app
from dash.dependencies import Input, Output
import pandas as pd


tests_labels = ["testFailed", "testPassed"]


tests_stats_layout = [html.Div([html.H3("Statistics on the latest tests"),
                                dcc.Input(id="tests_input", type="number", placeholder="Enter Limit"),
                                dcc.Graph(
                                    figure={},
                                    id='test_graph'
                                )
                                ])]


def request_generator(request_type, url, request_body):
    if request_type == "post":
        response = requests.post(url, json=request_body)
    else:
        response = requests.get(url)

    return response.json()


def parse_response_test(payload):
    res = dict()
    res["Builds"] = list()
    for key in tests_labels:
        res[key] = list()
    for elt in payload:
        for key in elt:
            if key in tests_labels:
                res[key].append(elt[key])
            elif key == "build":
                res["Builds"].append(elt[key]["build_name"])
    return res


@app.callback(
    Output("test_graph", "figure"),
    Input("tests_input", "value"),
)
def graph_render(number):
    if number:
        request_url = "http://localhost:8081/tests" + str(number)
    else:
        request_url = "http://localhost:8081/tests"
    df = parse_response_test(request_generator("get", request_url, None))
    fig = px.line(df, x="Builds", y=tests_labels, height=800, title="CppCheck Data", template="presentation")
    fig.update_traces(mode='markers+lines')
    return fig

