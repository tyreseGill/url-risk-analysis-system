from app.cli import parse_args, resolve_analysis_flags
from app.controller import analysis, multi_analysis


def main():
    parser, params = parse_args()
    params = resolve_analysis_flags(params)

    if params.url and params.multi_analysis:
        parser.error("Cannot specify a URL and perform a multi-analysis at the same time")
    elif not params.url and not params.multi_analysis:
        parser.error('You must either input a URL to analyze or run multiple analyses on URLs listed in "urls.txt"')

    if params.multi_analysis:
        multi_analysis(params)
    else:
        analysis(params)


if __name__ == "__main__":
    main()
