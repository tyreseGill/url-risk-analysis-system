from views.helpers import print_header, print_kv


def print_url_struct_analysis(risk: dict):
    print_header("URL Structure Analysis")
    color_coded_url = risk["url_structure"]["rendered_url"]
    print_kv("Analyzed URL", color_coded_url)
