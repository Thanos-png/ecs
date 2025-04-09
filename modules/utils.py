
def progress_bar(progress, total, bar_length=60):
    """Display a more compact progress bar that updates in place
    
    Args:
        progress: Current progress position
        total: Total items to process
        bar_length: Length of the progress bar in characters
    """
    percent = 100 * (progress / float(total))
    filled_length = int(bar_length * progress // total)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    
    # Use carriage return to reset cursor position, but don't add a newline
    print(f"\r|{bar}| {percent:.1f}%", end="", flush=True)
