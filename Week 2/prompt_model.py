import os
import sys
from dotenv import load_dotenv
import ollama
from google import genai

# Load environment variables from .env
load_dotenv()

# Gemini model list
GEMINI_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
}


# ----------------------------
# CHECK MODEL TYPE
# ----------------------------
def is_gemini(model: str) -> bool:
    return model in GEMINI_MODELS


# ----------------------------
# GEMINI CALL
# ----------------------------
def call_gemini(model: str, prompt: str) -> str:
    try:
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return "[Gemini Error] Missing GOOGLE_API_KEY in environment"

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text or "[Gemini Error] Empty response"

    except Exception as e:
        return f"[Gemini Error] {e}"


# ----------------------------
# OLLAMA CALL
# ----------------------------
def call_ollama(model: str, prompt: str) -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        return response["message"]["content"]

    except Exception as e:
        return f"[Ollama Error] {e}"


# ----------------------------
# MAIN ROUTER FUNCTION
# ----------------------------
def prompt_model(model: str, prompt: str) -> str:
    try:
        if is_gemini(model):
            return call_gemini(model, prompt)

        return call_ollama(model, prompt)

    except Exception as e:
        return f"[Fatal Error] {e}"


# ----------------------------
# CLI ENTRY POINT
# ----------------------------
def main():
    if len(sys.argv) < 3:
        print("Usage: uv run prompt_model.py <model> <prompt>")
        return

    model = sys.argv[1]
    prompt = " ".join(sys.argv[2:])

    result = prompt_model(model, prompt)

    print("\n--- RESPONSE ---\n")
    print(result)


if __name__ == "__main__":
    main()
