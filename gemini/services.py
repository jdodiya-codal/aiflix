# import google.generativeai as genai
from django.conf import settings

from google import genai

# Configure Gemini with your API key
# genai.configure(api_key=settings.GEMINI_API_KEY)



def get_gemini_response(prompt: str) -> str:
    """
    Sends a text prompt to Google Gemini and returns the model's response.
    """
    try:
        # Choose a Gemini model (you can use gemini-pro or gemini-1.5-pro etc.)
        # model = genai.GenerativeModel("gemini-pro")
        # model = genai.GenerativeModel("models/gemini-1.5-flash")
        # Generate content
        # response = model.generate_content(prompt)

        client = genai.Client(api_key="AIzaSyAj381m2GU7s4S_A3AZc2QV3pPh94_r3Rw")

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents={prompt}
        )

        # Return text response
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"
