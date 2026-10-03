import argparse
import sys


class SafeArgumentParser(argparse.ArgumentParser):
    """
    A subclass of argparse.ArgumentParser that overrides the default error behavior.

    Args:
        argparse.ArgumentParser: Object for parsing command line strings into Python objects.

    Methods:
        error(message): Overrides the default error handler to print a custom error message
            and terminate the program with a non-zero exit code.
    """
    def error(self, message: str):
        first_letter = message[0]
        message = message.replace(first_letter, first_letter.upper(), 1)

        print(f"\n[ERROR] {message}.\n")
        self.print_help()
        sys.exit(2)
