import google.generativeai as genai
import os

# API բանալիով մոդելը ակտիվացնել
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text
