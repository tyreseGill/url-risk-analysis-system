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


TRAINING_DATA = "../data/Training.parquet"
TESTING_DATA = "../data/Testing.parquet"
TARGET = "status"


# https://wellsr.com/python/upsampling-and-downsampling-imbalanced-data-in-python/
def frame_target_imbalance(df: pd.DataFrame, label="Status"):
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
    """
    data_frame[featured_distro].hist(figsize=(11, 8), bins=50)
    plt.suptitle("Feature Frequency")
    plt.tight_layout()
    plt.show()

    
def generate_sub_data_frame(cols: set, parquet_file: str = TRAINING_DATA, add_status: bool = True):
    """
    Creates a data frame from the provided columns.
    """
    cols = set(cols)
    
    if add_status:
        cols.add('status')
        
    data_frame = pd.read_parquet(parquet_file, columns=cols)
    
    if add_status:
        data_frame["status"] = (
            data_frame["status"] == "phishing"
        ).astype(int)

    data_frame = data_frame.reindex(sorted(data_frame.columns), axis=1)
        
    return data_frame


def frame_correlation_matrix(df: pd.DataFrame, threshold: float=0, annotate: bool=True):
    """
    Displays correlation matrix of a dataframe.
    """
    correlation_matrix = df.corr(numeric_only=True)
    correlation_matrix[abs(correlation_matrix) < threshold] = 0
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=annotate, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.show()


def get_correlation_to_target(cols: set, target: str = TARGET):
    """
    Obtains the intersecting correlation value between the given columns and a target row.
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
    """
    corr_matrix = data_frame.corr(numeric_only=True).abs()
    num_cols = len(data_frame.columns)
    top_pairs = corr_matrix.unstack().sort_values(ascending=False)[num_cols: num_cols + (num_pairs_to_list * 2): 2]
    
    return top_pairs


def get_highly_correlated_pairs(data_frame: pd.DataFrame, threshold=0.8) -> set:
    """
    Obtains column-pairings with a high correlation to each other.
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
    Determines and obtains the redundant feature from each highly-correlated column pairing.
    """
    REDUNDANT_ATTRIBUTES = set()
    
    data_frame = generate_sub_data_frame(
        set(data_frame.columns)
    )
    
    corr_matrix = data_frame.corr(numeric_only=True).abs()
    
    for x, y in get_highly_correlated_pairs(data_frame):
        corr_val_x = corr_matrix.at[TARGET, x]
        corr_val_y = corr_matrix.at[TARGET, y]
    
        if corr_val_x > corr_val_y:
            REDUNDANT_ATTRIBUTES.add(y)
        elif corr_val_y > corr_val_x:
            REDUNDANT_ATTRIBUTES.add(x)

    return REDUNDANT_ATTRIBUTES


def frame_box_plot(data_frame: pd.DataFrame, title: str):
    """
    Generates a box plot to visualize data spread.
    """
    data_frame.plot(kind="box")
    plt.title(title)
    plt.xticks(rotation=90)
    plt.show()


def get_low_target_correlation_features(data_frame: pd.DataFrame, threshold: float = 0.01):
    """
    Retrieves features with a very low correlation with regard to the variable to be predicted.
    """
    REDUNDANT_ATTRIBUTES = set()
    
    data_frame = generate_sub_data_frame(
        set(data_frame.columns)
    )
    
    target_row = data_frame.corr(numeric_only=True)[TARGET].abs()

    for column_name, corr_val in target_row.items():
        if corr_val <= threshold:
            REDUNDANT_ATTRIBUTES.add(column_name)

    return REDUNDANT_ATTRIBUTES


def save_redundant_features(redundant_features: set):
    """
    Saves redundant features to .pkl file.
    """
    try:
        with open('../data/redundant_features.pkl', 'wb') as file:
            pickle.dump(redundant_features, file)
    finally:
        file.close()
    

def save_stage_metrics(model_name: str, stage_name: str, model_path: str, relevant_features: set, model):
    """
    Saves performance metrics for a stage in data analysis process.
    """
    training_data_frame = generate_sub_data_frame(
        relevant_features
    )

    testing_data_frame = generate_sub_data_frame(
        cols=training_data_frame.columns,
        parquet_file=TESTING_DATA
    )
    
    x_train, y_train = get_x_y(training_data_frame)
    x_test, y_test = get_x_y(testing_data_frame)

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    _, fp, fn, _ = confusion_matrix(y_test, y_pred).ravel()
    num_misclassifications = fp + fn

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred)

    file_path = "../data/model_metrics.json"

    stage_metrics = {
        "model_path": f"models/machine_learning/{model_path}.pkl",
        "num_features": len(relevant_features),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc auc": roc_auc,
        "misclassifications": int(num_misclassifications)
    }

    # Loads in and adds to JSON file if it already exists
    if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
        # Loads JSON entries
        with open(file_path, "r") as file:
            metrics = json.load(file)

        # Creates model entry if not available
        if model_name not in metrics:
            metrics[model_name] = {}

        metrics[f"{model_name}"][f"{stage_name}"] = stage_metrics

        # Saves updates model entry
        with open(file_path, "w") as file:
            json.dump(metrics, file, indent=4)
            
        file.close()

    # Creates JSON file from scratch and adds first entry
    else:
        with open(file_path, "w") as file:
            metrics = {
                f"{model_name}": {
                    f"{stage_name}": stage_metrics
                }
            }
            json.dump(metrics, file, indent=4)

            file.close()


def get_redundant_features():
    """
    Fetches redundant features from .pkl file.
    """
    REDUNDANT_FEATURES = set()
    
    try:
        with open('../data/redundant_features.pkl', 'rb') as file:
            REDUNDANT_FEATURES = pickle.load(file)
    finally:
        file.close()

    return REDUNDANT_FEATURES


def get_relevant_features(data_frame: pd.DataFrame):
    """
    Returns set of relevant features.
    """
    REDUNDANT_FEATURES = get_redundant_features()
    
    RELEVANT_FEATURES = {
        col for col in data_frame.columns
        if col not in REDUNDANT_FEATURES
        and col != "status"
    }
    
    return RELEVANT_FEATURES


def get_x_y(data_frame: pd.DataFrame):
    """
    Obtains the features (x) and status (y) of a URL.
    """
    columns_to_drop = [TARGET]

    if "url" in data_frame.columns:
        columns_to_drop.append("url")

    x = data_frame.drop(columns=columns_to_drop)
    y = data_frame[TARGET]

    return x, y


def test_model(model, model_file_name: str, training_data_frame: pd.DataFrame):
    """
    Trains a model and prints out its training and testing results.
    """
    testing_data_frame = generate_sub_data_frame(
        cols=training_data_frame.columns,
        parquet_file=TESTING_DATA
    )

    # Fetch attributes and status of URL
    x_test, y_test = get_x_y(testing_data_frame)
    x_train, y_train = get_x_y(training_data_frame)

    # Trains model
    model.fit(x_train, y_train)

    # Test model predictions
    y_train_predicted = model.predict(x_train)
    y_test_predicted = model.predict(x_test)

    # Save the model as a pickle in a file
    MODEL_PATH = f"../models/machine_learning/{model_file_name}.pkl"
    joblib.dump(model, MODEL_PATH)

    print("\nTraining Report:")
    print(classification_report(y_train, y_train_predicted))
    print("\nTest Report:")
    print(classification_report(y_test, y_test_predicted))
    
    return model


# Source: https://www.geeksforgeeks.org/machine-learning/how-to-generate-feature-importance-plots-from-scikit-learn/
def plot_feature_importance(clf):
    """
    Plots bar char illustrating feature importance in descending order.
    """
    importances = clf.feature_importances_
    
    # Sort feature importances in descending order
    indices = np.argsort(importances)[::-1]
    
    # Rearrange feature names so they match the sorted feature importances
    names = [clf.feature_names_in_[i] for i in indices]
    data_frame = generate_sub_data_frame(cols=clf.feature_names_in_, parquet_file=TESTING_DATA, add_status=False)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances")
    plt.bar(range(data_frame.shape[1]), importances[indices])
    plt.xticks(range(data_frame.shape[1]), names, rotation=90)
    plt.xlabel("Features")
    plt.ylabel("Importance")
    plt.show()
