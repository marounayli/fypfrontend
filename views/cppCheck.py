import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_table
import requests
from app import app
from dash.dependencies import Input, Output

labels = ["error", "performance", "portability", "style", "warning"]

dummy_data = [
    {"id": 1, "buildName": "test", "error": 10, "performance": 43, "portability": 33, "style": 16, "warning": 55},
    {"id": 2, "buildName": "test2", "error": 13, "performance": 55, "portability": 45, "style": 17, "warning": 55},
    {"id": 3, "buildName": "test3", "error": 23, "performance": 42, "portability": 43, "style": 71, "warning": 39},
    {"id": 4, "buildName": "test4", "error": 43, "performance": 96, "portability": 10, "style": 17, "warning": 19},
    {"id": 5, "buildName": "test5", "error": 45, "performance": 44, "portability": 25, "style": 71, "warning": 49}
]


def fetch_data(request):
    check_request = requests.get(request)
    json_data = check_request.json()
    return json_data


# print(fetch_data(request_url))


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
                              # html.Button("Refresh", id="button", n_clicks=0),
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
                              dash_table.DataTable(
                                  id='table',
                                  columns=[{"name": key, "id": key} for key in labels],
                                  data=dummy_data,
                                  style_header={
                                      'backgroundColor': 'rgb(230, 230, 230)',
                                      'fontWeight': 'bold'
                                  },
                              ),
                              html.Label('Please select one on more aggregations'),
                              dcc.Dropdown(
                                  id="aggregations_dropdown",
                                  options=[
                                      {'label': 'Sum', 'value': 'sum'},
                                      {'label': 'Min', 'value': 'min'},
                                      {'label': 'Max', 'value': 'max'},
                                      {'label': 'Average', 'value': 'prod'}
                                  ],
                                  placeholder="Select one or many aggregations",
                                  multi=True
                              ),
                              html.Div(id='dd-output-container'),
                              dbc.Button("Primary", id="Primary", color="primary", className="mr-1"),
                              ])]


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
    # return "input: {}".format(number)

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
