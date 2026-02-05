def normalize_text(text: str) -> str:
    """
    Perform minimal normalization on extracted PDF text.
    This removes common line-break artifacts while
    preserving the original semantic meaning.
    """
    # Fix hyphenated line breaks
    text = text.replace("-\n", "")

    # Reduce excessive newlines
    text = text.replace("\n\n", "\n")

    return text

