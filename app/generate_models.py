import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator
from utils.notebook_utils import generate_sub_data_frame, test_model, save_stage_metrics, get_relevant_features, save_redundant_features, get_redundant_correlated_features, get_low_target_correlation_features
from utils.animations import load_bar, show_popup_message


def get_all_relevant_features(model: BaseEstimator) -> pd.DataFrame:
    """
    Retrieves all relevant features from the dataset by removing constant features, redundant correlated features, and low target correlation features.

    Args:
        model: The machine learning model used for testing.

    Returns:
        cleaned_data_frame: The cleaned data frame after removing irrelevant features.
    """
    full_data_frame = pd.read_parquet("data/Training.parquet", engine='pyarrow')
    cleaned_data_frame = pd.DataFrame()
    REDUNDANT_FEATURES = set()
    RELEVANT_FEATURES = set()

    MODEL_TITLE = f"Random Forest (All Features)"
    MODEL_FILE_NAME = f"random_forest_all"

    # Raw Data
    save_stage_metrics(
        MODEL_TITLE,
        "Raw Data",
        MODEL_FILE_NAME,
        set(full_data_frame.columns),
        model
    )


    def remove_constant_features(model: BaseEstimator, full_data_frame: pd.DataFrame) -> set:
        """
        Removes features that have constant values across all samples from the full data frame.

        Args:
            model: The machine learning model used for testing.
            full_data_frame: The full data frame containing all features.

        Returns:
            set: A set of redundant features that have constant values.
        """
        
        REDUNDANT_FEATURES = set(
            full_data_frame.loc[:, (full_data_frame.nunique() == 1)].columns
        )

        save_redundant_features(REDUNDANT_FEATURES)

        save_stage_metrics(
            MODEL_TITLE,
            "Remove Constant Features",
            MODEL_FILE_NAME,
            set(full_data_frame.columns) - set(REDUNDANT_FEATURES),
            model
        )

        return REDUNDANT_FEATURES


    REDUNDANT_FEATURES.update(remove_constant_features(model, full_data_frame))


    def remove_redundant_highly_correlated_features(model: BaseEstimator, full_data_frame: pd.DataFrame, cleaned_data_frame: pd.DataFrame) -> tuple:
        """
        Removes features that are highly correlated with each other from the cleaned data frame.

        Args:
            model: The machine learning model used for testing.
            full_data_frame: The full data frame containing all features.
            cleaned_data_frame: The cleaned data frame after removing constant features.

        Returns:
            tuple: A tuple containing the relevant features and the updated cleaned data frame.
        """
        RELEVANT_FEATURES = get_relevant_features(full_data_frame)

        cleaned_data_frame = generate_sub_data_frame(
            RELEVANT_FEATURES
        )

        REDUNDANT_FEATURES.update(
            get_redundant_correlated_features(cleaned_data_frame)
        )

        save_redundant_features(REDUNDANT_FEATURES)

        save_stage_metrics(
            MODEL_TITLE,
            "Remove Redundant Correlation Features",
            MODEL_FILE_NAME,
            set(full_data_frame.columns) - set(REDUNDANT_FEATURES),
            model
        )

        return RELEVANT_FEATURES, cleaned_data_frame
    

    RELEVANT_FEATURES, cleaned_data_frame = remove_redundant_highly_correlated_features(model, full_data_frame, cleaned_data_frame)


    def remove_low_target_correlation_features(model: BaseEstimator, full_data_frame: pd.DataFrame, cleaned_data_frame: pd.DataFrame):
        """
        Removes features that have low correlation with the target variable from the cleaned data frame.

        Args:
            model: The machine learning model used for testing.
            full_data_frame: The full data frame containing all features.
            cleaned_data_frame: The cleaned data frame after removing constant features.

        Returns:
            tuple: A tuple containing the relevant features and the updated cleaned data frame.
        """
        REDUNDANT_FEATURES.update(
            get_low_target_correlation_features(cleaned_data_frame)
        )

        save_redundant_features(REDUNDANT_FEATURES)

        save_stage_metrics(
            MODEL_TITLE,
            "Remove Low-Correlation Features",
            MODEL_FILE_NAME,
            set(full_data_frame.columns) - set(REDUNDANT_FEATURES),
            model
        )

        return RELEVANT_FEATURES, cleaned_data_frame

    
    RELEVANT_FEATURES, cleaned_data_frame = remove_low_target_correlation_features(model, full_data_frame, cleaned_data_frame)

    cleaned_data_frame = generate_sub_data_frame(
        RELEVANT_FEATURES
    )

    return cleaned_data_frame


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

    tasks = [
            lambda: get_all_relevant_features(
                RandomForestClassifier(random_state=41)
            ),
            *[
                lambda mt=model_title, d=data: create_random_forest_model(
                    mt,
                    d["data_frame"],
                    d["suffix"],
                    d["stage_name"]
                )
                for model_title, data in model_data.items()
            ]
        ]
    

    # Creates and tests random forest models for each feature category
    load_bar(
        tasks
    )


if __name__ == "__main__":
    main()
