from views.helpers import print_header, print_kv
from views.style import highlight


def print_transport_security_analysis(risk: dict):
    print_header("Transport Security")
    print_https_support_status(risk)

    
def print_https_support_status(risk: dict):
    color = risk["https_support"]["color"]
    status = risk["https_support"]["status"]
    value = highlight(status, color)
    print_kv("HTTPS Supported", value)
