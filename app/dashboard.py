import dash
import json
import dash_bootstrap_components as dbc
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
    "Precision Score": "Measures how often URLs predicted as phishing were actually phishing, helping assess false positive rates.",
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
                        className="metric",
                        **{"data-target": metrics[metric_name]}
                    ),
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
        # Organizes cards into a row
        dbc.Row(cards)
    ]
)

# Refers to JS file to run animation for each metric
for title, metric in metric_titles.items():
    app.clientside_callback(
        ClientsideFunction(
            namespace="dashboard_animations",
            function_name=f"animate{metric}"
        ),
        Output(generate_id(title), "children"),
        Input("metrics-store", "data")
    )


if __name__ == "__main__":
    app.run(debug=True)
