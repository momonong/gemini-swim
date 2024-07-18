from flask import Flask
import dash
from dash import dcc, html

# 创建 Flask 应用
server = Flask(__name__)

# 创建 Dash 应用
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')

# 定义 Dash 应用布局
app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for Python.
    """
        ),
        dcc.Graph(
            id="example-graph",
            figure={
                "data": [
                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "SF"},
                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar", "name": "NYC"},
                ],
                "layout": {"title": "Dash Data Visualization"},
            },
        ),
    ]
)

# 定义 Flask 路由
@server.route('/')
def index():
    return "Hello, this is Flask!"

# 运行应用
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000, debug=True)
