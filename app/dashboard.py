import dash
import json
import joblib
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.base import BaseEstimator
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


def extract_model(model_name: str, metrics: dict) -> BaseEstimator:
    """
    Extracts the trained machine learning model based on the selected model name.

    Args:
        model_name: The name of the model selected from dropdown.
        metrics: Dictionary containing the metric information for a given machine learning model.

    Returns:
        BaseEstimator: The trained machine learning model.
    """
    last_stage = list(metrics[model_name].keys())[-1]
    path = metrics[model_name][last_stage]["model_path"]
    model = joblib.load(path)
    return model


def extract_data_frame(model: BaseEstimator) -> pd.DataFrame:
    """
    Extracts the data frame containing the features and their associated importance values.

    Args:
        model: The trained machine learning model.

    Returns:
        pd.DataFrame: The extracted data frame.
    """
    data_frame = pd.read_parquet("data/Training.parquet")
    data_frame = data_frame[
        list(model.feature_names_in_) + ["status"]
    ]
    return data_frame


def extract_model_and_data_frame(selected_model: str, metrics: dict) -> tuple[BaseEstimator, pd.DataFrame]:
    """
    Extracts model and data frame based on the selected model from dropdown.

    Args:
        selected_model: The name of the model selected from dropdown.
        metrics: Dictionary containing the metric information for a given machine learning model.

    Returns:
        tuple: Consists of the trained machine learning model and the extracted data frame.
    """
    model = extract_model(selected_model, metrics)
    data_frame = extract_data_frame(model)
    return model, data_frame


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
    # Converts decimal value to percentile value if it is not already in percentile form
    percentile_value = (
        round(decimal_value, 1) 
        if 1 <= decimal_value <= 100 
        else round(decimal_value * 100, 1)
    )

    # Categorizes the frequency of a boolean feature based on its percentile value
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

    # Formats the display value to be shown on the profile card
    display_value = (
        f"{frequency_str} ({decimal_value:.1f}%)" 
        if 1 <= decimal_value <= 100 
        else f"{frequency_str} ({decimal_value:.1%})"
    )

    return display_value


def format_count(value: float, singular: str, plural: str | None = None, *, use_commas: bool = False) -> str:
    """
    Return a count string with correct singular/plural form.

    Args:
        value: The numeric value to be formatted.
        singular: The singular form of the noun.
        plural: The plural form of the noun. If None, 's' will be appended to the singular form.
        use_commas: Whether to format the number with commas.

    Returns:
        str: A formatted string representing the count and the appropriate noun form.
    """
    plural = plural or f"{singular}s"
    count = int(value)
    noun = singular if count == 1 else plural
    prefix = f"{count:,}" if use_commas else str(count)
    return f"{prefix} {noun}"


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


def generate_correlation_matrix(data_frame: pd.DataFrame, threshold: float=0.5) -> "plotly.Figure":
    """
    Generates a correlation matrix heatmap for the given data frame.

    Args:
        data_frame: The data frame for which to generate the correlation matrix.
        threshold: The minimum correlation value to display.

    Returns:
        plotly.Figure: The generated correlation matrix heatmap.
    """
    correlation_matrix = data_frame.corr(numeric_only=True)
    boolean_features, numeric_features = categorize_features(data_frame)
    num_features = len(correlation_matrix)

    fig = px.imshow(
        correlation_matrix,
        color_continuous_scale="RdBu_r",
        text_auto=".2f",
        aspect="auto",
        height=max(600, num_features * 20),
    )

    fig.update_layout(
        title="Correlation Matrix",
        title_x=0.5,
        height=max(600, num_features * 20),
        autosize=True
    )

    # Adds spacing between tick labels along y-axis and bar chart
    fig.update_yaxes(
        ticklabelstandoff=20
    )

    return fig


def generate_title(feature_name: str, boolean_features: list, numeric_features: list) -> str:
    """
    Generates a more readable title for a feature based on its type.

    Args:
        feature_name: The name of the feature to be renamed.
        boolean_features: List of boolean features.
        numeric_features: List of numeric features.

    Returns:
        str: A more readable title for the feature.
    """
    if feature_name in boolean_features:
        return generate_boolean_feature_title(feature_name)
    elif feature_name in numeric_features:
        return generate_numeric_feature_title(feature_name)
    else:
        raise Exception(f"The feature \"{feature_name}\" could not be categorized as neither a boolean nor as numeric.")


def load_json_data() -> tuple[dict, dict]:
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


