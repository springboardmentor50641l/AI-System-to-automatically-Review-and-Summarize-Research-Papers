from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json


def generate_results(compare_result: dict, model_name="gemini-2.5-flash") -> str:
    """
    Generates a Results section synthesizing performance findings.
    """

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        timeout=120
    )

    structured_input = json.dumps(compare_result, indent=2)

    prompt = f"""
    Based on the following structured comparison data:

    {structured_input}

    Generate a formal "Results" section that:

    - Synthesizes quantitative findings.
    - Highlights performance improvements.
    - Notes ensemble or multi-model performance.
    - Mentions computational efficiency findings.
    - Identifies any limitations.

    Rules:
    - Preserve all numerical values exactly as given.
    - Do NOT create new statistics.
    - Academic tone.
    - Return plain text only.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
