import pandas as pd
import json

TRAINING_DATA = "data/Training.parquet"
TESTING_DATA = "data/Testing.parquet"
FILE_PATH = "data/url_profile.json"

training_data_frame = pd.read_parquet(TRAINING_DATA, engine="pyarrow")
testing_data_frame = pd.read_parquet(TESTING_DATA, engine="pyarrow")
combined_data_frame = pd.concat([training_data_frame, testing_data_frame])

phishing_urls = combined_data_frame[
    combined_data_frame["status"] == "phishing"
]

legitimate_urls = combined_data_frame[
    combined_data_frame["status"] == "legitimate"
]

# Feature collection
boolean_features = list(
    combined_data_frame.loc[:, (combined_data_frame.nunique() == 2)].columns
)
numeric_features = list(
    combined_data_frame.loc[:, (combined_data_frame.nunique() > 2)].columns
)

# Removes string-type features
boolean_features.remove("status")
numeric_features.remove("url")

profile = {
    "phishing": {},
    "legitimate": {}
}

# Calculates the average value for a numeric feature
for feature in numeric_features:
    profile["phishing"][f"{feature}_mean"] = phishing_urls[feature].mean()
    profile["legitimate"][f"{feature}_mean"] = phishing_urls[feature].mean()
    
# Calculates percentage of URLs where the boolean feature is true
for feature in boolean_features:
    profile["phishing"][f"has_{feature}"] = phishing_urls[feature].mean()
    profile["legitimate"][f"has_{feature}"] = phishing_urls[feature].mean()

with open(FILE_PATH, "w") as file:
    json.dump(profile, file, indent=4)
    file.close()
