
class Span:
    """Represents a highlighted region within a string.
    
    Attributes:
        start (int): Start index of the span (inclusive).
        end (int): End index of the span (exclusive).
        color (str): ANSI color code associated with this span.
    """
    def __init__(self, start, end, color):
        self.start = start
        self.end = end
        self.color = color
        
    def __repr__(self):
        
        def get_color():
            match self.color:
                case "\033[92m":
                    return "green"
                case "\033[91m":
                    return "yellow"
                case "\033[93m":
                    return "red"
                case _:
                    return "Unknown color"
                
        color = get_color()
        
        return f"(({self.start}, {self.end}), {color!s})"
    

def make_spans(list_spans: list[Span], color: str) -> list[Span]:
    """Converts raw (start, end) tuples into Span objects with shared color."""
    return [ Span(start, end, color) for start, end in list_spans ]


def collect_spans(check_list: dict, url: str, domain: str=None) -> list[Span]:
    """
    Runs multiple span-returning detection functions along with their expected color.

    Attributes:
        check_list: Dictionary of function-color pairs determining the color for the spans returned from each function.
        url: URL to inspect.
        domain: Optional, determines whether scope is confined to domain or the full URL.

    Returns:
        list: Aggregated spans from all detection functions.
    """
    spans = []
    domain_index = url.find(domain) if domain else 0

    for check_func, color in check_list.items():
        for start, end in check_func(domain or url):
            start += domain_index
            end += domain_index
            spans.append(
                Span(start, end, color)
            )
    
    return spans

