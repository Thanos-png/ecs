
def remove_greek_accents(text: str) -> str:
    """
    Remove Greek accents from text.
    """
    # Greek accent mappings
    accent_map = {
        # Lowercase with tonos
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        # Uppercase with tonos
        'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ώ': 'Ω',
        # With dialytika and tonos
        'ΐ': 'ι', 'ΰ': 'υ',
        # With dialytika only
        'ϊ': 'ι', 'ϋ': 'υ', 'Ϊ': 'Ι', 'Ϋ': 'Υ'
    }

    result = text
    for accented, unaccented in accent_map.items():
        result = result.replace(accented, unaccented)

    return result


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
