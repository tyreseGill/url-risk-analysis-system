from models.network.whois import query_url, query_exists
from models.network.html_parser import fetch_absolute_links
from models.network.html_parser import convert_html_to_soup
from models.risk.classifiers import classify_risk
from models.risk_context import RiskContext
from models.url.parsing import extract_hostname
from views.domain import print_domain_identity_analysis
from views.url import print_url_struct_analysis
from views.transport import print_transport_security_analysis
from views.cert import print_cert_analysis
from views.html import print_html_analysis
from views.virustotal import print_virus_total_stats
from views.summary import print_risk_summary
from utils.animations import show_popup_message
import argparse
import os


def analysis(params: argparse.Namespace):
    """
    Performs an analysis on a URL based on the provided arguments.

    Args:
        params (argparse.Namespace): Parsed CLI arguments specifying the target URL
         and selected analysis options.
    """
    query = query_url(params.url) if params.domain_identity else None
    ctx = RiskContext()

    # Early return for non-existent URLs when query expected
    if params.domain_identity and not query_exists(params.url, query):
        return
    
    risk = classify_risk(params, ctx, query)
    
    if params.domain_identity:
        print_domain_identity_analysis(risk, query)

    if params.url_structure:
        print_url_struct_analysis(risk)

    if params.transport_security:
        print_transport_security_analysis(risk)

    if params.tls:
        domain_name = extract_hostname(params.url)
        print_cert_analysis(domain_name, ctx)

    if params.html:
        print_html_analysis(params.url, ctx)

    if params.virustotal:
        print_virus_total_stats(params.url)
    
    if not params.no_summary:
        print_risk_summary(params.no_explanations, ctx)
    
    print()


def multi_analysis(params: argparse.Namespace):
    """
    Perform batch analysis on URLs read from input file.

    Args:
        params (argparse.Namespace): Parsed CLI arguments specifying analysis options.
    """
    file_to_parse = "input/urls.txt"  # Default

    if params.input:
        # Allows user to input either the absolute path or relative path from the "input/" directory
        file_to_parse = (
            f"input/{params.input}"
            if os.path.isfile(f"input/{params.input}")
            else params.input
        )

        if not os.path.isfile(file_to_parse):
            print(f'[ERROR] The path "{file_to_parse}" was not found.\n')
            return

    urls = extract_urls(file_to_parse)

    if not urls:
        return

    for url in urls:
        params.url = url
        print()
        analysis(params)


def extract_urls(file:str):
    """
    Extracts all URLs from a file.

    Args:
        file (str): The file to be parsed.
    
    Returns:
        list[str]: List of URLs.
    """
    file_extension = file.split(".")[-1]

    if file_extension in ["txt", "csv"]:
        try:
            file = open(file, "r")
            urls = [
                line.strip("\n")
                for line in 
                file.readlines()  # Only works for .txt and .csv
                if not line.startswith("#")
                and line.strip("\n") != ""
            ]
            urls = filter_urls(urls)
        finally:
            file.close()

    elif file_extension in ["html", "htm"]:
        html_soup = convert_html_to_soup(file)
        abs_links = fetch_absolute_links(html_soup)
        urls = [
            link.get('href') for link in abs_links
        ]

        urls = filter_urls(urls)

    elif file_extension == "pdf":
        pass

    else:
        print(f'[ERROR] The format "{file_extension}" is not supported.\n')
        return None

    return urls


def filter_urls(urls: list) -> list:
    """
    Returns strings recognized as URLs based on the presence of a schema (http/https)
     and hostname format.

     Args:
        urls: List of potential URLs to be filtered out for suspected URLs.

    Returns:
        list[str]: Filtered list of recognized URLs.
    """
    from urllib.parse import urlparse
    
    urls = [
        url
        for url in urls
        if urlparse(url).scheme and extract_hostname(url)
    ]
    return urls

