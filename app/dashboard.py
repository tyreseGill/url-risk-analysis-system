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

metric_cards = []
profile_cards = []

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

# Loads in model metrics on performance
with open("data/model_metrics.json", "r") as file:
    metrics = json.load(file)
    file.close()

# Loads in profile breakdown of typical phishing/legitimate URLs
with open("data/url_profile.json", "r") as file:
    profile = json.load(file)
    file.close()

# Generates KPI card for each metric
for metric_name in metric_titles.keys():
    metric_cards.append(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6(metric_name),
                    html.H2(
                        "0.00%",
                        id=generate_id(metric_name),
                        className="metric"
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

symbol_units = {
    '"@"': "at sign",
    '":"': "colon",
    '","': "comma",
    '"$"': "dollar sign",
    '"."': "dot",
    '"="': "equal sign",
    '"-"': "hyphen",
    '"%"': "percentage",
    '"?"': "question mark",
    '";"': "semicolon",
    '"/"': "slash",
    '"_"': "underscore",
    '"*"': "star",
    '"~"': "tilde",
}

features_using_daily_units = ["Domain Age", "Domain Registration Length"]
features_using_char_units = ["Word Path", "Words Raw", "Hostname Length", "URL Length", "Shortest Word Host", "Shortest Word Path", "Shortest Words Raw", "Longest Word Path"]
features_using_occurences_units = ["Number of \"WWW\"s'", "HTTP in Path", "Number of Redirection", "Number of Subdomains", "Number of \".com\"s'"]

# Adds cards describing analytics of a typical phishing and legit URL
for status in profile:
    characteristics = []

    # Lists a bullet for each feature
    for feature, value in profile[status].items():
        symbol_used = None
        symbol_found = False

        for symbol in symbol_units.keys():
            if symbol in feature:
                symbol_used = symbol
                symbol_found = True
                break
        
        integer_value = int(value)

        # if feature.startswith("") or "Ratio" in feature:
        #     display_value = f"{value:.1%}"
        if symbol_found:
            display_value = f"{integer_value} {symbol_units[symbol_used]}{"s" if integer_value != 1 else ""}"
        elif feature in features_using_daily_units:
            num_years = int(value / 365)
            if num_years == 0:
                display_value = f"{integer_value} days"
            else:
                display_value = f"{num_years} year{"s" if num_years != 1 else ""}"
        elif feature in features_using_char_units:
            display_value = f"{integer_value} character{"s" if integer_value != 1 else ""}"
        elif feature == "Page Rank":
            rank_num = integer_value
            if rank_num == 1:
                display_value = "1st place"
            elif rank_num == 2:
                display_value = "2nd place"
            elif rank_num == 3:
                display_value = "3rd place"
            else:
                display_value = f"{rank_num}th place"
        elif feature == "Web Traffic":
            display_value = f"{integer_value:,} visitor{"s" if integer_value != 1 else ""}"
        elif feature in features_using_occurences_units:
            display_value = f"{integer_value} occurence{"s" if integer_value != 1 else ""}"
        elif feature == "Phish Hints":
            display_value = f"{integer_value} phishing keyword{"s" if integer_value != 1 else ""}"
        elif feature == "Statistical Report":
            display_value = f"{value:.1%} of URLs flagged by statistical report indicator"
        elif feature == "Characters Repeat":
            display_value = f"{integer_value} repeated character{"s" if integer_value != 1 else ""}"
        elif feature == "Number of External CSS":
            display_value = f"{integer_value} external CSS file{"s" if integer_value != 1 else ""}"
        elif feature == "Number of Hyperlinks":
            display_value = f"{integer_value} hyperlink{"s" if integer_value != 1 else ""}"
        # Fallback: Represent as a percentage
        else:
            display_value = f"{value:.1%}"

        characteristics.append(
            html.Li([
                html.Strong(f"{feature}: "),
                html.Span(display_value)
            ])
        )
    
    # Defines HTML Element
    profile_cards.append(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6(f"Typical {status.capitalize()} URL"),
                    html.Ul(characteristics)
                ]),
                color="lightblue" if status == "legitimate" else "salmon",
                className="profile-card"
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
        # Organizes metric cards into a row
        dbc.Row(metric_cards),
        dbc.Row(profile_cards),
        # Container holding bar chart for visualizing top feature importance metrics
        html.Div(
            id="graph-container",
            children=dcc.Graph(
                id="feature-importance-chart",
            ),
        ),
    ]
)


# Feature Importance 
@app.callback(
    Output("feature-importance-chart", "figure"),
    Input("model-dropdown", "value"),
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
