import sys
import threading
import time
from typing import Callable, Any
from views.style import highlight, RED, YELLOW, GREEN


def dot_animation(base_message: str, stop_event: threading.Event):
    """
    Loads animation cycle of three dots being generated, removed, regenerated, and so on.

    :param base_message: The portion of a message which is to remain static.
    :param stop_event: The flag that determines when to stop the animation.
    """
    dynamic_message = base_message
    dot_str = " . "
    max_message_length = len(base_message) +  len(dot_str * 3)
    num_dots_to_load = 0

    def edit_line(message: str):
        sys.stdout.write("\r" + message)
        sys.stdout.flush()

    def clear_line():
        sys.stdout.write("\r" + (" " * max_message_length))
        sys.stdout.write("\r")
        sys.stdout.flush()

    # Runs animation until function completes its task
    while not stop_event.is_set():
        # 
        if (num_dots_to_load + 1) % 4 == 0:
            dynamic_message = base_message
            num_dots_to_load = 0
            clear_line()
        else:
            num_dots_to_load += 1
        
        # Adds X number of dots to be loaded to root message
        dynamic_message = base_message + (dot_str * num_dots_to_load)

        edit_line(dynamic_message)
        time.sleep(0.5)

    clear_line()


def edit_line(message: str):
    sys.stdout.write("\r" + message)
    sys.stdout.flush()

def clear_line(cutoff_length = 59):
    sys.stdout.write("\r" + (" " * cutoff_length))
    sys.stdout.write("\r")
    sys.stdout.flush()


def load_bar(task_functs: list[Callable], cutoff_length=59):
    num_functions = len(task_functs)
    midpoint = cutoff_length // 2
    gap = "  "  # Spacing around percentage

    def edit_line(message: str):
        sys.stdout.write("\r" + message)
        sys.stdout.flush()

    edit_line(f"{" " * midpoint}{gap}{highlight("0%", RED)}{gap}{" " * midpoint}")

    for index, task in enumerate(task_functs, start=1):
        task()
        
        # Calcules progress
        progress_ratio = index / num_functions
        percentage = int(progress_ratio * 100)
        percentage_str = f"{percentage}%"

        # Calculates total fill width (excluding the center)
        center_width = len(f"{gap}{percentage_str}{gap}")
        total_fill_width = cutoff_length - center_width
        filled = round(progress_ratio * total_fill_width)

        # Highlights percentage
        if 0 <= percentage <= 33:
            percentage_str = highlight(percentage_str, RED)
        elif 33 <= percentage <= 66:
            percentage_str = highlight(percentage_str, YELLOW)
        else:
            percentage_str = highlight(percentage_str, GREEN)

        # Calculates number of fills left/right around center
        left_fill = min(filled, midpoint)
        right_fill = max(0, filled - midpoint)

        # Calculates remain empty space
        left_space = midpoint - left_fill
        right_space = midpoint - right_fill
        
        line = (
            f"{"=" * left_fill}"
            f"{" " * left_space}"
            f"{gap}"
            f"{percentage_str}"
            f"{gap}"
            f"{"=" * right_fill}"
            f"{" " * right_space}"
        )
        
        edit_line(line)

    edit_line(f"{"=" * midpoint}{gap}{highlight("100%", GREEN)}{gap}{"=" * midpoint}")
    time.sleep(1)
    
    clear_line()


def display_load_animation(task_func: Callable, message: str, *args: tuple) -> Any:
    """
    Runs a loading animation as some function executes.

    :param task_func: The function to load an animation for as it completes a task.
    :param message: The message to be displayed in loading animation.
    :return: Any expected output from the passed function.
    """
    stop_event = threading.Event()

    loader = threading.Thread(
        target=dot_animation,
        args=(message, stop_event)
    )

    loader.start()  # Starts running load animation

    try:      # Wait for function to return something
        result = task_func(*args)
    finally:  # Stops running load animation
        stop_event.set()
        loader.join()

    return result


def show_popup_message(message: str, delay_secs: int = 1, countdown_flag: bool = False):
    """
    Displays a message for X amount of seconds before disappearing.

    :param message: The text to be temporarily displayed.
    :param delay_secs: (optional) The delay in seconds until the message is removed.
    :param countdown_flag: (optional) Determines whether a countdown will be attached.
    """

    def clear_line(message):
        sys.stdout.write("\r" + (" " * len(message)))
        sys.stdout.write("\r")
        sys.stdout.flush()

    if countdown_flag:
        for sec in range(delay_secs, 0, -1):
            new_message = f"{message} in {sec}..."
            print(new_message, end="\r", flush=True)
            time.sleep(1)
            clear_line(new_message)
    else:  # Generic pop-up message
        print(message, end="\r", flush=True)
        time.sleep(delay_secs)
        clear_line(message)
        