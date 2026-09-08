import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math
from sklearn.ensemble import RandomForestClassifier
from utils.notebook_utils import generate_sub_data_frame, test_model, save_stage_metrics, get_relevant_features
from utils.animations import load_bar, show_popup_message


def get_relevant_structural_features() -> pd.DataFrame:
    """
    Retrieves relevant structural features from the dataset by combining various feature categories and filtering out constant features.

    Returns:
        pd.DataFrame: A data frame containing the relevant structural features.
    """   
    from utils.feature_categories import URL_LENGTH_FEATURES, URL_NUMERIC_FEATURES, URL_STRUCTURAL_FEATURES, URL_BEHAVIOR_FEATURES, WORD_STATS, DOMAIN_AND_SUBDOMAIN_FEATURES

    # Combines all URL-structural features into a single set
    ALL_URL_FEATURES = URL_LENGTH_FEATURES | URL_NUMERIC_FEATURES | URL_STRUCTURAL_FEATURES | URL_BEHAVIOR_FEATURES | WORD_STATS | DOMAIN_AND_SUBDOMAIN_FEATURES
    
    # Base data frame
    data_frame = generate_sub_data_frame(
        ALL_URL_FEATURES
    )
    
    # Get relevant features
    STRUCTURAL_URL_FEATURES = get_relevant_features(data_frame)
    
    # Regenerates data frame with relevant features
    data_frame = generate_sub_data_frame(
        STRUCTURAL_URL_FEATURES
    )
    
    return data_frame


def get_relevant_whois_features() -> pd.DataFrame:
    """
    Retrieves relevant WHOIS features from the dataset by filtering out constant features.

    Returns:
        pd.DataFrame: A data frame containing the relevant WHOIS features.
    """
    from utils.feature_categories import WHOIS_FEATURES

    data_frame = generate_sub_data_frame(
        WHOIS_FEATURES
    )

    # Get relevant features
    WHOIS_FEATURES = get_relevant_features(data_frame)

    # Regenerates data frame with relevant features
    data_frame = generate_sub_data_frame(
        WHOIS_FEATURES
    )

    return data_frame


def get_relevant_reputational_features() -> pd.DataFrame:
    """
    Retrieves relevant reputational features from the dataset by filtering out constant features.

    Returns:
        pd.DataFrame: A data frame containing the relevant reputational features.
    """
    from utils.feature_categories import REPUTATIONAL_FEATURES

    # Base data frame
    data_frame = generate_sub_data_frame(
        REPUTATIONAL_FEATURES
    )

    # Get relevant features
    REPUTATIONAL_FEATURES = get_relevant_features(data_frame)

    # Regenerates data frame with relevant features
    data_frame = generate_sub_data_frame(
        REPUTATIONAL_FEATURES
    )

    return data_frame


def get_relevant_webpage_features() -> pd.DataFrame:
    """
    Retrieves relevant webpage features from the dataset by combining various feature categories and filtering out constant features.

    Returns:
        pd.DataFrame: A data frame containing the relevant webpage features.
    """
    from utils.feature_categories import HTML_FEATURES, MEDIA_FEATURES, JAVASCRIPT_FEATURES, CONTENT_METADATA_FEATURES

    # Combines all webpage-related features into a single set
    WEBPAGE_FEATURES = HTML_FEATURES | MEDIA_FEATURES | JAVASCRIPT_FEATURES | CONTENT_METADATA_FEATURES

    # Base data frame
    data_frame = generate_sub_data_frame(
        WEBPAGE_FEATURES
    )

    # Removes all features that are constant
    CONSTANT_FEATURES = data_frame.loc[:, (data_frame.nunique() == 1)].columns
    WEBPAGE_FEATURES.difference_update(CONSTANT_FEATURES)

    # Regenerates data frame with relevant features
    data_frame = generate_sub_data_frame(
        WEBPAGE_FEATURES
    )

    return data_frame


def create_random_forest_model(model_title: str, data_frame: pd.DataFrame, file_name_suffix: str, stage_name: str):
    """
    Creates and tests a random forest model using the provided data frame and saves the model and metrics.

    Args:
        model_title (str): The title of the model.
        data_frame (pd.DataFrame): The data frame containing the features and target variable.
        file_name_suffix (str): The suffix to be used for the model file name.
        stage_name (str): The name of the stage for saving metrics.
    """
    MODEL_TITLE = f"Random Forest ({model_title})"
    MODEL_FILE_NAME = f"random_forest_{file_name_suffix}"
    
    random_forest = RandomForestClassifier(random_state=41)
    test_model(random_forest, MODEL_FILE_NAME, data_frame)

    save_stage_metrics(
        MODEL_TITLE,
        stage_name,
        MODEL_FILE_NAME,
        set(data_frame.columns),
        random_forest
    )

# Structural URL Model
def main():
    model_data = {
        "Structural URL Model": {
            "data_frame": get_relevant_structural_features(),
            "stage_name": "Used Structural URL Features",
            "suffix": "struct",
        },
        "WHOIS Model": {
            "data_frame": get_relevant_whois_features(),
            "stage_name": "Used WHOIS Features",
            "suffix": "whois",
        },
        "Reputational Model": {
            "data_frame": get_relevant_reputational_features(),
            "stage_name": "Used Reputational Features",
            "suffix": "reputation",
        },
        "Webpage Content Model": {
            "data_frame": get_relevant_webpage_features(),
            "stage_name": "Used Webpage Features",
            "suffix": "webpage",
        }
    }

    print()
    show_popup_message("Creating and testing random forest models for each feature category", delay_secs=3, countdown_flag=True)

    # Creates and tests random forest models for each feature category
    load_bar(
        [
            lambda mt=model_title, d=data: create_random_forest_model(
                mt,
                d["data_frame"],
                d["suffix"],
                d["stage_name"]
            )
            for model_title, data in model_data.items()
        ]
    )


if __name__ == "__main__":
    main()
