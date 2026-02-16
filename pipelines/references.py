from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json
def format_authors_apa(authors_str: str) -> str:
    """
    Converts comma-separated authors into APA format.
    Handles multiple authors properly.
    """
    authors = [a.strip() for a in authors_str.split(",") if a.strip()]

    formatted = []
    for author in authors:
        parts = author.split()
        if len(parts) == 1:
            formatted.append(parts[0])
        else:
            last_name = parts[-1]
            initials = " ".join([p[0] + "." for p in parts[:-1]])
            formatted.append(f"{last_name}, {initials}")

    # APA formatting rules
    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} & {formatted[1]}"
    else:
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"



def format_apa_reference(metadata: dict) -> str:
    authors = format_authors_apa(metadata.get("authors", "Unknown"))
    year = metadata.get("year", "n.d.")
    title = metadata.get("title", "Untitled")
    source = metadata.get("source", "Unknown source")

    return f"{authors} ({year}). {title}. {source}."
