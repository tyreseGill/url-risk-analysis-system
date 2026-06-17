# Link Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
![beautifulsoup4](https://img.shields.io/pypi/v/beautifulsoup4?label=BeautifulSoup&logo=python&logoColor=white)
![python-whois](https://img.shields.io/pypi/v/python-whois?label=Python-Whois&logo=python&logoColor=white)
![requests](https://img.shields.io/pypi/v/requests?label=Requests&logo=python&logoColor=white)
![tldextract](https://img.shields.io/pypi/v/tldextract?label=tldextract&logo=python&logoColor=white)

## Description
***Link Analyzer*** is a command-line tool designed to inspect and evaluate the security posture of a given URL. It performs multi-layered analysis across domain identity, URL structure, transport security, TLS certificates, and HTML/CSS behavior to detect common phishing and malicious patterns.

The tool aggregates low-level signals (e.g., domain age, mismatched links, hidden elements) into higher-level insights, helping users identify potentially unsafe or deceptive websites.

Key capabilities include:
- Domain registration and lifecycle analysis
- URL structure and obfuscation detection
- HTTPS and TLS certificate validation
- HTML and CSS behavior analysis (e.g., overlays, hidden elements)
- Explainable risk signals for educational insight

## Features

- 🔍 Multi-layer URL inspection pipeline (domain → transport → content)
- 🧠 Signal-based risk detection with rule-based reasoning
- 🔐 TLS and certificate validation (including edge cases)
- 🌐 URL structure and obfuscation analysis
- 🎭 HTML/CSS behavior detection (hidden elements, overlays, deceptive links)
- 📖 Explainable outputs with human-readable security insights


## Usage Instructions
1. Download python from the official website ([https://www.python.org/downloads/](https://www.python.org/downloads/)) if you have not already done so.
2. Clone/download a copy of this repository.
3. Open your terminal and navigate to the project folder.
4. Create a virtual environment within the folder by typing in `python -m venv venv` and pressing enter.
    - Confirm that the `venv/` folder exists with: `ls` for Linux/macOs or `dir` for Windows.
5. Activate the environment
    - On Windows, this is done via: `venv\Scripts\Activate`.
    - On Linux/macOS, this is done via: `source venv/bin/activate`.
6. Install the necessary packages with into the environment: `pip install -r requirements.txt`.
7. Run the program by running the example commands below.



## Notes

- All domains used in the following examples are safe, publicly documented, or reserved for testing purposes (e.g., example.com, badssl.com, neverssl.com).
- To utilize the VirusTotal feature, you will need to signup with VirusTotal in order to get an API key to interact with their API. Use of this feature will be permitted after inputting the line `API_KEY={YOUR_API_KEY_FOR_VIRUSTOTAL}` into a *.env* file within the directory.


## Arguments

### Usage:
```bash
python main.py <url> [options]
```

### Analysis Options
|Analysis            |Description                                               |
|--------------------|----------------------------------------------------------|
|domain_identity     |Performs Whois lookup for domain name registration details|
|url_structure       |Examines structural makeup of a URL                       |
|transport_security  |Performs HTTPS Check                                      |
|ssl, tls, cert      |Validates SSL/TLS certificate                             |
|html                |Examines HTML/CSS                                         |
|virustotal          |Performs VirusTotal lookup for malware                    |

### Mode Options
|Modes             |Description                                                                |
|------------------|---------------------------------------------------------------------------|
|default           |Runs safest configuration of analyses if no specific analysis is given     |
|passive           |Avoids direct contact to target site via a network connection              |
|offline, air_gap  |Runs only those analyses that require no network usage                     |
|full              |Runs all analyses

### Filter Options
|Filters    |Description                                   |
|-----------|----------------------------------------------|
|exclude    |Prevents the specified analyses from running  |

### Output Options
|Output             |Description                                         |
|-------------------|----------------------------------------------------|
|no_explanations    |Disables print out of explanations in risk summary  |
|no_summary         |Disables print out of risk summary                  |

## Commands and Outputs

### Legend

- ✅ <span style="color:#22c55e">GREEN</span> = Expected / secure component  
- ⚠️ <span style="color:#eab308">YELLOW</span> = Suspicious indicator  
- ❌ <span style="color:#ef4444">RED</span> = High-risk signal  

### Case #1: Default Scan
```bash
python ./main.py google.com
```
![Default URL Analysis](assets/default-analysis.png)

### Case #2: Full Analysis
```bash
python ./main.py https://example.com --full
```
![Full URL Analysis](assets/full-analysis.gif)

### Case #3: Passive Analysis
```bash
python ./main.py example.net --domain_identity
```
![Whois URL Analysis](assets/passive-analysis.png)

### Case #4: Offline Analysis (w/ Spoofed URL)
```bash
# Intentionally spoofed URL for demonstration
python ./main.py http://login-goȱgle.verify.secure.account.attacker.xyz --url_structure
```
![Structural URL Analysis](assets/url-struct-analysis.png)

### Case #5: Transport Security Analysis
```bash
python ./main.py http://neverssl.com/ --transport_security
```
![Secure Communication Analysis](assets/insecure-comm-analysis.png)

### Case #6: SSL/TLS Certificate Analysis (w/ Expired Certificate)
```bash
python ./main.py https://expired.badssl.com --cert
```
![SSL/TLS Certificate Analysis](assets/expired-cert-analysis.png)

### Case #7: SSL/TLS Certificate Analysis (w/ Self-Signed Certificate)
```bash
python ./main.py https://self-signed.badssl.com/ --cert
```
![SSL/TLS Certificate Analysis](assets/self-signed-cert-analysis.png)

## Architectural Designs and Future Blueprints

![Analysis Methods](assets/analysis-methods.drawio.svg)


![Order of Risk Analysis](assets/order_of_risk_analysis.drawio.svg)


![Analysis Work Flow](assets/detection-system-finite-automata.drawio.svg)


![Network Topology](assets/network-topology-diagram.drawio.png)

