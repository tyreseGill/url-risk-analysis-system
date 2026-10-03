import argparse

from app.cli_options import *
from app.parser import SafeArgumentParser
from models.network.virustotal import virustotal_available
from utils.animations import show_popup_message


def parse_args() -> argparse.Namespace:
    """
    Manages and defines expected arguments and behavior for the command-line interface.

    Returns:
        SafeArgumentParser: Subclass of ArgumentParser designed to handle errors gracefully.
        Namespace: Collection of arguments and the associated input values provided by the user.
    """
    parser = SafeArgumentParser(
        description="Analyze a URL for red flags",
        usage="\tpython main.py <url> [options]"
    )

    # Adds arguments as options to choose from
    parser = add_positional_options(parser)
    parser = add_analysis_options(parser)
    parser = add_mode_options(parser)
    parser = add_filter_options(parser)
    parser = add_output_options(parser)

    # Extracts the data associated from the aforementioned arguments
    params = parser.parse_args()

    return parser, params


def resolve_analysis_flags(params: argparse.Namespace) -> argparse.Namespace:
    """
    Determines which analysis sections should run by resolving mutually exclusive, 
    default, full, and offline modes.

    Args:
        params: Parsed CLI arguments.
    
    Returns:
        argparse.Namespace: Updated arguments to reflect resolved analysis flags.
    """
    vt_available = virustotal_available()

    if params.virustotal:
        if not vt_available:
            show_popup_message("\n[INFO] VirusTotal disabled (no API key found)", delay_secs=2)

        params.virustotal = vt_available

    analysis_requested = any([
        params.url_structure,
        params.domain_identity,
        params.dns,
        params.transport_security,
        params.tls,
        params.html,
        params.virustotal
    ])

    # Performs analysis without direct network contact
    if params.passive :
        params.url_structure = True
        params.domain_identity = True
        params.dns = False
        params.transport_security = False
        params.tls = False
        params.html = False
        params.virustotal = vt_available

    # Performs all analyses
    elif params.full:
        params.url_structure = True
        params.domain_identity = True
        params.dns = True
        params.transport_security = True
        params.tls = True
        params.html = True
        params.virustotal = vt_available
    
    # Performs analysis with offline-capabilities
    elif params.offline:
        params.url_structure = True
        params.domain_identity = False
        params.dns = False
        params.transport_security = False
        params.tls = False
        params.html = False
        params.virustotal = False
    
    # Performs passive analysis by default if no specific analysis is specified
    elif not analysis_requested:
        show_popup_message('\n[INFO] Running passive analysis by default (no analysis specified)', delay_secs=2)
        params.domain_identity = True
        params.url_structure = True
        params.virustotal = vt_available

    # Performs enabled analyses with the exception of any analyses following "--exclude"
    if params.exclude:
        for excluded_param in params.exclude:
            setattr(params, excluded_param, False)

    return params
