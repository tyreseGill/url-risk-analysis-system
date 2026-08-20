import dash
import json
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "URL Phishing Analytics Dashboard"

performance_metric_container = html.Div(
    id="performance-container",
    children=[]
    )

app.layout = html.Div(
    id="app-container",
    children=[
        html.H1(
            "Model Performance Dashboard",
            id="title"
            ),
        performance_metric_container
    ]
)

dbc_rows = dbc.Row([])

with open("data/model_metrics.json", "r") as f:
    data = json.load(f)
    metrics = [
        'Accuracy Score',
        'Precision Score',
        'Recall Score',
        'F1-Score',
        'Roc-Auc Score'
    ]
    for metric_str in metrics:
        metric_val = f"{data[metric_str]:.2%}"

        metric_card = dbc.Card(
            dbc.CardBody([
                html.H6(
                    metric_str
                ),
                html.H2(className="metric", children=[metric_val]),
            ]),
            color="success",
            inverse=True
        )
        performance_metric_container.children.append(
            metric_card
        )

        dbc_rows.children.append(
            dbc.Col(metric_card)
        )


if __name__ == "__main__":
    app.run(debug=True)
