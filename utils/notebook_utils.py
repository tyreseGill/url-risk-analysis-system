import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pickle
import json
import joblib
import os
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.base import BaseEstimator


TRAINING_DATA = "data/Training.parquet"
TESTING_DATA = "data/Testing.parquet"
TARGET = "status"


# Source: https://wellsr.com/python/upsampling-and-downsampling-imbalanced-data-in-python/
def frame_target_imbalance(df: pd.DataFrame, label="Status"):
    """
    Creates a pie chart representation of the target variable's class imbalance.

    Args:
        df: A data frame containing the target variable.
        label: The label for the target variable.
    """
    df.groupby(TARGET).size().plot(
        kind="pie",
        y=TARGET,
        title=f"{label} Class Imbalance",
        labels=[f"{label} = Phishing",
                f"{label} = Legitimate"],
        autopct="%1.1f%%")


def showcase_featured_distributions(data_frame: pd.DataFrame, featured_distro: set):
    """
    Creates a histogram representation for each provided feature.

    Args:
        data_frame: A data frame containing the features to display.
        featured_distro: A set of column names for the features to display.
    """
    data_frame[featured_distro].hist(figsize=(11, 8), bins=50)
    plt.suptitle("Feature Frequency")
    plt.tight_layout()
    plt.show()

    
def generate_sub_data_frame(cols: set, parquet_file: str = TRAINING_DATA, add_status: bool = True) -> pd.DataFrame:
    """
    Creates a sub-data frame from a given parquet file with the specified columns.

    Args:
        cols: A set of column names to include in the sub-data frame.
        parquet_file: The path to the parquet file from which to create the sub-data frame.
        add_status: Whether to include the "status" column in the sub-data frame.
    
    Returns:
        pd.DataFrame: A sub-data frame containing the specified columns.
    """
    cols = set(cols)
    
    if add_status:
        cols.add('status')
        
    data_frame = pd.read_parquet(parquet_file, columns=cols)
    
    # Prevents the "status" column from being a string type for machine learning purposes
    if add_status:
        data_frame["status"] = (
            data_frame["status"] == "phishing"
        ).astype(int)

    # Sorts the columns of the data frame in alphabetical order
    data_frame = data_frame.reindex(sorted(data_frame.columns), axis=1)
        
    return data_frame


def extract_datasets(training_data_frame: pd.DataFrame) -> tuple:
    """
    Extracts the training and testing datasets from the provided training data frame.

    Args:
        training_data_frame: The data frame from which to extract the training and testing datasets.
    
    Returns:
        tuple: A tuple containing the training features (x_train), training labels (y_train),
    """
    testing_data_frame = generate_sub_data_frame(
        cols=training_data_frame.columns,
        parquet_file=TESTING_DATA
    )
    
    x_train, y_train = get_x_y(training_data_frame)
    x_test, y_test = get_x_y(testing_data_frame)
    return x_train, y_train, x_test, y_test


def train_model(model: BaseEstimator, training_data_frame: pd.DataFrame) -> BaseEstimator:
    """
    Creates a scikit-learn model and trains it on the provided training data frame.

    Args:
        model: A scikit-learn model to be trained.
        training_data_frame: The data frame from which the model will be trained.

    Returns:
        BaseEstimator: A scikit-learn model.
    """
    x_train, y_train, _, _ = extract_datasets(training_data_frame)
    model.fit(x_train, y_train)
    return model


def frame_correlation_matrix(df: pd.DataFrame, threshold: float=0, annotate: bool=True):
    """
    Displays a heatmap of the correlation matrix for a given data frame.

    Args:
        df: The data frame for which to display the correlation matrix.
        threshold: The threshold for displaying correlations.
        annotate: Whether to annotate the heatmap with correlation values.
    """
    correlation_matrix = df.corr(numeric_only=True)
    correlation_matrix[abs(correlation_matrix) < threshold] = 0
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=annotate, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.show()


def get_correlation_to_target(cols: set, target: str = TARGET) -> pd.Series:
    """
    Obtains the intersecting correlation value between the given columns and a target row.

    Args:
        cols: A set of column names for which to obtain correlation values.
        target: The target row for which to obtain correlation values.

    Returns:
        pd.Series: A series containing the correlation values between the given columns and the target row.
    """
    cols.add('status')
    data_frame = generate_sub_data_frame(cols)
    
    corr_with_target = (
        data_frame.corr(numeric_only=True)[target]
        .sort_values(ascending=False)
    )
    
    return corr_with_target


def get_top_correlation_pairs(data_frame: pd.DataFrame, num_pairs_to_list: int) -> pd.Series:
    """
    Obtains top data_frame number of column-pairings with the highest correlation. 

    Args:
        data_frame: The data frame for which to obtain the top correlation pairs.
        num_pairs_to_list: The number of top correlation pairs to return.
    
    Returns:
        pd.Series: A series containing the top correlation pairs and their corresponding correlation values.
    """
    corr_matrix = data_frame.corr(numeric_only=True).abs()
    num_cols = len(data_frame.columns)
    top_pairs = corr_matrix.unstack().sort_values(ascending=False)[
        num_cols: num_cols + (num_pairs_to_list * 2): 2
    ]
    
    return top_pairs


