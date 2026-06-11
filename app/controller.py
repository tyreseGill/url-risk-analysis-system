from models.network.whois import query_url, query_exists
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
import argparse


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
    Perform batch analysis on URLs read from "urls.txt".

    Args:
        params (argparse.Namespace): Parsed CLI arguments specifying analysis options.
    """
    try:
        file = open("urls.txt", "r")
        urls = [
            line.strip("\n")
            for line in 
            file.readlines()
            if not line.startswith("#")
            and line.strip("\n") != ""
        ]
    finally:
        file.close()

    for url in urls:
        params.url = url
        analysis(params)
