import pandas as pd
import plotly.express as px


def create_figures(json_data):
    # 将 JSON 数据转换为 DataFrame
    df = pd.DataFrame(json_data)

    scatter_fig = px.scatter(
        df, x="event_number", y="grade", color="gender", hover_data=["name"]
    )

    bar_fig = px.bar(
        df, x="event_number", y="grade", color="gender", hover_data=["name"]
    )

    line_fig = px.line(
        df, x="event_number", y="grade", color="gender", hover_data=["name"]
    )

    return scatter_fig, bar_fig, line_fig
