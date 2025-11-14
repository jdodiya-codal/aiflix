import os
import google.generativeai as genai

# Load API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini once at import time
genai.configure(api_key=GEMINI_API_KEY)


def get_gemini_response(prompt: str) -> str:
    """
    Sends a text prompt to Google Gemini and returns the model's response.
    """

    try:
        # Use a valid Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Generate text
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        return f"Error: {str(e)}"
