from google import genai
from google.genai import types
import os

try:
    # API key check
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise Exception("GEMINI_API_KEY is missing.")

    # Gemini client
    client = genai.Client(api_key=api_key)

    # Open screenshot
    with open("chat.jpeg", "rb") as f:
        image_bytes = f.read()

    # Analysis prompt
    prompt = """
    Analyze the provided screenshot and determine whether the visible
    message/content is likely to be AI-generated.

    Return ONLY valid JSON in exactly this format:

    {
      "ai_likelihood": 0,
      "reasoning": "Brief explanation of the clues found in the screenshot.",
      "confidence": 0
    }

    Rules:
    - ai_likelihood must be a number from 0 to 100.
    - 0 means very unlikely to be AI-generated.
    - 100 means very likely to be AI-generated.
    - confidence must be a number from 0 to 100.
    - Base the analysis only on evidence visible in the screenshot.
    - Do not invent information that is not visible.
    - Return valid JSON only.
    - Do not use Markdown or code fences.
    """

    # Send image + prompt
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/png"
            ),
            prompt
        ]
    )

    # Successful response
    print("Gemini Response:")
    print(response.text)

except FileNotFoundError:
    print("ERROR: Screenshot file was not found.")

except Exception as e:
    print("Gemini API Error:")
    print(e)