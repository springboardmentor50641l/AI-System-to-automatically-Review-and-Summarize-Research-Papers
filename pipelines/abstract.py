from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import json


def generate_abstract(compare_result: dict, model_name="gemini-2.5-flash") -> str:
    """
    Generates a structured abstract using comparison results.
    """

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        timeout=120
    )

    structured_input = json.dumps(compare_result, indent=2)

    prompt = f"""
    You are generating a structured academic abstract based strictly on provided structured comparison data.

    Comparison Data:
    {structured_input}

    Write a structured abstract with the following sections:
    - Background
    - Objective
    - Methods Overview
    - Results
    - Conclusion

    Rules:
    - Use only the information provided.
    - Do NOT fabricate numerical values.
    - Synthesize across papers where possible.
    - Maintain formal academic tone.
    - Return plain text only.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