def get_highly_correlated_pairs(data_frame: pd.DataFrame, threshold=0.8) -> set:
    """
    Obtains column-pairings with a high correlation to each other.

    Args:
        data_frame: The data frame for which to obtain highly correlated pairs.
        threshold: The threshold for determining high correlation between column pairs.

    Returns:
        set: A set of column pairs with high correlation.
    """
    corr_matrix = data_frame.corr(numeric_only=True).abs()
    num_cols = len(data_frame.columns)
    most_to_least_corr_pairs = corr_matrix.unstack().sort_values(ascending=False)[num_cols:]
    highly_corr_pairs = set()

    # Adds any non-status column-pairings whose intercepting correlation value are too high
    for (pair, corr_pair_value) in most_to_least_corr_pairs[::2].items():
        (x, y) = pair
        corr_pair_value = math.ceil(corr_pair_value * 100) / 100  # Rounds up to nearest tenth

        # Prevents tossing out features with high correlation to URL status
        if 'status' in pair:
            continue
        
        if corr_pair_value >= threshold:
            highly_corr_pairs.add(pair)
            
    return highly_corr_pairs


def get_redundant_correlated_features(data_frame: pd.DataFrame) -> set:
    """
    Obtains redundant features from a given data frame based on their correlation to 
    each other and the target variable.

    Args:
        data_frame: The data frame for which to obtain redundant features.

    Returns:
        set: A set of redundant features.
    """
    REDUNDANT_ATTRIBUTES = set()
    
    data_frame = generate_sub_data_frame(
        set(data_frame.columns)
    )
    
    corr_matrix = data_frame.corr(numeric_only=True).abs()
    
    # Compares the correlation values of each column in the pairing to the target variable
    for x, y in get_highly_correlated_pairs(data_frame):
        corr_val_x = corr_matrix.at[TARGET, x]
        corr_val_y = corr_matrix.at[TARGET, y]
    
        # Adds the column with the lower correlation value to the set of redundant attributes
        if corr_val_x > corr_val_y:
            REDUNDANT_ATTRIBUTES.add(y)
        elif corr_val_y > corr_val_x:
            REDUNDANT_ATTRIBUTES.add(x)

    return REDUNDANT_ATTRIBUTES


def frame_box_plot(data_frame: pd.DataFrame, title: str):
    """
    Generates a box plot to visualize data spread.

    Args:
        data_frame: The data frame for which to generate the box plot.
        title: The title of the box plot.
    """
    data_frame.plot(kind="box")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.show()


def get_low_target_correlation_features(data_frame: pd.DataFrame, threshold: float = 0.01) -> set:
    """
    Retrieves features with a very low correlation with regard to the variable to be predicted.

    Args:
        data_frame: The data frame for which to obtain low correlation features.
        threshold: The threshold for determining low correlation with the target variable.
    
    Returns:
        set: A set of features with low correlation to the target variable.
    """
    REDUNDANT_ATTRIBUTES = set()
    
    data_frame = generate_sub_data_frame(
        set(data_frame.columns)
    )
    
    target_row = data_frame.corr(numeric_only=True)[TARGET].abs()

    # Adds any non-status columns whose correlation value to the target variable is too low
    for column_name, corr_val in target_row.items():
        if corr_val <= threshold:
            REDUNDANT_ATTRIBUTES.add(column_name)

    return REDUNDANT_ATTRIBUTES


def save_redundant_features(redundant_features: set):
    """
    Saves redundant features to .pkl file.

    Args:
        redundant_features: A set of redundant features to be saved.
    """
    try:
        with open('data/redundant_features.pkl', 'wb') as file:
            pickle.dump(redundant_features, file)
    finally:
        file.close()

    
def pickle_model(model: BaseEstimator, file_name: str):
    """
    Saves a scikit-learn model to a .pkl file.

    Args:
        model: The scikit-learn model to be saved.
        file_name: The name of the .pkl file to be created.
    """
    MODEL_PATH = f"models/machine_learning/{file_name}.pkl"

    # Updates .pkl for existing model if it exists
    try:
        joblib.dump(model, MODEL_PATH)
    # Model path doesn't exist
    except FileNotFoundError:
        # Creates directory and .pkl file from scratch
        os.mkdir("models/machine_learning")
        open(MODEL_PATH, 'w').close()

        joblib.dump(model, MODEL_PATH)


