import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

df = pd.DataFrame({
    "x": [1, 2, 3, 4],
    "y": [1, 2, 3, 4],
})


fig = px.line(df)

cpp_check_layout = [html.Div([html.H3("Welcome to cppCheck !"),
                              dcc.Graph(
                                  figure=fig,
                                  id='welcome-to-cpp-check'
                              )
                              ])]