def build_profile_cards(profile: dict, feature_order: list = None, build_cards: bool = True) -> list:
    """
    Creates HTML cards describing analytics of a typical phishing and legit URL.

    Args:
        profile: Dictionary storing quantitative info on key features of a typical URL profile.
        feature_order: The list of features to be displayed (sorted in order of most to 
            least important).
        build_cards: Flag that determines whether to create profile cards from scratch or 
            rewrite the profile details for an existing card.

    Returns:
        list: HTML Cards or HTML Li elements displaying profile characteristics.
    """
    profile_cards = []
    profile_measurement_lists = []

    FEATURES_USING_DAILY_UNITS = ["Domain Age", "Domain Registration Length"]
    FEATURES_USING_CHAR_UNITS = ["Word Path", "Words Raw", "Hostname Length", "URL Length", "Shortest Word Host", "Shortest Word Path", "Shortest Words Raw", "Longest Word Path"]
    FEATURES_USING_OCCURENCES_UNITS = ["Number of \"WWW\"s'", "HTTP in Path", "Number of Redirections", "Number of Subdomains", "Number of \".com\"s'"]

    # Runs for Phishing and Legitimate Profile
    for status in profile:
        feature_measurements = []

        features = (
            feature_order
            if feature_order is not None
            else profile[status].keys()
        )

        # Generates a bullet for across feature for each profile
        for feature in features:
            if feature not in profile[status]:
                continue

            symbol_used: str = None

            decimal_value = profile[status][feature]
            INTEGER_VALUE = int(decimal_value)

            # Parses feature title for symbols with an associated unit
            for symbol in symbol_units.keys():
                if symbol in feature:
                    symbol_used = symbol
                    break
            
            # Features using symbols as a measurement
            if symbol_used:
                singular = symbol_units[symbol_used]
                plural = f"{singular}s"
                display_value = format_count(INTEGER_VALUE, singular, plural)
            # Features using days as a measurement
            elif feature in FEATURES_USING_DAILY_UNITS:
                num_years = int(decimal_value / 365)
                if num_years == 0:
                    display_value = format_count(INTEGER_VALUE, "day", "days")
                else:
                    display_value = format_count(num_years, "year", "years")
            # Features using characters as a measurement
            elif feature in FEATURES_USING_CHAR_UNITS:
                display_value = format_count(INTEGER_VALUE, "character", "characters")
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
                display_value = format_count(INTEGER_VALUE, "visitor", "visitors", use_commas=True)
            # Features using generic "occurences" as a measurement
            elif feature in FEATURES_USING_OCCURENCES_UNITS:
                display_value = format_count(INTEGER_VALUE, "occurence", "occurences")
            # Features using keywords as a measurement
            elif feature == "Number of Phish Hints":
                display_value = format_count(INTEGER_VALUE, "phishing keyword", "phishing keywords")
            # Features using repeated characters as a measurement
            elif feature == "Characters Repeat":
                display_value = format_count(INTEGER_VALUE, "repeated character", "repeated characters")
            # Features using external CSS as a measurement
            elif feature == "Number of External CSS":
                display_value = format_count(INTEGER_VALUE, "external CSS file", "external CSS files")
            # Features using hyperlinks as a measurement
            elif feature == "Number of Hyperlinks":
                display_value = format_count(INTEGER_VALUE, "hyperlink", "hyperlinks")
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
            feature_measurements.append(
                html.Li([
                    html.Strong(f"{feature}: "),
                    html.Span(display_value)
                ],
                # Uniquely identifies a characteristic to be highlighted
                **{"data-metric": generate_data_metric(feature)}
                )
            )

        # Creates cards from scratch
        if build_cards:
            # Defines HTML composition of new Profile Card
            profile_cards.append(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H6(f"{status.capitalize()} URL Profile"),
                            html.Ul(
                                feature_measurements,
                                id=f"ul-{status}-url-profile-card"
                            )
                        ]),
                        color=(
                            "lightblue" 
                            if status == "legitimate" 
                            else "salmon"
                        ),
                        className="profile-card",
                        id=f"{status}-url-profile-card"
                    )
                )
            )
        # Cards have already been initialized
        else:
            profile_measurement_lists.append(feature_measurements)
    
    # Returns entire HTML cards when application initially runs
    if build_cards:
        return profile_cards
    # Otherwise, returns just the list elements to prevent duplication and curb processing
    else:
        return profile_measurement_lists


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
            # Visualizes top feature importance metrics
            html.Div(
                id="graph-container",
                children=dcc.Graph(
                    id="feature-importance-chart",
                ),
                style={"margin": "20px auto", "width": "90%"}
            ),
            # Organizes profile cards into a row
            dbc.Row(profile_cards),
            # Visualizes difference between Phishing URL Profile and a Legitimate URL Profile
            html.Div(
                id="radar-chart-container",
                children=dcc.Graph(
                    id="profile-radar-chart",
                ),
                style={"margin": "20px auto", "width": "70%"}
            ),
            # Additional graph to visualize correlation matrix of features
            dcc.Graph(
                id="correlation-matrix",
                style={
                    "width": "90vw",
                    "height": "90vh"
                }
            )
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
        phishing_profile_values = []
        legitimate_profile_values = []

        model, data_frame = extract_model_and_data_frame(selected_model, metrics)
        boolean_features, numeric_features = categorize_features(data_frame)

        # Renames tick labels for each feature to be more readable
        for feature_name in model.feature_names_in_:
            model_features.append(
                generate_title(feature_name, boolean_features, numeric_features)
            )

        # Creates data frame that sorts features based on importance
        feature_df = (
            pd.DataFrame({
                "Feature": model_features,
                "Importance": model.feature_importances_
            })
            .sort_values("Importance", ascending=False)
        )

        def get_top_features(feature_df: pd.DataFrame, num_features: int) -> list:
            """
            Obtains list of most important features based on how influential each 
            feature is in helping a predictive model make a prediction.

            Args:
                feature_df: The data frame containing the features and their associated importance values.
                num_features: The number of features to be returned based on importance.

            Returns:
                list: The top most important features based on the number of features requested.
            """
            # Creates data frame based on the top most important features
            feature_df = (
                pd.DataFrame({
                    "Feature": model_features,
                    "Importance": model.feature_importances_
                })
                .sort_values("Importance", ascending=False)
            )

            # Determines the threshold for feature importance based on the number of features requested
            avg_feature_importance_threshold = 1 / len(feature_df)

            # Obtains the list of features that meet the threshold for importance
            top_features = feature_df.loc[
                feature_df["Importance"] >= avg_feature_importance_threshold,
                "Feature"
            ].tolist()

            # Ensures that the number of features returned is at least 3 and at most the number of features requested
            if len(top_features) < 3:
                top_features = feature_df.head(3)["Feature"].tolist()
            elif len(top_features) > num_features:
                top_features = feature_df.head(num_features)["Feature"].tolist()

            return top_features

        # Obtains top most important features
        top_features = get_top_features(feature_df, 5)

        def normalize_features(features: list) -> tuple[list, list]:
            """
            Normalizes the values of each feature to be displayed in a radar chart.

            Args:
                features: The list of features to be normalized.
            
            Returns:
                tuple[list, list]: Two lists containing the normalized values for phishing and legitimate features, respectively.
            """
            phishing_normalized = []
            legitimate_normalized = []

            # Normalizes each feature to be displayed in radar chart
            for feature in top_features:
                # Obtains the phishing and legitimate values for each feature
                p = profile["phishing"][feature]
                l = profile["legitimate"][feature]

                max_val = max(p, l)

                # Normalizes the values for each feature to be displayed in radar chart
                phishing_normalized.append(
                    p / max_val 
                    if max_val 
                    else 0
                )
                legitimate_normalized.append(
                    l / max_val 
                    if max_val 
                    else 0
                )
            
            return phishing_normalized, legitimate_normalized

        phishing_normalized, legitimate_normalized = normalize_features(top_features)

        # Creates bar chart showing feature importance
        feature_importance_graph = px.bar(
            feature_df.head(15),
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
            title="URL Profile Comparison by Top Features",
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
        Output("ul-phishing-url-profile-card", "children"),
        Output("ul-legitimate-url-profile-card", "children"),
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

        model, data_frame = extract_model_and_data_frame(selected_model, metrics)
        feature_df = data_frame.drop(columns=["status"])
        boolean_features, numeric_features = categorize_features(feature_df)

        # Generates a more readable title for each feature based on its type
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

        # Sorts dataframe features based on importance
        importance_df = (
            pd.DataFrame({
                "Feature": model_features,
                "Importance": model.feature_importances_
            })
            .sort_values("Importance", ascending=False)
        )

        # Obtains list of features ordered by importance
        feature_order = importance_df["Feature"].tolist()

        phishing_measurements, legitimate_measurements = build_profile_cards(
            profile,
            feature_order,
            build_cards=False
        )

        return phishing_measurements, legitimate_measurements


    @app.callback(
        Output("correlation-matrix", "figure"),
        Input("model-dropdown", "value")
    )


    def update_correlation_matrix(selected_model: str) -> "plotly.Figure":
        """
        Updates the correlation matrix based on the selected model.

        Args:
            selected_model: The name of the model selected from dropdown.

        Returns:
            plotly.Figure: The updated correlation matrix to be displayed onscreen.
        """
        model = extract_model(selected_model, metrics)
        data_frame = extract_data_frame(model)
        boolean_features, numeric_features = categorize_features(data_frame)

        # Renames tick labels for each feature to be more readable
        for feature_name in model.feature_names_in_:
            data_frame.rename(
                columns={
                    feature_name: generate_title(feature_name, boolean_features, numeric_features)
                },
                inplace=True
            )

        return generate_correlation_matrix(data_frame)


    # Animates metric values in response to the user selecting a model from dropdown
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
