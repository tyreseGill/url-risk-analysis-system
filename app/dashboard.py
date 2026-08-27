import dash
import json
import joblib
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, ClientsideFunction


def generate_id(metric_name: str) -> str:
    """
    Automates creation of an ID for an HTML element based on a metric.
    """
    return f"{metric_name.lower().replace(' ', '-').replace('.', '')}-value"

cards = []

metric_titles = {
    "Accuracy Score": "Accuracy",
    "Precision Score": "Precision",
    "Recall Score": "Recall",
    "F1-Score": "F1",
    "Roc-Auc Score": "RocAuc"
}

metric_descriptions = {
    "Accuracy Score": "Overall percentage of URLs correctly classified as phishing or legitimate.",
    "Precision Score": "Measures how often URLs predicted as phishing were actually phishing.",
    "Recall Score": "Measures how many phishing URLs were successfully identified, highlighting detection coverage.",
    "F1-Score": "Balances precision and recall into a single metric, providing a holistic view of phishing detection performance.",
    "Roc-Auc Score": "Evaluates how effectively the model distinguishes between phishing and legitimate URLs across classification thresholds."
}


app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "URL Phishing Analytics Dashboard"

# Loads in metrics from JSON file
with open("data/model_metrics.json", "r") as f:
    metrics = json.load(f)

# Generates KPI card for each metric
for metric_name in metric_titles.keys():
    cards.append(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6(metric_name),
                    html.H2(
                        "0.00%",
                        id=generate_id(metric_name),
                        className="metric"                    ),
                    html.P(
                        metric_descriptions[metric_name]
                    )
                ]),
                color="success",
                inverse=True,
            )
        )
    )

# Sets up HTML layout to render
app.layout = html.Div(
    id="app-container",
    children=[
        # Stores JSON data in the browser for data sharing
        dcc.Store(
            id="metrics-store",
            data=metrics
        ),
        # Title
        html.H1(
            "Model Performance Dashboard",
            id="title"
        ),
        dcc.Dropdown(
            [ model for model in metrics.keys() ],
            placeholder="Select a model",
            value=max(
                metrics,
                key=lambda model: list(metrics[model].values())[-1]["accuracy"]
            ),
            id="model-dropdown"
        ),
        # Organizes cards into a row
        dbc.Row(cards),
        # Container holding bar chart for visualizing top feature importance metrics
        html.Div(
            id="graph-container",
            children=dcc.Graph(
                id="feature-importance-chart",
                # figure=fig
            ),
        ),
    ]
)

@app.callback(
    Output("feature-importance-chart", "figure"),
    Input("model-dropdown", "value")
)

def update_model_graphs(selected_model):
    last_stage = list(
        metrics[selected_model].keys()
    )[-1]

    path = metrics[selected_model][last_stage]["model_path"]
    model = joblib.load(path)

    # Creates data frame based on the top most important features
    feature_df = (
        pd.DataFrame({
            "Feature": model.feature_names_in_,
            "Importance": model.feature_importances_
        })
        .sort_values("Importance", ascending=False)
        .head(15)
    )

    # Creates bar chart showing feature importance
    fig = px.bar(
        feature_df,
        x="Importance",
        y="Feature",
        title=f"Top {min(len(model.feature_names_in_), 15)} Most Important Features",
        color="Importance",
        color_continuous_scale="Viridis"
    )

    # Adds spacing between tick labels along y-axis and bar chart
    fig.update_yaxes(
        ticklabelstandoff=20
    )

    return fig

# Refers to JS file to run animation for each metric
for title, metric in metric_titles.items():
    app.clientside_callback(
        ClientsideFunction(
            namespace="dashboard_animations",
            function_name=f"animate{metric}"
        ),
        Output(generate_id(title), "children"),
        Input("metrics-store", "data"),
        Input("model-dropdown", "value")
    )


if __name__ == "__main__":
    app.run(debug=True)
