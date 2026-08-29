import dash
import json
import joblib
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, ClientsideFunction
from utils.statistical_profiling import generate_boolean_feature_title, generate_numeric_feature_title, categorize_features, generate_profiles


metric_titles = {
    "Accuracy Score": "Accuracy",
    "Precision Score": "Precision",
    "Recall Score": "Recall",
    "F1-Score": "F1",
    "Roc-Auc Score": "RocAuc"
}

symbol_units = {
    '"@"': "at sign",
    '":"': "colon",
    '","': "comma",
    '"$"': "dollar sign",
    '"."': "dot",
    '"="': "equal sign",
    '"-"': "hyphen",
    '"%"': "percentage sign",
    '"?"': "question mark",
    '";"': "semicolon",
    '"/"': "slash",
    '"_"': "underscore",
    '"*"': "star",
    '"~"': "tilde",
}


def generate_id(metric_name: str) -> str:
    """
    Automates creation of an ID for an HTML element based on a metric.

    Args:
        metric_name: The name of a metric from which a unique ID name will be generated.
    
    Returns:
        str: A string representative of a unique ID.
    """
    return f"{metric_name.lower().replace(' ', '-').replace('.', '')}-value"


def generate_frequency_string(decimal_value: float) -> str:
    """
    Creates a string describing the frequency of a boolean feature.

    Args:
        decimal_value: A float value that may be in percentile or non-percentile form.

    Returns:
        str: Text indicating how frequent a boolean characteristic occurs.
    """
    percentile_value = (
        round(decimal_value, 1) 
        if 1 <= decimal_value <= 100 
        else round(decimal_value * 100, 1)
    )

    if 0 <= percentile_value <= 5:
        frequency_str = "Very uncommon"
    elif percentile_value <= 25:
        frequency_str = "Uncommon"
    elif percentile_value <= 50:
        frequency_str = "Moderately common"
    elif percentile_value <= 75:
        frequency_str = "Common"
    elif percentile_value <= 90:
        frequency_str = "Very common"
    else:
        frequency_str = "Nearly universal" 

    display_value = (
        f"{frequency_str} ({decimal_value:.1f}%)" 
        if 1 <= decimal_value <= 100 
        else f"{frequency_str} ({decimal_value:.1%})"
    )

    return display_value


def generate_data_metric(feature_name: str) -> str:
    """
    Generates a useable data-metric attribute based on feature name.

    Args:
        feature_name: The name of the feature from which a unique attribute 
        name will be generated from.
    
    Returns:
        str: A safe string to be used for "data-metric" attribute.
    """
    metric_name = feature_name.lower().replace(" ", "-")

    # Removes any symbols explicitly mentioned in symbol_units dictionary
    for symbol in symbol_units:
        metric_name = metric_name.replace(symbol, symbol_units[symbol])

    metric_name = feature_name.replace("\"", "")

    return metric_name


def load_json_data() -> (dict, dict):
    """
    Loads dictionaries from JSON files representing model performance metrics 
    and URL profile statistics.
    
    Returns:
        tuple: Consists of two dictionaries representing metrics and profile stats.
    """
    # Loads in model metrics on performance
    with open("data/model_metrics.json", "r") as file:
        metrics = json.load(file)
        file.close()

    # Loads in profile breakdown of typical phishing/legitimate URLs
    with open("data/url_profile.json", "r") as file:
        profile = json.load(file)
        file.close()
    
    return metrics, profile


def build_metric_cards() -> list:
    """
    Creates HTML cards describing predictive analytics of the selected machine learning model.

    Returns:
        list: Cards displaying a unique performance metric for a given machine learning model.
    """
    metric_cards = []

    metric_descriptions = {
        "Accuracy Score": "Overall percentage of URLs correctly classified as phishing or legitimate.",
        "Precision Score": "Measures how often URLs predicted as phishing were actually phishing.",
        "Recall Score": "Measures how many phishing URLs were successfully identified, highlighting detection coverage.",
        "F1-Score": "Balances precision and recall into a single metric, providing a holistic view of phishing detection performance.",
        "Roc-Auc Score": "Evaluates how effectively the model distinguishes between phishing and legitimate URLs across classification thresholds."
    }

    for metric_name in metric_titles.keys():
        # Defines HTML composition of new Metric Card
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

    return metric_cards


