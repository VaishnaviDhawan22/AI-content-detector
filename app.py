import os
import re
import json
import statistics

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
ALLOWED_MIME = {"image/png", "image/jpeg", "image/webp"}

PROMPT = """
You are an AI-content detector. Analyze the provided text and/or screenshot
and estimate whether the message is likely AI-generated.

Return JSON in exactly this format:
{
  "ai_likelihood": 0,
  "confidence": 0,
  "reasoning": "Brief explanation of the clues you found.",
  "extracted_text": "The message text you analyzed (max 1500 characters)."
}

Rules:
- ai_likelihood and confidence are numbers from 0 to 100.
- 0 = very unlikely AI-generated, 100 = very likely AI-generated.
- Base your analysis only on evidence in the input. Do not invent details.
- Short or casual messages are hard to judge: lower your confidence for them.
"""

STOCK_PHRASES = [
    "as an ai", "i hope this helps", "certainly!", "delve", "in conclusion",
    "it is important to note", "furthermore", "moreover", "tapestry",
    "i'd be happy to", "feel free to", "great question", "in today's",
    "ever-evolving", "navigate the",
]
CASUAL_MARKERS = r"\b(lol|lmao|bro|haha|hehe|yaar|nah|bruh|idk|u|ur|ok|k)\b"


def clamp(value, low=0, high=100):
    try:
        return max(low, min(high, float(value)))
    except (TypeError, ValueError):
        return 0.0


def heuristic_score(text):
    """Simple rule-based score (0-100). Returns None if text is too short."""
    if not text:
        return None
    lower = text.lower()
    words = re.findall(r"[a-zA-Z']+", lower)
    if len(words) < 15:
        return None

    score = 35.0

    # 1. Very uniform sentence lengths -> more AI-like
    sentences = [s for s in re.split(r"[.!?]+\s", text) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    if len(lengths) >= 3:
        mean = statistics.mean(lengths) or 1
        variation = statistics.pstdev(lengths) / mean
        if variation < 0.35:
            score += 15

    # 2. Stock AI phrases
    hits = sum(1 for p in STOCK_PHRASES if p in lower)
    score += min(hits * 10, 30)

    # 3. Em dashes are common in AI text
    if "\u2014" in text:
        score += 8

    # 4. Repetitive vocabulary
    if len(set(words)) / len(words) < 0.5:
        score += 8

    # 5. Casual / human markers reduce the score
    if re.search(CASUAL_MARKERS, lower):
        score -= 15
    if text.strip() and text.strip()[0].islower():
        score -= 8

    return clamp(score)


def ask_gemini(text=None, image_bytes=None, mime_type=None):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=api_key)

    parts = []
    if image_bytes:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    if text:
        parts.append(f"Text to analyze:\n{text}")
    parts.append(PROMPT)

    response = client.models.generate_content(
        model=MODEL,
        contents=parts,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    data = json.loads(response.text)
    return {
        "ai_likelihood": clamp(data.get("ai_likelihood")),
        "confidence": clamp(data.get("confidence")),
        "reasoning": str(data.get("reasoning", "")),
        "extracted_text": str(data.get("extracted_text", "")),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    text = (request.form.get("text") or "").strip()
    file = request.files.get("image")

    image_bytes, mime_type = None, None
    if file and file.filename:
        mime_type = file.mimetype
        if mime_type not in ALLOWED_MIME:
            return jsonify(error="Please upload a PNG, JPEG or WEBP image."), 400
        image_bytes = file.read()

    if not text and not image_bytes:
        return jsonify(error="Paste some text or upload a screenshot."), 400

    try:
        gemini = ask_gemini(text or None, image_bytes, mime_type)
    except json.JSONDecodeError:
        return jsonify(error="The model returned an invalid response. Try again."), 502
    except Exception as e:
        return jsonify(error=f"Gemini error: {e}"), 500

    # Heuristics run on the pasted text, or on text Gemini read from the image
    analysed_text = text or gemini["extracted_text"]
    heuristic = heuristic_score(analysed_text)

    if heuristic is None:
        final = gemini["ai_likelihood"]
    else:
        final = round(0.7 * gemini["ai_likelihood"] + 0.3 * heuristic, 1)

    return jsonify(
        final_score=final,
        confidence=gemini["confidence"],
        reasoning=gemini["reasoning"],
        gemini_score=gemini["ai_likelihood"],
        heuristic_score=heuristic,
    )


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="Image is too large (max 5 MB)."), 413


if __name__ == "__main__":
    app.run(debug=True)
