from flask import Flask
import dash
from dash import dcc, html
import pandas as pd
from database import fetch_data_from_db, connect_to_db, disconnect_from_db
import asyncio
from flask_caching import Cache
from visualization import create_figures

# 创建 Flask 应用
server = Flask(__name__)

# 配置缓存
cache = Cache(server, config={"CACHE_TYPE": "simple"})

# 创建 Dash 应用
app = dash.Dash(__name__, server=server, url_base_pathname="/dash/")


# 从数据库中提取数据并缓存
@cache.cached(timeout=60, key_prefix="all_swim_data")
def get_data_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_data())


async def get_data():
    await connect_to_db()
    query = "SELECT * FROM swim_competitions WHERE gender = '女生' LIMIT 100"  # 根据需要修改查询语句
    json_data = await fetch_data_from_db(query)
    await disconnect_from_db()
    return json_data


# 获取数据并创建图表
json_data = get_data_sync()
df = pd.DataFrame(json_data)

# 创建图表
scatter_fig, bar_fig, line_fig = create_figures(json_data)

# 定义 Dash 应用布局
app.layout = html.Div(
    children=[
        html.H1(children="Swimming Competition Dashboard"),
        # 数据过滤控件
        html.Div(
            [
                html.Label("Select Gender"),
                dcc.Dropdown(
                    id="gender-dropdown",
                    options=[{"label": i, "value": i} for i in df["gender"].unique()],
                    value="女生",
                ),
            ]
        ),
        dcc.Graph(id="scatter-graph", figure=scatter_fig),
        dcc.Graph(id="bar-graph", figure=bar_fig),
        dcc.Graph(id="line-graph", figure=line_fig),
    ]
)


# 更新图表的回调
@app.callback(
    [
        dash.dependencies.Output("scatter-graph", "figure"),
        dash.dependencies.Output("bar-graph", "figure"),
        dash.dependencies.Output("line-graph", "figure"),
    ],
    [dash.dependencies.Input("gender-dropdown", "value")],
)
def update_graph(selected_gender):
    filtered_df = df[df["gender"] == selected_gender]
    scatter_fig, bar_fig, line_fig = create_figures(
        filtered_df.to_dict(orient="records")
    )
    return scatter_fig, bar_fig, line_fig


# 定义 Flask 路由
@server.route("/")
def index():
    return "Hello, this is Flask!"


# 运行应用
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000, debug=True)
