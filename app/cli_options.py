from app.parser import SafeArgumentParser


def add_positional_options(parser: SafeArgumentParser) -> SafeArgumentParser:
    parser.add_argument(
        "url",
        type=str,
        nargs="?",
        help="Target URL to analyze"
    )
    parser.add_argument(
        "--multi_analysis",
        "--batch_analysis",
        action="store_true",
        help='Analyzes urls stored in "url.txt"'
    )

    return parser


def add_analysis_options(parser: SafeArgumentParser) -> SafeArgumentParser:
    analysis_group = parser.add_argument_group("Analysis Options")

    analysis_group.add_argument(
        "--domain_identity",
        action="store_true",
        help="Whois info"
    )
    analysis_group.add_argument(
        "--url_structure",
        action="store_true",
        help="URL structural analysis"
    )
    analysis_group.add_argument(
        "--transport_security",
        action="store_true",
        help="HTTPS check"
    )
    analysis_group.add_argument(
        "--ssl",
        "--tls",
        "--cert",
        dest="tls",
        action="store_true",
        help="SSL/TLS certificate info"
    )
    analysis_group.add_argument(
        "--html",
        action="store_true",
        help="HTML analysis"
    )
    analysis_group.add_argument(
        "--virustotal",
        action="store_true",
        help="VirusTotal lookup"
    )

    return parser


def add_mode_options(parser: SafeArgumentParser) -> SafeArgumentParser:
    mode_group = parser.add_argument_group("Mode Options")

    mode_group.add_argument(
        "--full",
        action="store_true",
        help="Runs all analyses"
    )
    mode_group.add_argument(
        "--offline",
        "--air_gap",
        action="store_true",
        help="No network usage"
    )
    mode_group.add_argument(
        "--passive",
        action="store_true",
        help="No direct contact to target via network connection"
    )

    return parser


def add_filter_options(parser: SafeArgumentParser) -> SafeArgumentParser:
    filter_group = parser.add_argument_group("Filter Options")

    filter_group.add_argument(
        "--exclude",
        nargs="+",
        choices=[
            "domain_identity",
            "url_structure",
            "transport_security",
            "tls_cert",
            "html",
            "virustotal"
        ],
        help="Excludes analyses"
    )

    return parser


def add_output_options(parser: SafeArgumentParser) -> SafeArgumentParser:
    output_flag = parser.add_argument_group("Output Options")

    output_flag.add_argument(
        "--no_explanations",
        action="store_false",
        help="Disables print out of explanations in risk summary"
    )
    output_flag.add_argument(
        "--no_summary",
        action="store_true",
        help="Disables print out of risk summary"
    )

    return parser
