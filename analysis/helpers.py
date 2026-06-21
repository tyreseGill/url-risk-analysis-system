import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


TRAINING_DATA = "data/Testing.parquet"
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

    
def generate_sub_data_frame(cols: set, parquet_file: str = TRAINING_DATA):
    """
    Creates a data frame from the provided columns.
    """
    cols.add('status')
    data_frame = pd.read_parquet(parquet_file, columns=cols)
    data_frame["status"] = (
        data_frame["status"] == "phishing"
    ).astype(int)
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
    Obtains top X number of column-pairings with the highest correlation. 
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