def build_profile_cards(profile: dict) -> list:
    """
    Creates HTML cards describing analytics of a typical phishing and legit URL.

    Args:
        profile: Dictionary storing quantitative info on key features of a typical URL profile.

    Returns:
        list: Cards displaying profile characteristics of typical phishing and legitimate URLs.
    """
    profile_cards = []

    FEATURES_USING_DAILY_UNITS = ["Domain Age", "Domain Registration Length"]
    FEATURES_USING_CHAR_UNITS = ["Word Path", "Words Raw", "Hostname Length", "URL Length", "Shortest Word Host", "Shortest Word Path", "Shortest Words Raw", "Longest Word Path"]
    FEATURES_USING_OCCURENCES_UNITS = ["Number of \"WWW\"s'", "HTTP in Path", "Number of Redirections", "Number of Subdomains", "Number of \".com\"s'"]

    # Runs for Phishing and Legitimate Profile
    for status in profile:
        list_of_feature_measurements = []

        # Generates a bullet for across feature for each profile
        for feature, decimal_value in profile[status].items():
            symbol_used: str = None
            INTEGER_VALUE = int(decimal_value)

            # Parses feature title for symbols with an associated unit
            for symbol in symbol_units.keys():
                if symbol in feature:
                    symbol_used = symbol
                    break
            
            # Formulates a description of the measurements for a given feature
            
            # Provides measurement description 
            if symbol_used:
                display_value = (
                    f"{INTEGER_VALUE} {symbol_units[symbol_used]}{"s" if INTEGER_VALUE != 1 else ""}"
                )
            # Features using days as a measurement
            elif feature in FEATURES_USING_DAILY_UNITS:
                NUM_YEARS = int(decimal_value / 365)
                if NUM_YEARS == 0:
                    display_value = f"{INTEGER_VALUE} days"
                else:
                    display_value = f"{NUM_YEARS} year{"s" if NUM_YEARS != 1 else ""}"
            # Features using characters as a measurement
            elif feature in FEATURES_USING_CHAR_UNITS:
                display_value = f"{INTEGER_VALUE} character{"s" if INTEGER_VALUE != 1 else ""}"
            # Features using ranking as a measurement
            elif feature == "Page Rank":
                rank_num: int = INTEGER_VALUE
                if rank_num == 1:
                    display_value = "1st place"
                elif rank_num == 2:
                    display_value = "2nd place"
                elif rank_num == 3:
                    display_value = "3rd place"
                else:
                    display_value = f"{rank_num}th place"
            # Features using visitors as a measurement
            elif feature == "Web Traffic":
                display_value = f"{INTEGER_VALUE:,} visitor{"s" if INTEGER_VALUE != 1 else ""}"
            # Features using generic "occurences" as a measurement
            elif feature in FEATURES_USING_OCCURENCES_UNITS:
                display_value = f"{INTEGER_VALUE} occurence{"s" if INTEGER_VALUE != 1 else ""}"
            # Features using keywords as a measurement
            elif feature == "Number of Phish Hints":
                display_value = f"{INTEGER_VALUE} phishing keyword{"s" if INTEGER_VALUE != 1 else ""}"
            # Features using repeated characters as a measurement
            elif feature == "Characters Repeat":
                display_value = f"{INTEGER_VALUE} repeated character{"s" if INTEGER_VALUE != 1 else ""}"
            # Features using external CSS as a measurement
            elif feature == "Number of External CSS":
                display_value = f"{INTEGER_VALUE} external CSS file{"s" if INTEGER_VALUE != 1 else ""}"
            # Features using hyperlinks as a measurement
            elif feature == "Number of Hyperlinks":
                display_value = f"{INTEGER_VALUE} hyperlink{"s" if INTEGER_VALUE != 1 else ""}"
            # Features representative of a percentage value
            else:
                if "Percentage" in feature:
                    display_value = (
                        f"{decimal_value:.1f}%" 
                        if 1 <= decimal_value <= 100 
                        else f"{decimal_value:.1%}"
                    )
                else:
                    display_value = generate_frequency_string(decimal_value)

            # Adds new HTML bullet to list of bulletpoints
            list_of_feature_measurements.append(
                html.Li([
                    html.Strong(f"{feature}: "),
                    html.Span(display_value)
                ],
                # Uniquely identifies a characteristic to be highlighted
                **{"data-metric": generate_data_metric(feature)}
                )
            )
        
        # Defines HTML composition of new Profile Card
        profile_cards.append(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H6(f"{status.capitalize()} URL Profile"),
                        html.Ul(list_of_feature_measurements)
                    ]),
                    color=(
                        "lightblue" 
                        if status == "legitimate" 
                        else "salmon"
                    ),
                    className="profile-card",
                    id=(
                        "phishing-url-profile-card" 
                        if status == "phishing" 
                        else "legitimate-url-profile-card"
                    )
                )
            )
        )
    
    return profile_cards


