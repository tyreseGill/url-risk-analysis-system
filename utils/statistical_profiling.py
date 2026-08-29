import pandas as pd
import json
from utils.notebook_utils import get_relevant_features, generate_sub_data_frame


TRAINING_DATA = "data/Training.parquet"
TESTING_DATA = "data/Testing.parquet"
FILE_PATH = "data/url_profile.json"

SHORTHAND_TO_NORMAL = {
    "nb": "number of",
    " at": ' "@" symbols',
    "colon": '":" symbols',
    "comma": '"," symbols',
    "dollar": '"$" symbols',
    "dots": '"." symbols',
    "eq": '"=" symbols',
    "hyphens": '"-" symbols',
    "percent": '"%" symbols',
    "qm": '"?" symbols',
    "semicolumn": '";" symbols',
    " slash": ' "/" symbols',
    "underscore": '"_" symbols',
    "star": '"*" symbols',
    "tilde": '"~" symbols',
    "char": "characters",
    "ext": "external ",
    "tld": "top-level domain"
}

ALL_UPPERCASED = ["tld","whois", "http", "https", "dns", "ip", "url", "css"]


def get_combined_data_frame() -> pd.DataFrame:
    """
    Combines data from training and testing files.

    Returns:
        pd.DataFrame: Dataframe with data from both the testing and training datasets.
    """
    training_data_frame = pd.read_parquet(TRAINING_DATA, engine="pyarrow")
    testing_data_frame = pd.read_parquet(TESTING_DATA, engine="pyarrow")
    data_frame = pd.concat([training_data_frame, testing_data_frame])

    return data_frame


def categorize_features(data_frame: pd.DataFrame) -> (list, list):
    """
    Given a data frame, categorizes its features between boolean and numeric attributes.

    Args:
        data_frame: The data frame from which features/columns will be extracted from.

    Returns:
        tuple: Two lists representative of boolean and numeric features respectively.
    """
    # Redefine data frame based on relevant features
    RELEVANT_FEATURES = get_relevant_features(data_frame, use_parent_directory=False)
    data_frame = data_frame.reindex(sorted(RELEVANT_FEATURES), axis=1)

    # Feature collection
    boolean_features = list(
        data_frame.loc[:, (data_frame.nunique() == 2)].columns
    )
    numeric_features = list(
        data_frame.loc[:, (data_frame.nunique() > 2)].columns
    )

    # Removes string-type features
    if "url" in numeric_features:
        numeric_features.remove("url")

    return boolean_features, numeric_features


def generate_numeric_feature_title(feature_name: str) -> str:
    """
    Generates a title for a given feature representative of a numeric attribute.

    Args:
        feature_name: The string to be renamed for enhanced readability.
    
    Returns:
        str: A string representing a more human-readable version of the previous feature name.
    """
    feature_name = feature_name.replace("_", " ")
    feature_name = feature_name.replace("avg", "")

    for shorthand, normal in SHORTHAND_TO_NORMAL.items():
        feature_name = feature_name.replace(shorthand, normal)

    feature_name = feature_name.title()

    feature_name = feature_name.replace("Ernal", "")
    feature_name = feature_name.replace("Int", "Internal ")
    feature_name = feature_name.title()  # To capitalize newly split words

    feature_name = feature_name.replace("Www", '"WWW"s\'')
    feature_name = feature_name.replace("Com", '".com"s\'')
    feature_name = feature_name.replace("Of", "of")
    feature_name = feature_name.replace(" In ", " in ")

    for word in ALL_UPPERCASED:
        feature_name = feature_name.replace(word.title(), word.upper())

    # Removes trailing whitespace
    feature_name = feature_name.strip()

    # Average Length Hostname -> Average Hostname Length
    if feature_name.startswith("Length "):
        feature_name = feature_name.replace("Length ", "")
        feature_name += " Length"

    # Provided more descriptive name for certain features
    if feature_name == "Statistical Report":
        feature_name = "Flagged in Statistical Report"
    elif feature_name == "Phish Hints":
        feature_name = "Number of Phish Hints"
    elif feature_name == "Ratio Digits Host":
        feature_name = "Percentage of Digits in Hostname"
    elif feature_name == "Ratio Digits URL":
        feature_name = "Percentage of Digits in URL"
    elif feature_name == "Number of Redirection":
        feature_name = "Number of Redirections"

    if "Ratio" in feature_name:
        feature_name = feature_name.replace("Ratio", "Percentage of")

    feature_name = feature_name.replace("  ", " ")
    
    return feature_name


def generate_boolean_feature_title(feature_name: str) -> str:
    """
    Generates a title for a given feature representative of a boolean attribute.

    Args:
        feature_name: The string to be renamed for enhanced readability.
    
    Returns:
        str: A string representing a more human-readable version of the previous feature name.
    """
    feature_name = feature_name.replace("_", " ")
    feature_name = feature_name.replace("nb", "")
    feature_name = feature_name.replace("  ", " ")

    for shorthand, normal in SHORTHAND_TO_NORMAL.items():
        feature_name = feature_name.replace(shorthand, normal)

    feature_name = feature_name.title()

    feature_name = feature_name.replace("Ernal", "")
    feature_name = feature_name.replace("Int", "Internal ")
    feature_name = feature_name.title()  # To capitalize newly split words

    feature_name = feature_name.replace("In ", "in ")
    feature_name = feature_name.replace(" With ", " with ")

    for word in ALL_UPPERCASED:
        feature_name = feature_name.replace(word.title(), word.upper())
    
    # Removes trailing whitespace
    feature_name = feature_name.strip()

    # Provided more descriptive name for certain features
    if feature_name == "IP":
        feature_name = "IP Address"   

    if "Suspecious" in feature_name:
        feature_name = feature_name.replace("Suspecious", "Suspicious")

    feature_name = feature_name.replace("  ", " ")

    return feature_name



def generate_profiles(data_frame: pd.DataFrame, numeric_features: list, boolean_features: list) -> dict:
    """
    Generates nested dictionary representing profile makeup of typical phishing and 
    legitimate URLs.

    Args:
        data_frame: The data frame from which to URLs will be categorized between phishing 
            and legitimate URLs. 
        numeric_features: The list of numeric features to be renamed.
        boolean_features: The list of boolean features to be renamed.
    
    Returns:
        dict: A dictionary describing the characteristics of phishing and legitimate 
            URLs respectively.
    """
    profile = {
        "phishing": {},
        "legitimate": {}
    }

    # Collect URLS based on status
    phishing_urls = data_frame[
        data_frame["status"] == "phishing"
    ]
    legitimate_urls = data_frame[
        data_frame["status"] == "legitimate"
    ]

    # Calculates and displays average value for a numeric feature
    for feature in numeric_features:
        feature_title = generate_numeric_feature_title(feature)

        # Renames each feature to be more readable
        profile["phishing"][feature_title] = phishing_urls[feature].mean()
        profile["legitimate"][feature_title] = legitimate_urls[feature].mean()
        
    # Calculates and displays percentage of URLs where the boolean feature is true
    for feature in boolean_features:
        feature_title = generate_boolean_feature_title(feature)

        # Renames each feature to be more readable
        profile["phishing"][feature_title] = phishing_urls[feature].mean()
        profile["legitimate"][feature_title] = legitimate_urls[feature].mean()

    return profile


def main():
    data_frame = get_combined_data_frame()
    boolean_features, numeric_features = categorize_features(data_frame)
    profile = generate_profiles(data_frame, numeric_features, boolean_features)

    with open(FILE_PATH, "w") as file:
        json.dump(profile, file, indent=4)
        file.close()


if __name__ == "__main__":
    main()
