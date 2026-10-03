from models.network.html_analysis import (
    analyze_css,
    analyze_external_domains,
    analyze_html,
)
from models.network.html_parser import fetch_external_css
from models.network.requests import fetch_page_resource, fetch_page_resource_soup
from models.risk_context import RiskContext
from models.url.parsing import contains_scheme
from views.helpers import print_header, print_kv
from views.style import highlight_green, highlight_red, highlight_yellow


def print_html_analysis(url: str, ctx: RiskContext):
    print_header("HTML Content & Link Analysis")
    
    if not contains_scheme(url):
        url = "https://" + url

    soup = fetch_page_resource_soup(url)
    value = highlight_green("Yes") if soup else highlight_red("No")

    print_kv("HTML Retrieved", value)

    if not soup:
        return

    result = analyze_html(url, soup, ctx)

    # Scripts
    num_scripts_detected = result["script_count"]
    value = (
        highlight_green(num_scripts_detected)
        if num_scripts_detected == 0
        else highlight_yellow(num_scripts_detected)
    )
    print_kv("Scripts Detected", value)

    # External domains
    external_domains = result["external_domains"]
    num_external_domains = len(external_domains)
    value = (
        highlight_green(num_external_domains) 
        if num_external_domains == 0 
        else highlight_yellow(num_external_domains)
    )
    print_kv("External Links", value)

    if external_domains:
        print_kv("External Domains", ', '.join(external_domains))

    # Mismatch
    num_mismatches = result["mismatch_count"]
    value = (
        highlight_green(num_mismatches) 
        if num_mismatches == 0 
        else highlight_red(num_mismatches)
    )
    print_kv("Mismatched URLs", value)

    # Suspicious domains
    sus_links = analyze_external_domains(external_domains)
    if sus_links:
        print_kv("Suspicious External Links", ', '.join(sus_links))

    html = fetch_page_resource(url)
    external_links = fetch_external_css(soup)
    result = analyze_css(html, external_links, ctx)

    # CSS check for invisible elements and overlays
    hidden_elems_flag = result["hidden_elements_present"]
    invisible_elems_detected = (
        highlight_yellow("Yes")
        if hidden_elems_flag
        else highlight_green("No")
    )
    print_kv("Suspicious Hidden Elements Detected", invisible_elems_detected)

    overlays_flag = result["overlays_present"]
    overlays_detected = (
        highlight_yellow("Yes")
        if overlays_flag
        else highlight_green("No")
    )
    print_kv("Overlays Detected", overlays_detected)
    