import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_table
import requests
from app import app
import dash

labels = ["error", "performance", "portability", "style", "warning"]

dummy_data = [
    {"id": 1, "buildName": "test", "error": 10, "performance": 43, "portability": 33, "style": 16, "warning": 55},
    {"id": 2, "buildName": "test2", "error": 13, "performance": 55, "portability": 45, "style": 17, "warning": 55},
    {"id": 3, "buildName": "test3", "error": 23, "performance": 42, "portability": 43, "style": 71, "warning": 39},
    {"id": 4, "buildName": "test4", "error": 43, "performance": 96, "portability": 10, "style": 17, "warning": 19},
    {"id": 5, "buildName": "test5", "error": 45, "performance": 44, "portability": 25, "style": 71, "warning": 49}
]
request_url = "http://localhost:8081/cppcheck"


def fetch_data(request):
    check_request = requests.get(request)
    json_data = check_request.json()
    return json_data


print(fetch_data(request_url))


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
    print(res)
    return res


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
mydata = []
cpp_check_layout = [html.Div([html.H3("Statistics on the latest cppChecks"),
                              dcc.Graph(
                                  figure=fig,
                                  id='welcome-to-cpp-check'
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
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('Primary', "n-clicks")])
def on_button_click(n):
    if n is None:
        return "Pepehands"
    else:
        return f"Clicked {n} times."

# @app.callback(
#     dash.dependencies.Output('dd-output-container', 'children'),
#     [dash.dependencies.Input('aggregations_dropdown', 'value')])
# def update_output(value):
#     return 'You have selected "{}"'.format(value)


