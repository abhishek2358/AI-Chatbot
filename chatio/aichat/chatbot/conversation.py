import google.generativeai as genai
import os
from dotenv import load_dotenv
from aichat.models import patient
from aichat.chatbot.llm import get_llm


model = get_llm()

def summarize_conversation(conversation):
    llm_prompt = f"""
    Please summarize the following conversation while retaining all important details:
    
    {conversation}
    
    The summary should be concise and cover all key points.
    """
    
    response = model.generate_content(llm_prompt)  
    summary = response.text.strip()
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
    # Append the user input and bot response to the conversation memory
    conversation_memory.append(f"User: {user_input}")
    conversation_memory.append(f"AI Bot: {bot_response}")
    
    return conversation_memory

def extract_entities_with_llm(conversation, model="gpt-3.5-turbo"):
    llm_prompt = f"""
    Extract the key entities from the following conversation in JSON format. 
    Identify medication, frequency, appointment time, and other relevant information.
    
    Conversation: "{conversation}"
    
    Provide the output in the following format:
    {{
        "medication": "medication name",
        "frequency": "frequency",
        "appointment_time": "appointment time"
    }}
    """
    
    response = model.generate_content(llm_prompt)
    
    return response.choices[0].message["content"]
