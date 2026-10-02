# URL Risk Analysis System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Framework-blue?logo=plotly&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Dash_Bootstrap_Components-7952Brap&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Web_Scraping-green)
![Requests](https://img.shields.io/badge/Requests-HTTP_Client-orange)
![Python-Whois](https://img.shields.io/badge/Python--Whois-Domain_Analysis-red)
![tldextract](https://img.shields.io/badge/tldextract-URL_Parsing-yellow)
![Cryptography](https://img.shields.io/badge/Cryptography-Security-darkgreen)

## Table of Contents
- [Overview](#overview)
- [Project Highlights](#project-highlights)
- [Dashboard](#dashboard)
- [Command Line Interface](#command-line-interface)
- [Architecture](#architecture)
- [Installation](#installation)
- [Technologies Used](#technologies-used)

## Overview
***URL Risk Analysis System*** is a phishing website analysis platform consisting of an interactive machine learning dashboard and a command-line URL inspection tool. Users can explore phishing detection models, compare phishing and legitimate website characteristics, and perform detailed URL security analysis.

The tool aggregates low-level signals (e.g., domain age, mismatched links, hidden elements) into higher-level insights, helping users identify potentially unsafe or deceptive websites.

## Attributions to Datasets Used

This project utilizes the **Phishing Url** dataset by [Hemanth Pingali](https://www.kaggle.com/hemanthpingali),
obtained from [Kaggle](https://www.kaggle.com/) at https://www.kaggle.com/datasets/hemanthpingali/phishing-url.

The dataset is licensed under [**CC BY-NC-SA 4.0**](https://creativecommons.org/licenses/by-nc-sa/4.0/). No modifications were made to the original dataset. It is used for model training, evaluation, and feature analysis within this project.

For exploratory data analysis (EDA) and to understand the rationale behind feature removal decisions, see [dataset_overview.ipynb](docs/dataset_overview.ipynb).

## Project Highlights
- Built and evaluated multiple machine learning phishing detection models
- Interactive Dash/Plotly analytics dashboard
- Feature importance and explainable ML visualizations
- Statistical profiling of phishing and legitimate URLs
- Command-line URL risk assessment and inspection

## Dashboard
The dashboard enables users to explore model performance, visualize feature importance, compare phishing and legitimate URL characteristics, and better understand how machine learning models identify malicious websites. The dashboard is deployed and available at [https://url-risk-analysis-dashboard.onrender.com/](https://url-risk-analysis-dashboard.onrender.com/).

### Dashboard Preview
![Dashboard Preview](assets/gif/dashboard.gif)

### Features
- 📈 Model Performance Metrics
    - Accuracy
    - Precision
    - Recall
    - F1-Score
    - ROC-AUC
- 📊 Feature Importance Analysis
    - Displays the most important predictive features used by the selected model
    - Updates automatically when a different model is selected
- 🆚 URL Profile Comparison
    - Compares characteristic phishing and legitimate URL patterns side-by-side
- 𖣠 Radar Chart
    - Compares phishing and legitimate URL profiles across the model's five most important features
    - Enables quick visual identification of distinguishing characteristics

## Command Line Interface
A detailed URL inspection tool that analyzes domain, certificate, transport, structural URL, and webpage characteristics to identify potential phishing indicators and provide explainable security insights.

### Command Line Interface Preview
![Full URL Analysis](assets/gif/full-analysis.gif)

### Features

- 🔍 Multi-layer URL inspection pipeline
- 🧠 Signal-based risk detection with rule-based reasoning
- 🔐 TLS and certificate validation
- 🌐 URL structure and obfuscation analysis
- 🎭 HTML/CSS behavior detection (hidden elements, overlays, deceptive links)
- 📖 Explainable outputs with human-readable security insights

## Architecture

The URL Risk Analysis System combines multiple analysis techniques and external intelligence sources to evaluate the risk associated with a URL. For a detailed overview of the system design, see [architecture.md](docs/architecture.md) for architecture diagrams created using [diagrams.net](https://app.diagrams.net/).

The architecture documentation includes:
- Network topology
- Risk analysis hierarchy
- Multi-stage evaluation pipeline
- Analysis methods and data sources

## Installation
1. Download python from the official website ([https://www.python.org/downloads/](https://www.python.org/downloads/)) if you have not already done so.
2. Clone/download a copy of this repository.
3. Open your terminal and navigate to the project folder.
4. Create a virtual environment within the folder by typing in `python -m venv venv` and pressing enter.

> [!NOTE]
> Confirm that the `venv/` folder was created using `dir` for Windows users or `ls` for Linux/macOs users.

5. Activate the environment

> [!NOTE]
> On Windows, this is done via: `venv\Scripts\Activate`.
> On Linux/macOS, this is done via: `source venv/bin/activate`.

6. Install the necessary packages into the environment
    - Application users run: `pip install -r requirements.txt`.

> [!TIP]
> In addition to running the above command, developers looking to contribute should run: `pip install -r requirements-dev.txt`

7. Run either the dashboard or command line tool based on

> [!NOTE]
> To utilize the "VirusTotal Malware Scan" feature, you will need to signup with [VirusTotal](https://www.virustotal.com/gui/join-us) in order to get an API key to interact with their API. Use of this feature will be permitted after inputting the line `API_KEY="{YOUR_API_KEY_FOR_VIRUSTOTAL}"` into a *.env* file at project root.

### Usage

#### Dashboard
- Run `python -m app.generate_models`

> [!NOTE]
> Confirm that files ending in *.pkl* were generated under `models/machine_learning/` folder (these are the machine learning models from which performance will be measured)

- Run `python -m utils.statistcal_profiling.py`

> [!NOTE]
> Confirm that `url_profile.json` was created under the folder `data/`.

- Run `python -m app.dashboard`.
- Open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) on your browser to view dashboard.

#### Command Line
- Refer to [cli.md](docs/cli.md) for specific command instructions and usages.

## Technologies Used
- Programming Languages
    - Python
    - JavaScript
    - CSS
- Python Libraries Used
    - BeautifulSoup
    - Dash
    - Joblib
    - Matplotlib
    - Numpy
    - Plotly
    - Pandas
    - Seaborn
    - Scikit-learn
