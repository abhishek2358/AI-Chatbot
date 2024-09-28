import google.generativeai as genai
import os
from dotenv import load_dotenv
from aichat.models import patient

# Load the environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")

def summarize_conversation(conversation):
    llm_prompt = f"""
    Please summarize the following conversation while retaining all important details:
    
    {conversation}
    
    The summary should be concise and cover all key points.
    """
    
    response = model.generate_content(llm_prompt)  
    summary = response.text.strip()
    print(summary)
    return summary

def conversation_history(conversation_memory, user_input, bot_response,summarized_memory):

    # Check if the conversation memory is too long
    if len(conversation_memory) > 5:  # Example: summarize after 5 exchanges
        summarized_memory += summarize_conversation("\n".join(conversation_memory))
        conversation_memory = []  # Clear the memory after summarizing
        # use patient record of patient_id 1. and save patient_summary in that
        patient_record = patient.objects.get(patient_id=1)
        patient_record.patient_summary = summarized_memory
        patient_record.save()
    print(len(conversation_memory),"conversation_memory")
    # Append the user input and bot response to the conversation memory
    conversation_memory.append(f"User: {user_input}")
    conversation_memory.append(f"AI Bot: {bot_response}")
    
    return conversation_memory