def save_metric_data_to_file(model_name: str, stage_name: str, metric_data: dict, file_path: str):
    """
    Saves metric data to a JSON file.

    Args:
        model_name: The name of the model in "model_metrics.json".
        stage_name: The stage of the model at which metrics are being collected for.
        metric_data: The metric data to be saved.
        file_path: The file path to the "model_metrics.json" file.
    """
    # Updates existing model entry in "model_metrics.json" if it exists
    try:
        # Loads existing JSON entries from file
        with open(file_path, "r") as file:
            metrics = json.load(file)

        # Updates JSON entries with new metric data
        if model_name not in metrics:
            metrics[model_name] = {}

        metrics[model_name][stage_name] = metric_data

        # Saves updated JSON entries to file
        with open(file_path, "w") as file:
            json.dump(metrics, file, indent=4)
            
        file.close()

    # Creates new "model_metrics.json" file if it doesn't exist
    except FileNotFoundError:
        with open(file_path, "w") as file:
            metrics = {
                model_name: {
                    stage_name: metric_data
                }
            }
            json.dump(metrics, file, indent=4)

            file.close()
    

def save_stage_metrics(model_name: str, stage_name: str, model_path: str, relevant_features: set, model: BaseEstimator):
    """
    Saves performance metrics for a stage in data analysis process.

    Args:
        model_name: The name of the model in "model_metrics.json".
        stage_name: The stage of the model at which metrics are being collected for.
        model_path: The file path to the .pkl for the model.
        relevant_features: The features on which the model trained on.
        model: The model from which metric data will be obtained and saved from.
    """
    FILE_PATH = "data/model_metrics.json"

    training_data_frame = generate_sub_data_frame(
        relevant_features
    )

    model = train_model(model, training_data_frame)

    # Tests model predictions on the testing data set
    _, _, x_test, y_test = extract_datasets(training_data_frame)
    y_pred = model.predict(x_test)

    # Calculates number of misclassifications
    _, fp, fn, _ = confusion_matrix(y_test, y_pred).ravel()
    num_misclassifications = fp + fn

    # Calculates performance metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred)

    # Creates dictionary of metric data to be saved to file
    stage_metric_data = {
        "model_path": f"models/machine_learning/{model_path}.pkl",
        "num_features": len(relevant_features),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc auc": roc_auc,
        "misclassifications": int(num_misclassifications)
    }

    save_metric_data_to_file(model_name, stage_name, stage_metric_data, FILE_PATH)


def get_redundant_features() -> set:
    """
    Returns set of redundant features.
    
    Returns:
        set: A set of redundant features.
    """
    REDUNDANT_FEATURES = set()
    PKL_FILE_PATH = "data/redundant_features.pkl"
    
    # Loads redundant features from .pkl file if it exists
    try:
        with open(PKL_FILE_PATH, 'rb') as file:
            REDUNDANT_FEATURES = pickle.load(file)
    finally:
        file.close()

    return REDUNDANT_FEATURES


def get_relevant_features(data_frame: pd.DataFrame) -> set:
    """
    Returns a set of relevant features from a given data frame.

    Args:
        data_frame: The data frame from which relevant features will be obtained.
    
    Returns:
        set: A set of relevant features.
    """
    REDUNDANT_FEATURES = get_redundant_features()
    
    RELEVANT_FEATURES = {
        col for col in data_frame.columns
        if col not in REDUNDANT_FEATURES
        and col != "status"
    }
    
    return RELEVANT_FEATURES


def get_x_y(data_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Obtains the features (x) and status (y) of a URL.

    Args:
        data_frame: The data frame from which features and status will be obtained.

    Returns:
        x: The features of a URL.
        y: The status of a URL.
    """
    columns_to_drop = [TARGET]

    # Prevents dropping the "url" column if it doesn't exist in the data frame
    if "url" in data_frame.columns:
        columns_to_drop.append("url")

    x = data_frame.drop(columns=columns_to_drop)
    y = data_frame[TARGET]

    return x, y


def test_model(model: BaseEstimator, file_name: str, training_data_frame: pd.DataFrame):
    """
    Tests a scikit-learn model and saves it to a .pkl file.

    Args:
        model: The scikit-learn model to be tested.
        file_name: The name of the .pkl file to be created.
        training_data_frame: The data frame from which the model was trained.
    """
    model = train_model(model, training_data_frame)
    x_train, y_train, x_test, y_test = extract_datasets(training_data_frame)

    # Test model predictions
    y_train_predicted = model.predict(x_train)
    y_test_predicted = model.predict(x_test)

    pickle_model(model, file_name)


# Source: https://www.geeksforgeeks.org/machine-learning/how-to-generate-feature-importance-plots-from-scikit-learn/
def plot_feature_importance(clf: BaseEstimator):
    """
    Plots the feature importance of a scikit-learn model.

    Args:
        clf: The scikit-learn model from which feature-importance will be plotted.
    """
    importances = clf.feature_importances_
    
    # Sort feature importances in descending order
    indices = np.argsort(importances)[::-1]
    
    # Rearrange feature names so they match the sorted feature importances
    names = [clf.feature_names_in_[i] for i in indices]
    data_frame = generate_sub_data_frame(
        cols=clf.feature_names_in_,
        parquet_file=TESTING_DATA,
        add_status=False
    )
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances")
    plt.bar(range(data_frame.shape[1]), importances[indices])
    plt.xticks(range(data_frame.shape[1]), names, rotation=90)
    plt.xlabel("Features")
    plt.ylabel("Importance")
    plt.show()