def build_app(metrics: dict, profile: dict, metric_cards: list, profile_cards: list) -> dash.Dash:
    """
    Constructs the HTML layout.

    Args:
        metrics: Dictionary containing the metric information for a given machine learning model.
        metric_cards: HTML Cards to represent metric information.
        profile_cards: HTML Cards to represent a URL profile.
    
    Returns:
        dash.Dash: The Dash constructor intializing the application.
    """
    app = dash.Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    app.title = "URL Phishing Analytics Dashboard"

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
            # Organizes profile cards into a row
            dbc.Row(profile_cards),
            # Visualizes difference between Phishing URL Profile and a Legitimate URL Profile
            html.Div(
                id="radar-chart-container",
                children=dcc.Graph(
                    id="profile-radar-chart",
                ),
                style={"margin": "20px auto", "width": "60%"}
            ),
            # Visualizes top feature importance metrics
            html.Div(
                id="graph-container",
                children=dcc.Graph(
                    id="feature-importance-chart",
                ),
                style={"margin": "20px auto", "width": "90%"}
            ),
        ]
    )

    # Updates model graphs in response to the user selecting a model from dropdown
    @app.callback(
        Output("feature-importance-chart", "figure"),
        Output("profile-radar-chart", "figure"),
        Input("model-dropdown", "value"),
    )

    def update_model_graphs(selected_model: str) -> "plotly.Figure":
        """
        Updates any graphics associated with the selected model.

        Args:
            selected_model: The name of the model selected from dropdown.
        
        Returns:
            plotly.Figure: The graphic to be updated onscreen.
        """
        model_features = []
        last_stage = list(metrics[selected_model].keys())[-1]
        path = metrics[selected_model][last_stage]["model_path"]
        model = joblib.load(path)

        # Creates data frame consisting of the columns the model trained on
        data_frame = pd.read_parquet("data/Training.parquet")
        data_frame = data_frame[
            list(model.feature_names_in_) + ["status"]
        ]

        boolean_features, numeric_features = categorize_features(data_frame)

        phishing_profile_values = []
        legitimate_profile_values = []

        # Renames tick labels for each feature to be more readable
        for feature_name in model.feature_names_in_:

            if feature_name in boolean_features:
                model_features.append(
                    generate_boolean_feature_title(feature_name)
                )
            elif feature_name in numeric_features:
                model_features.append(
                    generate_numeric_feature_title(feature_name)
                )
            else:
                raise Exception(f"The feature \"{feature_name}\" could not be categorized as neither a boolean nor as numeric.")

        # Creates data frame based on the top most important features
        feature_df = (
            pd.DataFrame({
                "Feature": model_features,
                "Importance": model.feature_importances_
            })
            .sort_values("Importance", ascending=False)
            .head(15)
        )

        feature_df_2 = (
            pd.DataFrame({
                "Feature": model_features,
                "Importance": model.feature_importances_
            })
            .sort_values("Importance", ascending=False)
            .head(5)
        )

        top_features = feature_df_2["Feature"].tolist()

        phishing_normalized = []
        legitimate_normalized = []

        for feature in top_features:
            p = profile["phishing"][feature]
            l = profile["legitimate"][feature]

            max_val = max(p, l)

            phishing_normalized.append(p / max_val if max_val else 0)
            legitimate_normalized.append(l / max_val if max_val else 0)

        # Creates bar chart showing feature importance
        feature_importance_graph = px.bar(
            feature_df,
            x="Importance",
            y="Feature",
            title=f"Top {min(len(model.feature_names_in_), 15)} Most Important Features",
            color="Importance",
            color_continuous_scale="Viridis"
        )

        feature_importance_graph.update_layout(
            title_x=0.5
        )

        # Adds spacing between tick labels along y-axis and bar chart
        feature_importance_graph.update_yaxes(
            ticklabelstandoff=20
        )


        radar_chart = go.Figure()

        radar_chart.add_trace(go.Scatterpolar(
            r=phishing_normalized,
            theta=top_features,
            fill="toself",
            line=dict(color="red"),
            name="Phishing"
        ))

        radar_chart.add_trace(go.Scatterpolar(
            r=legitimate_normalized,
            theta=top_features,
            fill="toself",
            line=dict(color="blue"),
            name="Legitimate"
        ))

        radar_chart.update_layout(
            title="Profile Comparison w/ Top 5 Most Important Features",
            title_x=0.5,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                ),
                angularaxis=dict(
                    tickfont=dict(size=14)
                )
            ),
            showlegend=True
        )

        return feature_importance_graph, radar_chart

    
    # Updates profile cards in response to the user selecting a model from dropdown
    @app.callback(
        Output("phishing-url-profile-card", "children"),
        Output("legitimate-url-profile-card", "children"),
        Input("model-dropdown", "value")
    )

    def update_profile_cards(selected_model: str) -> tuple:
        """
        Updates any profile cards associated with the selected model.

        Args:
            selected_model: The name of the model selected from dropdown.
        
        Returns:
            tuple: Updated phishing and legitimate profile card contents.
        """
        model_features = []
        last_stage = list(metrics[selected_model].keys())[-1]
        path = metrics[selected_model][last_stage]["model_path"]
        model = joblib.load(path)

        # Creates data frame consisting of the columns the model trained on
        data_frame = pd.read_parquet("data/Training.parquet")
        data_frame = data_frame[
            list(model.feature_names_in_) + ["status"]
        ]

        feature_df = data_frame.drop(columns=["status"])

        boolean_features, numeric_features = categorize_features(feature_df)

        # Renames tick labels for each feature to be more readable
        for feature_name in model.feature_names_in_:
            if feature_name in boolean_features:
                model_features.append(
                    generate_boolean_feature_title(feature_name)
                )
            elif feature_name in numeric_features:
                model_features.append(
                    generate_numeric_feature_title(feature_name)
                )
            else:
                raise Exception(f"The feature \"{feature_name}\" could not be categorized as neither a boolean nor as numeric.")
        
        profile = generate_profiles(data_frame, numeric_features, boolean_features)

        phishing_card, legitimate_card = build_profile_cards(profile)

        return phishing_card, legitimate_card


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

    return app


def main():
    metrics, profile = load_json_data()
    metric_cards = build_metric_cards()
    profile_cards = build_profile_cards(profile)
    app = build_app(metrics, profile, metric_cards, profile_cards)
    app.run(debug=True)


if __name__ == "__main__":
    main()
