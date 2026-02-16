from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json


def generate_methods(compare_result: dict, model_name="gemini-2.5-flash") -> str:
    """
    Generates a Methods section by analyzing comparative claims.
    """

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        timeout=120
    )

    structured_input = json.dumps(compare_result, indent=2)

    prompt = f"""
    Using the following structured comparison data:

    {structured_input}

    Generate a formal academic "Methods" section that:

    - Describes the methodological approaches referenced in the claims.
    - Identifies models, architectures, or algorithms discussed.
    - Mentions evaluation strategies (e.g., multi-crop evaluation, ensemble methods).
    - Explains comparative framework across studies if applicable.

    Rules:
    - Do NOT invent methods not mentioned.
    - Base reasoning only on provided claims.
    - Academic tone.
    - Return plain text only.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
