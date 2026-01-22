def clean_text(text):
    """
    Cleans raw extracted text
    """
    # Remove tabs
    text = text.replace("\t", " ")

    # Remove extra spaces
    while "  " in text:
        text = text.replace("  ", " ")

    # Remove leading & trailing spaces
    return text.strip()
