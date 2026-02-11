# utils/llm_utils.py

def normalize_llm_output(content):
    """
    Ensures LLM output is always returned as clean readable string.
    Handles:
    - Plain string
    - List of dicts
    - Dict format
    """

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        cleaned_parts = []

        for item in content:
            if isinstance(item, dict) and "text" in item:
                cleaned_parts.append(item["text"])
            else:
                cleaned_parts.append(str(item))

        return "\n".join(cleaned_parts).strip()

    if isinstance(content, dict):
        if "text" in content:
            return content["text"].strip()
        return str(content)

    return str(content).strip()
