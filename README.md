# URL Risk Analysis System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
![beautifulsoup4](https://img.shields.io/pypi/v/beautifulsoup4?label=BeautifulSoup&logo=python&logoColor=white)
![python-whois](https://img.shields.io/pypi/v/python-whois?label=Python-Whois&logo=python&logoColor=white)
![requests](https://img.shields.io/pypi/v/requests?label=Requests&logo=python&logoColor=white)
![tldextract](https://img.shields.io/pypi/v/tldextract?label=tldextract&logo=python&logoColor=white)

## Table of Contents
- [Overview](#overview)
- [Project Highlights](#project-highlights)
- [Dashboard](#dashboard)
- [Command Line Interface](#command-line-interface)
- [Installation](#installation)
- [Technologies Used](#technologies-used)

## Overview
***URL Risk Analysis System*** is a phishing website analysis platform consisting of an interactive machine learning dashboard and a command-line URL inspection tool. Users can explore phishing detection models, compare phishing and legitimate website characteristics, and perform detailed URL security analysis.

The tool aggregates low-level signals (e.g., domain age, mismatched links, hidden elements) into higher-level insights, helping users identify potentially unsafe or deceptive websites.

## Project Highlights
- Built and evaluated multiple machine learning phishing detection models
- Interactive Dash/Plotly analytics dashboard
- Feature importance and explainable ML visualizations
- Statistical profiling of phishing and legitimate URLs
- Command-line URL risk assessment and inspection


## Dashboard
The dashboard enables users to explore model performance, visualize feature importance, compare phishing and legitimate URL characteristics, and better understand how machine learning models identify malicious websites.

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

### Dashboard Preview
![Dashboard Preview](img/dashboard.gif)

## Command Line Interface
A detailed URL inspection tool that analyzes domain, certificate, transport, structural URL, and webpage characteristics to identify potential phishing indicators and provide explainable security insights.

### Command Line Interface Preview
![Full URL Analysis](img/full-analysis.gif)

### Features

- 🔍 Multi-layer URL inspection pipeline (domain → transport → content)
- 🧠 Signal-based risk detection with rule-based reasoning
- 🔐 TLS and certificate validation (including edge cases)
- 🌐 URL structure and obfuscation analysis
- 🎭 HTML/CSS behavior detection (hidden elements, overlays, deceptive links)
- 📖 Explainable outputs with human-readable security insights


## Installation
1. Download python from the official website ([https://www.python.org/downloads/](https://www.python.org/downloads/)) if you have not already done so.
2. Clone/download a copy of this repository.
3. Open your terminal and navigate to the project folder.
4. Create a virtual environment within the folder by typing in `python -m venv venv` and pressing enter.
    - Confirm that the `venv/` folder exists with: `ls` for Linux/macOs or `dir` for Windows.
5. Activate the environment
    - On Windows, this is done via: `venv\Scripts\Activate`.
    - On Linux/macOS, this is done via: `source venv/bin/activate`.
6. Install the necessary packages with into the environment: `pip install -r requirements.txt`.
7. Run either the dashboard or command line tool.

### Usage

#### Dashboard
- Run *.ipynb* notebooks 00-04 in the `notebooks` folder.
    - Confirm that files ending in *.pkl* were generated under `models/machine_learning` folder (these are the machine learning models from which performance will be measured)
- Run `python -m utils.statistcal_profiling.py`
    - Confirm that `url_profile.json` was created under the folder `data`.
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
