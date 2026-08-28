import pandas as pd
import json
from notebook_utils import get_relevant_features, generate_sub_data_frame

TRAINING_DATA = "data/Training.parquet"
TESTING_DATA = "data/Testing.parquet"
FILE_PATH = "data/url_profile.json"

# Combines data from training and testing files
training_data_frame = pd.read_parquet(TRAINING_DATA, engine="pyarrow")
testing_data_frame = pd.read_parquet(TESTING_DATA, engine="pyarrow")
combined_data_frame = pd.concat([training_data_frame, testing_data_frame])

# Collect URLS based on status
phishing_urls = combined_data_frame[
    combined_data_frame["status"] == "phishing"
]
legitimate_urls = combined_data_frame[
    combined_data_frame["status"] == "legitimate"
]

# Redefine data frame based on relevant features
RELEVANT_FEATURES = get_relevant_features(combined_data_frame, use_parent_directory=False)
combined_data_frame = combined_data_frame.reindex(sorted(RELEVANT_FEATURES), axis=1)

# Feature collection
boolean_features = list(
    combined_data_frame.loc[:, (combined_data_frame.nunique() == 2)].columns
)
numeric_features = list(
    combined_data_frame.loc[:, (combined_data_frame.nunique() > 2)].columns
)

# Removes string-type features
numeric_features.remove("url")

profile = {
    "phishing": {},
    "legitimate": {}
}

ALL_UPPERCASED = ["tld","whois", "http", "https", "dns", "ip", "url", "css"]

shorthand_to_normal = {
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
}

# Calculates the average value for a numeric feature
for feature in numeric_features:
    feature_name = feature.replace("_", " ")
    feature_name = feature_name.replace("avg", "")

    for shorthand, normal in shorthand_to_normal.items():
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

    # Average Length Hostname -> Average Hostname Length
    if feature_name.startswith("Length "):
        feature_name = feature_name.replace("Length ", "")
        feature_name += " Length"
    
    # Removes trailing whitespace
    feature_name = feature_name.strip()

    profile["phishing"][f"{feature_name}".replace("  ", " ")] = phishing_urls[feature].mean()
    profile["legitimate"][f"{feature_name}".replace("  ", " ")] = legitimate_urls[feature].mean()
    
# Calculates percentage of URLs where the boolean feature is true
for feature in boolean_features:
    feature_name = feature.replace("_", " ")
    feature_name = feature_name.replace("nb", "")
    feature_name = feature_name.replace("  ", " ")

    for shorthand, normal in shorthand_to_normal.items():
        feature_name = feature_name.replace(shorthand, normal)

    feature_name = feature_name.title()

    feature_name = feature_name.replace("Ernal", "")
    feature_name = feature_name.replace("Int", "Internal ")
    feature_name = feature_name.title()  # To capitalize newly split words

    feature_name = feature_name.replace("In", "in")

    for word in ALL_UPPERCASED:
        feature_name = feature_name.replace(word.title(), word.upper())

    profile["phishing"][f"{feature_name}".replace("  ", " ")] = phishing_urls[feature].mean()
    profile["legitimate"][f"{feature_name}".replace("  ", " ")] = legitimate_urls[feature].mean()

# Correct grammar error in initial feature naming
try:
    profile["phishing"]["Suspicious TLD"] = profile["phishing"].pop("Suspecious TLD")
    profile["legitimate"]["Suspicious TLD"] = profile["legitimate"].pop("Suspecious TLD")
except KeyError:
    pass

with open(FILE_PATH, "w") as file:
    json.dump(profile, file, indent=4)
    file.close()
