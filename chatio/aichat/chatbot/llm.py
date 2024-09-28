from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Load the environment variables
load_dotenv()
api_key = os.getenv('API_KEY')
model_name = os.getenv('MODEL_NAME')



class GeminiChat():
    def __init__(self, key, model_name):
        from google.generativeai import client,GenerativeModel
        
        self.api_key = key
        self.model_name = model_name
        genai.configure(api_key=key)
        self.model = GenerativeModel(model_name=self.model_name)
        
        
    def generate_content(self,prompt):
        from google.generativeai.types import content_types
        
        try:
            response = self.model.generate_content(prompt)
            return response
        except Exception as e:
            return "**ERROR**: " + str(e), 0

class OpenAIChat():
    
        def __init__(self, key, model_name):
            self.api_key = key
            self.model_name = model_name
            self.model = OpenAI(self.api_key)
            
        def generate_content(self,prompt):
            try:
                response = openai.Completion.create(
                engine=self.model_name,  # Specify the model to use (you can change this based on your subscription)
                prompt=prompt,
                max_tokens=10,
                temperature=0
            )
                return response
            except Exception as e:
                return "**ERROR**: " + str(e), 0

def get_llm():
    if model_name is None:
        raise ValueError("Model name is not set")
    
    if model_name == "gemini-pro":
        return GeminiChat(api_key, model_name)
    elif model_name == "davinci":
        return OpenAIChat(api_key, model_name)